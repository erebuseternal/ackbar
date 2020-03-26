import argparse
import psycopg2
import json
import os
import requests


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--meta', help='path to meta data',
                        type=str)
    parser.add_argument('--sql', help='hostname of postgres db',
                        type=str, default='172.17.0.2')
    parser.add_argument('--password', help='password for postgres db',
                        type=str, default='ackbar')
    parser.add_argument('--store', help='hostname of storage',
                        type=str, default='172.17.0.3')
    args = parser.parse_args()
    if args.meta is None:
        parser.error('please specify --meta')
        
    # create connection to db
    conn = psycopg2.connect('host=%s dbname=postgres user=postgres password=%s' %
                            (args.sql, args.password))
    with open(args.meta, 'r') as fh:
        meta_data = json.load(fh)
    cursor = conn.cursor()
    broker = DockerBroker(args.store, 5000)
    records = []
    for data in meta_data:
        upload_id = data['upload_id']
        image_path = data['image_path']
        observation_time = data['observation_time']
        with open(image_path, 'rb') as fh:
            broker.upload(fh, 'upload', upload_id)
        records.append(('caltech', upload_id, observation_time))
    cursor.executemany(
        "INSERT INTO uploads VALUES (%s, %s, %s)",
        records
    )
    conn.commit()
    print(cursor.rowcount, ' records committed')
        
        