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
    parser.add_argument('--project', help='project for job',
                        type=str, required=True)
    args, unknown_args = parser.parse_known_args()
    
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
    
    # grab the meta data required to post classifications
    sql = """
    SELECT upload_id, detection_id, observation_time
    FROM detections
    WHERE observation_time > '%s'
    AND project = '%s'
    """ % (latest_date, project)
    cursor = conn.cursor()
    cursor.execute(sql)
    broker = BlobBroker()
    observation_times = {}
    for result in cursor:
        upload_id, detection_id, observation_time = result
        observation_times[(upload_id, detection_id)] = observation_time
        
    # pull down class names
    sql = """
    SELECT class_name from class_names
    WHERE project = '%s'
    """ % project
    cursor = conn.cursor()
    cursor.execute(sql)
    class_names = sorted([result[0] for result in cursor])
        
    # now we load in the detections and create the rows
    # to push back
    data_keys = [
        'class_predictions',
        'class_confidences',
        'identifiers',
    ]
    classification_data = {
        k: list() for key in data_keys
    }
    for file_path in os.listdir(args.input_path):
        with open('/'.join([args.input_path, file_path]), 'r') as fh:
            data_partition = json.load(fh)
            for key in data_keys:
                classification_data[key].extend(data_partition[key])
    upload_rows = []
    print(list(observation_times.keys()))
    zipped_data = zip(
        classification_data['class_predictions'],
        classification_data['class_confidences'],
        classification_data['identifiers']
    )
    for predictions, confidences, (project, upload_id, detection_id) in zipped_data:
        predictions = [class_names[p] for p in predictions]
        observation_time = observation_times[(upload_id, detection_id)]
        record = [project, upload_id, observation_time, detection_id, predictions[0], False] + predictions
        upload_rows.append(record)
        
    # finally we upload all the new records
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO classifications VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
         upload_rows
    )
    conn.commit()
    print(cursor.rowcount, ' records committed')
    cursor.close()
