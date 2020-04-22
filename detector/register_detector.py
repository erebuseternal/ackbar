from azureml.core.model import Model
from azureml.core import Workspace

ws = Workspace.from_config()

model = Model.register(
    model_path='./mega_detector_v3',
    model_name='mega_detector_v3',
    description='detector model for ackbar, first upload',
    workspace=ws,
)