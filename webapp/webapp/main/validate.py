import os
from PIL import Image
from flask import current_app

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

class Curator(object):
    def __init__(self, project, session):
        self.session = session
        self.project = project
        self.upload_ids = sorted(
            [path.split('.')[0] for path in os.listdir('webapp/main/images')
             if path.endswith('jpg')]
        )
    
    def pull(self, session, upload_id, detection_id):
        i = next(j for j in range(len(self.upload_ids))
                  if self.upload_ids[j] == upload_id)
        before = (self.upload_ids[i - 1], 0) if i > 0 else (None, None)
        after = (self.upload_ids[i + 1], 0) if i < len(self.upload_ids) - 1 else (None, None)
        top = ['Dog', 'Cat', 'Elephant']
        other = ['Horse', 'Crab', 'Frog']
        bbox = {
            'y1': 0.25,
            'y0': 0.75,
            'x0': 0.25,
            'x1': 0.75
        }
        return after, before, top, other, bbox
    
    def first(self, session):
        return self.upload_ids[0], 0
            
def update_record(upload_id, detection_id, selection):
    pass