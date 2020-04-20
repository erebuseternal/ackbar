import azureml.core
from azureml.core import Workspace, PipelineData, Datastore
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline
from azureml.core import Experiment

ws = Workspace.from_config()

def_blob_store = Datastore(ws, 'workspaceblobstore')
output_data = PipelineData('output_data',
                            datastore=def_blob_store,
                            output_name='output_data')

compute_target = ws.compute_targets['cpu_cluster']

prepare_step = PythonScriptStep(
    script_name='prepare.py',
    arguments=['--output', output_data],
    inputs=[],
    outputs=output_data,
    compute_target=compute_target,
    source_directory='prepare',
)

pipeline_steps = [prepare_step]

pipeline = Pipeline(workspace=ws, steps=pipeline_steps)

pipeline_run = Experiment(ws, 'test_prepare').submit(pipeline)
pipeline_run.wait_for_completion()
