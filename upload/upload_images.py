import argparse
import datetime
import os
import json
import psycopg2
from broker import BlobBroker
from tqdm import tqdm

def upload_records(conn, records):
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO uploads VALUES (%s, %s, %s)",
        records
    )
    conn.commit()
    print(cursor.rowcount, ' records committed')
    cursor.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='directory of images',
                        type=str, required=True)
    parser.add_argument('--project', help='project',
                        type=str, required=True)
    args = parser.parse_args()
    
    conn = psycopg2.connect('host=%s dbname=postgres user=ackbar@ackbar-postgres password=%s'
                            % (os.environ['POSTGRES_HOSTNAME'],
                               os.environ['POSTGRES_PASSWORD']))
    
    sql = '''
    select upload_id from uploads
    order by upload_id desc
    limit 1
    '''
    cursor = conn.cursor()
    cursor.execute(sql)
    try:
        last_id = next(cursor)[0]
    except StopIteration:
        last_id = -1
        
    if not os.path.exists('%s_tracking.json' % args.project):
        with open('%s_tracking.json' % args.project, 'w') as fh:
            json.dump([], fh)
            
    with open('%s_tracking.json' % args.project, 'r') as fh:
        all_paths = json.load(fh)
    
    time_format = '%Y-%m-%d %H:%M:%S.%f'
    broker = BlobBroker()
    records = []
    for path in tqdm(os.listdir(args.dir)):
        file_path = '/'.join((args.dir, path))
        if file_path in all_paths or not file_path.endswith('.jpg'):
            continue
        last_id += 1
        all_paths.append(path)
        with open(file_path, 'rb') as fh:
            broker.upload(fh, args.project, last_id)
        upload_time = datetime.datetime.now().strftime(time_format)
        records.append((args.project, last_id, upload_time))
        if len(records) == 100:
            upload_records(conn, records)
            records = []
            with open('%s_tracking.json' % args.project, 'w') as fh:
                json.dump(all_paths, fh)
    if records:
        upload_records(conn, records)
        records = []
        with open('%s_tracking.json' % args.project, 'w') as fh:
            json.dump(all_paths, fh)
        
        