import os
import argparse
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from azureml.core.model import Model


def init():
    global detection_model, output_path
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', required=True, type=str)
    args, unknown_args = parser.parse_known_args()
    
    output_path = os.environ['AZUREML_BI_OUTPUT_PATH']
    
    model_path = Model.get_model_path(args.model_name)
    detection_model = tf.saved_model.load(model_path).signatures['default']


def break_path(file_path):
    file_name = file_path.split('/')[-1].split('.')[0]
    return file_name.split('_')


def load_image(file_path):
    image = Image.open(file_path)
    image.convert('RGB')
    image.resize((1494, 2048))
    return image


def run(mini_batch):
    records = []
    file_paths = list(mini_batch)
    identifiers = [break_path(file_path) for file_path in file_paths]
    images = [load_image(file_path) for file_path in file_paths]
    images = [np.asarray(image, np.float32) for image in images]
    input_tensor = tf.convert_to_tensor(np.array(images))
    detections = detection_model(input_tensor)
    scores = detections['detection_scores'].numpy()
    labels = detections['detection_classes'].numpy()
    bboxes = detections['detection_boxes'].numpy()
    for j, (project, upload_id) in enumerate(identifiers):
        for k, (score, label) in enumerate(zip(scores[j], labels[j])):
            if score >= 0.9 and label == 1.:
                y1, x0, y0, x1 = [float(e) for e in bboxes[j][k]]
                records.append((
                    project, upload_id, observation_time, k, y0, y1, x0, x1
                ))
    output_name = '%s/%s.json' % (output_path, hash(identifiers))
    with open(output_name, 'w') as fh:
        json.dump(records, output_name)
        