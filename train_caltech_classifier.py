import tensorflow as tf
import numpy as np
import os
import argparse
import pickle
import time
import json


CLASS_NAMES = np.array(['badger', 'bird', 'bobcat', 'car', 'cat', 'coyote', 'deer', 'dog', 
						'fox', 'insect', 'lizard', 'mountain_lion', 'opossum', 'rabbit',
						'raccoon', 'rodent', 'skunk', 'squirrel',
					   ])
IMG_HEIGHT = 160
IMG_WIDTH = 160
AUTOTUNE = tf.data.experimental.AUTOTUNE
BATCH_SIZE = 32
SHUFFLE_BUFFER_SIZE = 1000
LEARNING_RATE = 0.0001
TRAINING_EPOCHS = 10


def process_path(file_path):
	parts = tf.strings.split(file_path, os.path.sep)
	label = parts[-2] == CLASS_NAMES
	img = tf.io.read_file(file_path)
	img = tf.image.decode_jpeg(img, channels=3)
	img = tf.image.convert_image_dtype(img, tf.float32)
	img = tf.image.resize(img, [IMG_WIDTH, IMG_HEIGHT])
	return img, label


def build_dataset(file_pattern):
	ds = tf.data.Dataset.list_files(file_pattern)
	ds = ds.map(process_path, num_parallel_calls=AUTOTUNE)
	ds = ds.shuffle(buffer_size=SHUFFLE_BUFFER_SIZE)
	ds = ds.batch(BATCH_SIZE)
	ds = ds.prefetch(buffer_size=AUTOTUNE)
	return ds


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--layers', help='number of layers to tune',
                        type=int, default=0)
	parser.add_argument('--epochs', help='number of epochs to train',
                        type=int, default=10)
	parser.add_argument('--rate', help='learning rate',
                        type=float, default=0.0001)
	args = parser.parse_args()
    
	run_id = int(time.time())
    
	train = build_dataset('train/*/*.jpg')
	test = build_dataset('test/*/*.jpg')
	IMG_SHAPE = (160, 160, 3)
	base_model = tf.keras.applications.inception_v3.InceptionV3(input_shape=IMG_SHAPE,
													include_top=False,
													weights='imagenet')
	base_model.summary()
	base_model.trainable = True
	for layer in base_model.layers[:len(base_model.layers) - args.layers]:
		layer.trainable = False
	model = tf.keras.models.Sequential([
		base_model,
		tf.keras.layers.GlobalAveragePooling2D(),
		tf.keras.layers.Dense(CLASS_NAMES.shape[0]),
		tf.keras.layers.Activation('softmax'),
	])
	model.compile(
		optimizer=tf.keras.optimizers.RMSprop(lr=args.rate),
		loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
		metrics=['accuracy']
	)
	model.summary()
	history = model.fit(train,
						epochs=args.epochs,
						validation_data=train)

	with open('config_%s.json' % run_id, 'w') as fh:
		json.dump({
            'layers': args.layers,
            'epochs': args.epochs,
            'rate': args.rate,
            'history': {
                k: [float(e) for e in v]
                for k, v in history.history.items()
            },
        }, fh)
    
	if not os.path.exists('classifier'):
		os.mkdir('classifier')
	tf.saved_model.save(model, 'classifier/')

