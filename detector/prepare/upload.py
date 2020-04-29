import argparse
import os
import psycopg2
import datetime
import json
from broker import BlobBroker


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', help='path of detection output',
                        type=str, required=True)
    args, unknown_args = parser.parse_known_args()
    
    # connect to the database
    conn = psycopg2.connect('host=%s dbname=postgres user=ackbar@ackbar-postgres password=%s'
                            % (os.environ['AML_PARAMETER_POSTGRES_HOSTNAME'],
                               os.environ['AML_PARAMETER_POSTGRES_PASSWORD']))

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
    
    # grab the meta data required to post detections
    sql = """
    SELECT project, upload_id, observation_time FROM uploads
    WHERE observation_time > '%s'
    """ % latest_date
    cursor = conn.cursor()
    cursor.execute(sql)
    broker = BlobBroker()
    observation_times = {}
    for result in cursor:
        project, upload_id, observation_time = result
        observation_times[(project, upload_id)] = observation_time
        
    # now we load in the detections and create the rows
    # to push back
    detection_rows = []
    for file_path in os.listdir(args.input_path):
        with open('/'.join([args.input_path, file_path]), 'r') as fh:
            detection_rows.extend(json.load(fh))
    upload_rows = []
    print(list(observation_times.keys()))
    for project, upload_id, k, y0, y1, x0, x1 in detection_rows:
        observation_time = observation_times[(project, upload_id)]
        upload_rows.append((
            project, upload_id, observation_time, k, y0, y1, x0, x1
        ))
        
    # finally we upload all the new records
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO detections VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
         upload_rows
    )
    conn.commit()
    print(cursor.rowcount, ' records committed')
    cursor.close()
        
