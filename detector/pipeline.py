import os
import azureml.core
from azureml.core import Workspace, Datastore
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core import Experiment, Environment, ScriptRunConfig, RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies

ws = Workspace.from_config()

def_blob_store = Datastore(ws, 'workspaceblobstore')
output_data = PipelineData('output_data',
                            datastore=def_blob_store,
                            output_name='output_data',
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
env.python.conda_dependencies = conda
run_config = RunConfiguration()
run_config.environment = env

prepare_step = PythonScriptStep(
    script_name='prepare.py',
    arguments=['--output', output_data],
    inputs=[],
    outputs=[output_data],
    compute_target=compute_target,
    source_directory='prepare',
    runconfig=run_config,
)

pipeline_steps = [prepare_step]

pipeline = Pipeline(workspace=ws, steps=pipeline_steps)

pipeline_run = Experiment(ws, 'test_prepare').submit(pipeline)
pipeline_run.wait_for_completion()
