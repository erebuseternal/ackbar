import os
import tensorflow as tf
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Workspace
from azureml.core.model import Model


IMG_SHAPE = (160, 160, 3)
TRAINABLE_LAYERS = 50
LEARNING_RATE = 0.0001


def authenticate():
    sp = ServicePrincipalAuthentication(tenant_id=os.environ['AML_TENANT_ID'],
                                        service_principal_id=os.environ['AML_PRINCIPLE_ID'],
                                        service_principal_password=os.environ['AML_PRINCIPLE_PASSWORD'])
    return sp


def get_workspace():
    ws = Workspace.get(name='ackbarMLWorkspace',
                   auth=authenticate(),
                   subscription_id='5a74635a-63a7-4b16-b5ea-933131f9d174')
    return ws


def build_new_model(project, num_classes, img_shape=IMG_SHAPE,
                    trainable_layers=TRAINABLE_LAYERS,
                    learning_rate=LEARNING_RATE):
    base_model = tf.keras.applications.inception_v3.InceptionV3(input_shape=IMG_SHAPE,
                                                    include_top=False,
                                                    weights='imagenet')
    base_model.summary()
    base_model.trainable = True
    for layer in base_model.layers[:len(base_model.layers) - trainable_layers]:
        layer.trainable = False
    model = tf.keras.models.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(num_classes),
        tf.keras.layers.Activation('softmax'),
    ])
    model.compile(
        optimizer=tf.keras.optimizers.RMSprop(lr=learning_rate),
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    model.summary()
    
    model_name = '%s_v1' % project
    if not os.path.exists(model_name):
        os.mkdir(model_name)
    tf.keras.models.save_model(model, model_name + '/')
    return model_name


def register_model(model_name, project):
    ws = get_workspace()
    model = Model.register(
        model_path=model_name,
        model_name=model_name,
        description='classifier for project %s' % project,
        workspace=ws,
    )
    