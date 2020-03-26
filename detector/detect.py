import psycopg2
import datetime
import os
import io
import requests
import pandas as pd
import tensorflow as tf
import numpy as np
from PIL import Image
from tqdm import tqdm


class DockerBroker(object):
    def __init__(self, hostname, port):
        self.base_url = 'http://%s:%s' % (hostname, port)
        
    def upload(self, fh, bucket, key):
        url = '%s/push?bucket=%s&key=%s.jpg' % (self.base_url, bucket, key)
        files = {'upload': fh}
        response = requests.post(url, files=files)
        if not str(response.status_code).startswith('2'):
            raise Exception('upload failed (%s): %s' % (url, response.status_code))
    
    def download(self, bucket, key):
        url = '%s/pull?bucket=%s&key=%s.jpg' % (self.base_url, bucket, key)
        response = requests.get(url)
        if not str(response.status_code).startswith('2'):
            raise Exception('download failed (%s): %s' % (url, response.status_code))
        return response.content


# first we get the last timestamp from the detections table
# this will let us know where we need to start from
conn = psycopg2.connect('host=%s dbname=postgres user=postgres password=%s'
                        % (os.environ['POSTGRES_HOSTNAME'],
                           os.environ['POSTGRES_PASSWORD']))
sql = """
SELECT observation_time FROM detections 
ORDER BY observation_time DESC LIMIT 1;
"""
cursor = conn.cursor()
cursor.execute(sql)
try:
    result = next(cursor)
    latest_date = result[0]
except StopIteration:
    latest_date = datetime.datetime(1970, 1, 1)

# next we can query for all of the uploads we need
# to run the detector on
sql = """
SELECT project, upload_id, observation_time FROM uploads
WHERE observation_time > '%s'
""" % latest_date
cursor.execute(sql)
projects = []
upload_ids = []
observation_times = []
for result in cursor:
    projects.append(result[0])
    upload_ids.append(result[1])
    observation_times.append(result[2])
cursor.close()

if upload_ids:
    # next we create the detections
    batch_size = int(os.environ['BATCH_SIZE'])
    broker = DockerBroker(os.environ['STORAGE_HOSTNAME'], 5000)
    detection_model = tf.saved_model.load(os.environ['MODEL_PATH']).signatures['default']
    records = []
    for i in tqdm(range(0, len(upload_ids), batch_size)):
        upload_id_batch = upload_ids[i:i+batch_size]
        observation_time_batch = observation_times[i:i+batch_size]
        project_batch = projects[i:i+batch_size]
        images = [Image.open(io.BytesIO(broker.download('upload', upload_id)))
                  for upload_id in upload_id_batch]
        images = [image.convert('RGB') for image in images]
        images = [image.resize((1494, 2048)) for image in images]
        images = [np.asarray(image, np.float32) for image in images]
        input_tensor = tf.convert_to_tensor(np.array(images))
        detections = detection_model(input_tensor)
        scores = detections['detection_scores'].numpy()
        labels = detections['detection_classes'].numpy()
        bboxes = detections['detection_boxes'].numpy()
        for j, (project, upload_id, observation_time) in enumerate(zip(project_batch, upload_id_batch, observation_time_batch)):
            for k, (score, label) in enumerate(zip(scores[j], labels[j])):
                if score >= 0.9 and label == 1.:
                    y1, x0, y0, x1 = [float(e) for e in bboxes[j][k]]
                    records.append((
                        project, upload_id, observation_time, k, y0, y1, x0, x1
                    ))

    # finally we upload all the new records
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO detections VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
         records
    )
    conn.commit()
    print(cursor.rowcount, ' records committed')
    cursor.close()
else:
    print('nothing to do')