import argparse
import psycopg2
import json
import os


class LocalBroker(object):
    def __init__(self, directory='root/local_storage'):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
            
    def upload(self, data, identifier, case):
        directory = '/'.join(self.directory, case)
        if not os.path.exists(directory):
            os.mkdir(directory)
        with open('/'.join([directory, str(identifier) + '.jpg']), 'wb') as fh:
            fh.write(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--meta', '-m', help='path to meta data',
                        type=str)
    parser.add_argument('--host', '-h', help='hostname of postgres db',
                        type=str)
    parser.add_argument('--password', '-p', help='password for postgres db',
                        type=str)
    args = parser.parse_arguments()
    if args.meta is None:
        parser.error('please specify --meta')
    if args.host is None:
        parser.error('please specify --host')
    if args.password is None:
        parser.error('please specify --password')
        
    # create connection to db
    conn = psycopg2.connect('host=%s dbname=postgres user=postgres password=%s' %
                            (args.host, args.password))
    with open(args.meta, 'r') as fh:
        meta_data = json.load(fh)
    cursor = conn.cursor()
    broker = LocalBroker()
    for data in meta_data:
        upload_id = data['upload_id']
        image_path = data['image_path']
        observation_time = data['observation_time']
        with open(image_path, 'rb') as fh:
            broker.upload(fh.read(), upload_id, 'upload')
        cursor.execute(
            'INSERT INTO uploads VALUES (%s, %s)',
            (upload_id, observation_time)
        )
        
        