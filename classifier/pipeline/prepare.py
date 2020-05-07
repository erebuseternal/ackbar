import argparse
import os
import io
import psycopg2
import datetime
from broker import BlobBroker
from PIL import Image


def crop_image(image, left, upper, right, lower):
    left = image.size[0] * left
    upper = image.size[1] * upper
    right = image.size[0] * right
    lower = image.size[1] * lower
    return image.crop((left, upper, right, lower))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_path', help='path to write images to',
                        type=str, required=True)
    parser.add_argument('--project', help='project for job',
                        type=str, required=True)
    args = parser.parse_args()
    
    # ensure output directory exists
    os.makedirs(args.output_path, exist_ok=True)
    print(args.output_path)
    
    # connect to the database
    conn = psycopg2.connect('host=%s dbname=postgres user=ackbar@ackbar-postgres password=%s'
                            % (os.environ['AML_PARAMETER_POSTGRES_HOSTNAME'],
                               os.environ['AML_PARAMETER_POSTGRES_PASSWORD']))

    # get the latest timestamp to produce classifications
    sql = """
    SELECT observation_time FROM classifications 
    WHERE project = '%s'
    ORDER BY observation_time DESC LIMIT 1;
    """ % args.project
    cursor = conn.cursor()
    cursor.execute(sql)
    try:
        result = next(cursor)
        latest_date = result[0]
    except StopIteration:
        latest_date = datetime.datetime(1970, 1, 1)
    print(latest_date)
    
    sql = """
    SELECT upload_id, detection_id, y0, y1, x0, x1 
    FROM detections
    WHERE observation_time > '%s'
    AND project = '%s'
    """ % (latest_date, args.project)
    cursor = conn.cursor()
    cursor.execute(sql)
    broker = BlobBroker()
    for result in cursor:
        upload_id, detection_id, y0, y1, x0, x1 = result
        image = Image.open(io.BytesIO(broker.download(args.project, upload_id)))
        image = crop_image(image, x0, y1, x1, y0)
        file_path = '/'.join([
            args.output_path,
            '%s_%s_%s.jpg' % (args.project, upload_id, detection_id)
        ])
        image.save(file_path)
