import os
import io
import requests
from PIL import Image
from flask import current_app
from .. import redis_client
from .. import db

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

def get_image(upload_id):
    storage_host = current_app.config['STORAGE_HOST']
    storage_port = current_app.config['STORAGE_PORT']
    broker = DockerBroker(storage_host, storage_port)
    return Image.open(io.BytesIO(broker.download('upload', upload_id)))

def crop_image(image, left, upper, right, lower):
    left = image.size[0] * left
    upper = image.size[1] * upper
    right = image.size[0] * right
    lower = image.size[1] * lower
    return image.crop((left, upper, right, lower))

def get_curator(project, session):
    return Curator(project, session)

def get_class_names(project):
    cache_name = '%s_class_names' % project
    if not redis_client.exists(cache_name):
        result = db.session.execute("SELECT class_name FROM class_names WHERE project = '%s'" % project)
        class_names = [r[0] for r in result]
        redis_client.zadd(cache_name, {name: 1 for name in class_names})
    else:
        class_names = [name.decode('utf-8') 
                       for name in redis_client.zrange(cache_name, 0, -1)]
    return class_names
        
            
def update_record(stream_name, stream_id, upload_id, detection_id, selection):
    if selection != '_skip':
        sql = '''
        UPDATE classifications
        SET class_name = '%s', validated = true
        WHERE upload_id = '%s' AND detection_id = '%s'
        ''' % (selection, upload_id, detection_id)
        db.session.execute(sql)
        db.session.commit()
    redis_client.xack(stream_name, 'validation_workers', stream_id)