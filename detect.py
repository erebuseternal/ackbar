import argparse
import json
import tensorflow as tf
import numpy as np
from tqdm import tqdm
from PIL import Image


def load_model(export_path):
	imported = tf.saved_model.load(export_path)
	return imported.signatures['default']


def load_image(image_path):
	image = Image.open(image_path)
	image = image.convert(mode='RGB')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--model', '-m', help='path to the saved model directory',
						default='mega_detector_v3')
	parser.add_argument('--signature', '-s', help='signature of the saved model',
						default='default')
	parser.add_argument('--input', '-i', help='path to input json file')
	parser.add_argument('--output', '-o', help='path to output directory')
	parser.add_argument('--batch', '-b', help='maximum batch size for inference',
						default=100, type=int)
	parser.add_argument('--threshold', '-t', help='threshold for detection',
						default=0.9, type=float)
	parser.add_argument('--label', '-l', help='label for animal class',
						default=1., type=float)
	args = parser.parse_args()
	if args.input is None:
		parser.error('please specify --input')
	if args.output is None:
		parser.error('please specify --output')

	with open(args.input) as fh:
		input_image_meta_data = json.load(fh)
	input_id_path_pairs = [(data['id'], data['file_name']) 
					 		for data in input_image_meta_data['images']]

	output_image_meta_data = []
	detection_model = tf.saved_model.load(args.model).signatures[args.signature]
	for i in tqdm(range(0, len(input_id_path_pairs), args.batch)):
		id_array = []
		image_array = []
		inference_array = []
		for image_id, image_path in input_id_path_pairs[i:i+args.batch]:
			id_array.append(image_id)
			image = Image.open(image_path).convert(mode='RGB')
			image_array.append(image)
			inference_array.append(np.asarray(image, np.float32))
		inference_tensor = tf.convert_to_tensor(np.array(inference_array))
		detections = detection_model(inference_tensor)
		scores = detections['detection_scores'].numpy()
		labels = detections['detection_classes'].numpy()
		bboxes = detections['detection_boxes'].numpy()
		for j, (origin_id, image) in enumerate(zip(id_array, image_array)):
			for k, (score, label) in enumerate(zip(scores[j], labels[j])):
				if score >= args.threshold and label == args.label:
					upper, left, lower, right = bboxes[k][j]
					left *= image.size[0]
					upper *= image.size[1]
					right *= image.size[0]
					lower *= image.size[1]
					cropped_image = image.crop((left, upper, right, lower))
					image_id = '%s_%s' % (origin_id, k)
					image_path = '/'.join([args.output, image_id + '.jpg'])
					output_image_meta_data.append({
						'origin_id': origin_id,
						'id': image_id,
						'file_name': image_path,
					})
					cropped_image.save(image_path)
	output_path = '/'.join([args.output, 'metadata.json'])
	with open(output_path, 'w') as fh:
        output_image_meta_data = {'images': output_image_meta_data}
		json.dump(output_image_meta_data, fh)



