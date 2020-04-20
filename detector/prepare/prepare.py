import argparse
import os
import psycopg2
import datetime
from broker import BlobBroker


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_path', help='path to write images to',
                        type=str, required=True)
    args = parser.parse_args()
    
    # ensure output directory exists
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    
    # connect to the database
    conn = psycopg2.connect('host=%s dbname=postgres user=ackbar@ackbar-postgres password=%s'
                            % (os.environ['POSTGRES_HOSTNAME'],
                               os.environ['POSTGRES_PASSWORD']))

    # get the latest timestamp to produce detections
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
    
    sql = """
    SELECT project, upload_id FROM uploads
    WHERE observation_time > '%s'
    """ % latest_date
    cursor = conn.cursor()
    cursor.execute()
    broker = BlobBroker()
    for result in cursor:
        project, upload_id = result
        file_path = '/'.join([
            os.path.dirname(args.output_path),
            '%s_%s.jpg' % (project, upload_id)
        ])
        content = broker.download(project, upload_id)
        with open(file_path, 'wb') as fh:
            fh.write(content)
