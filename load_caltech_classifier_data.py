import os
import json
from tqdm import tqdm
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

creatures = ['badger', 'bird', 'bobcat', 'car', 'cat', 'coyote', 'deer', 'dog', 
		  	 'fox', 'insect', 'lizard', 'mountain_lion', 'opossum', 'rabbit',
		  	 'raccoon', 'rodent', 'skunk', 'squirrel',
		  	]
labels = {
	creatures[i]: i for i in range(len(creatures))
}

con_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
container = 'async-api'
client = BlobServiceClient.from_connection_string(con_str)

for case in ['test', 'train']:
	print('DOWNLOADING ' + case.upper())
	if not os.path.exists(case):
		os.mkdir(case)
	meta_data = {
		'annotations': [],
		'images': [],
		'categories': [{
			'id': label,
			'name': creature,
		} for creature, label in labels.items()],
	}
	blob_client = client.get_blob_client(container=container, blob=('caltech_%s_images.json' % case))
	image_paths = json.loads(blob_client.download_blob().readall())
	for image_path in tqdm(image_paths):
		blob_client = client.get_blob_client(container=container, blob=image_path)
		image_id = image_path.split('/')[-1].split('.')[0]
		file_path = '/'.join([case] + image_path.split('/')[-2:])
		directory = '/'.join(file_path.split('/')[:-1])
		if not os.path.exists(directory):
			os.mkdir(directory)
		with open(file_path, 'wb') as fh:
			fh.write(blob_client.download_blob().readall())
		creature = image_path.split('/')[-2]
		label = labels[creature]
		meta_data['annotations'].append({
			'image_id': image_id,
			'category_id': label,
		})
		meta_data['images'].append({
			'id': image_id,
			'file_name': file_path,
		})
	with open(case + '.json', 'w') as fh:
		json.dump(meta_data, fh)

