from PIL import Image

def get_image(upload_id):
    return Image.open('images/%s.jpg')

def crop_image(image, left, upper, right, lower):
    return image.crop((left, upper, right, lower))

def create_curator(project, session):
    return Curator(project, session)

class Curator(object):
    def __init__(self, project, session):
        self.session = session
        self.project = project
        self.upload_ids = sorted(
            [path.split('.')[0] for path in os.path.listdir('images')
             if path.endswith('jpg')]
        )
    
    def pull(self, session, upload_id, detection_id):
        i = next([j for j in range(len(self.upload_ids))
                  if self.upload_ids[j] == upload_id])
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
            
def update_record(upload_id, detection_id, selection):
    pass