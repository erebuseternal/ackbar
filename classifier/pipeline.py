import os
import azureml.core
from azureml.core import Workspace, Datastore
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core import Experiment, Environment, ScriptRunConfig, RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.contrib.pipeline.steps import ParallelRunConfig, ParallelRunStep
from azureml.core.runconfig import DEFAULT_GPU_IMAGE

ws = Workspace.from_config()

def_blob_store = Datastore(ws, 'workspaceblobstore')
output_data = PipelineData('output_data',
                            datastore=def_blob_store,
                            output_name='output_data',
                            is_directory=True)
batch_input = output_data.as_dataset()

classification_data = PipelineData('classification_data',
                            datastore=def_blob_store,
                            output_name='classification_data',
                            is_directory=True)

compute_target = ws.compute_targets['cpu-cluster']

environment_variables = {
    'POSTGRES_PASSWORD': os.environ['POSTGRES_PASSWORD'],
    'POSTGRES_HOSTNAME': 'ackbar-postgres.postgres.database.azure.com',
    'AZURE_STORAGE_CONNECTION_STRING': os.environ['AZURE_STORAGE_CONNECTION_STRING']
}
env = Environment(name='env', environment_variables=environment_variables)
conda = CondaDependencies()
conda.add_conda_package('psycopg2')
conda.add_conda_package('numpy')
conda.add_conda_package('Pillow')
# have to use pip to install azure packages...
conda.add_pip_package('azure-storage-blob')
env.python.conda_dependencies = conda
run_config = RunConfiguration()
run_config.environment = env

PROJECT = 'caltech'

prepare_step = PythonScriptStep(
    script_name='prepare.py',
    arguments=['--output', batch_input, '--project', PROJECT],
    inputs=[],
    outputs=[batch_input],
    compute_target=compute_target,
    source_directory='pipeline',
    runconfig=run_config,
    params=environment_variables,
)

upload_step = PythonScriptStep(
    script_name='upload.py',
    arguments=['--input', classification_data, '--project', PROJECT],
    inputs=[classification_data],
    outputs=[],
    compute_target=compute_target,
    source_directory='pipeline',
    runconfig=run_config,
    params=environment_variables,
)


env = Environment(name='env', environment_variables=environment_variables)
conda = CondaDependencies()
conda.add_conda_package('numpy')
conda.add_conda_package('Pillow')
conda.add_pip_package('tensorflow==2.1.0')
# have to use pip to install azure packages...
conda.add_pip_package('azureml-sdk')
env.python.conda_dependencies = conda
env.docker.base_image = DEFAULT_GPU_IMAGE

compute_target = ws.compute_targets['gpu-cluster']
parallel_run_config = ParallelRunConfig(
    environment=env,
    entry_script="classify.py",
    source_directory="pipeline",
    mini_batch_size="10",
    compute_target=compute_target,
    process_count_per_node=1,
    run_invocation_timeout=300,
    node_count=1,
    error_threshold=1,
    output_action="summary_only",
)


classify_step = ParallelRunStep(
    name='classify',
    inputs=[batch_input],
    output=classification_data,
    arguments=["--model_name", "%s_v1" % PROJECT,
               '--output', classification_data],
    parallel_run_config=parallel_run_config,
    allow_reuse=False
)

pipeline_steps = [prepare_step, classify_step, upload_step]

pipeline = Pipeline(workspace=ws, steps=pipeline_steps)

pipeline_run = Experiment(ws, 'test_prepare_classify_upload').submit(pipeline)