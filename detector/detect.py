import psycopg2
import datetime
import os
import io
import pandas as pd


class LocalBroker(object):
    def __init__(self, directory='/root/local_storage'):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
            
    def upload(self, data, identifier, case):
        directory = '/'.join([self.directory, case])
        if not os.path.exists(directory):
            os.mkdir(directory)
        with open('/'.join([directory, str(identifier) + '.jpg']), 'wb') as fh:
            fh.write(data)
            
    def download(self, identifier, case):
        directory = '/'.join([self.directory, case])
        with open('/'.join([directory, str(identifier) + '.jpg']), 'rb') as fh:
            content = fh.read()
        return content


# first we get the last timestamp from the detections table
# this will let us know where we need to start from
conn = psycopg2.connect('host=%s dbname=postgres user=postgres password=%s'
                        % (os.environ['POSTGRES_HOST_NAME'],
                           os.environ['POSTGRES_PASSWORD']))
sql = """
SELECT observation_time FROM detections 
ORDER BY observation_time DESC LIMIT 1;
"""
cursor = conn.cursor(sql)
cursor.execute()
try:
    result = next(cursor)
    latest_date = result[0]
except StopIteration:
    latest_date = datetime.datetime(1970, 1, 1)

# next we can query for all of the uploads we need
# to run the detector on
sql = """
SELECT upload_id FROM uploads
WHERE observation_time > '%s'
""" % latest_date
cursor.execute(sql)
upload_ids = []
observation_times = []
for result in cursor:
    upload_ids.append(result[0])
    observation_times.append(result[1])
cursor.close()

# next we create the detections
batch_size = os.environ['BATCH_SIZE']
broker = LocalBroker()
detection_model = tf.saved_model.load(os.environ['MODEL_PATH']).signatures['default']
for i in range(0, len(upload_ids), batch_size):
    upload_id_batch = upload_ids[i:i+batch_size]
    observation_time_batch = observation_times[i:i+batch_size]
    images = [Image.open(io.BytesIO(broker.download(upload_id, 'upload')))
              for upload_id in upload_id_batch]
    images = [image.convert('RGB') for image in images]
    images = [np.asarray(image, np.float32) for image in images]
    input_tensor = tf.convert_to_tensor(np.array(images))
    detections = detection_model(inference_tensor)
    scores = detections['detection_scores'].numpy()
    labels = detections['detection_classes'].numpy()
    bboxes = detections['detection_boxes'].numpy()
    for j, (upload_id, observation_time) in enumerate(zip(upload_id_batch, observation_time_batch)):
        for k, (score, label) in enumerate(zip(scores[j], labels[j])):
            if score >= 0.9 and label == 1.:
                y1, x0, y0, x1 = bboxes[k][j]
                records.append((
                    upload_id, observation_time, k, y0, y1, x0, x1
                ))

# finally we upload all the new records
cursor = conn.cursor()
cursor.executemany(
    "INSERT INTO detections VALUES (%s, %s, %s, %s, %s, %s, %s)",
     records
)
conn.commit()
print(cursor.rowcount, ' records committed')
cursor.close()