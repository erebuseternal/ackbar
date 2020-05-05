import os
import argparse
import json
import tensorflow as tf
import numpy as np
from PIL import Image
from azureml.core.model import Model
from azureml.core import Workspace


IMG_SIZE = (160, 160)


def __init__():
    global classification_model, output_path
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', help='name of the model to use',
                        type=str, required=True)
    args, unknown_args = parser.parse_known_args()
    
    output_path = os.environ['AZUREML_BI_OUTPUT_PATH']
    
    model_path = Model.get_model_path(args.model_name)
    classification_model = tf.keras.models.load_model(model_path)
    
    
def load_image(file_path):
    img = tf.io.read_file(file_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, IMG_SIZE)
    return img


def run(minibatch):
    file_paths = tuple(minibatch)
    images = [load_image(file_path) for file_path in file_paths]
    input_tensor = tf.convert_to_tensor(images)
    predictions = classification_model.predict(input_tensor)
    class_predictions = [[int(e) for e in np.argsort(-array)[:5]] for array in predictions]
    class_confidences = [[float(predictions[i][j]) for j in preds]
                         for i, preds in enumerate(class_predictions)]
    identifiers = [file_path.split('.')[0].split('_') for file_path in file_paths]
    data = {
        'class_predictions': class_predictions,
        'class_confidences': class_confidences,
        'identifiers': identifiers,
    }
    output_name = '%s/%s' % (output_path, hash(file_paths))
    with open(output_name, 'w') as fh:
        json.dump(data, fh, sort_keys=True, indent=4)
    return file_paths
    