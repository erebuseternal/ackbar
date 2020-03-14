from flask import Flask, request, send_file
import os
app = Flask(__name__)


BASE_DIR = '/root/local_storage'


def make_bucket(bucket):
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    file_dir = '/'.join([BASE_DIR, bucket])
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)


@app.route('/pull')
def pull():
    bucket = request.args.get('bucket')
    key = request.args.get('key')
    if bucket is None:
        return 'Bucket Must Be Specified', 404
    if key is None:
        return 'Key Must Be Specified', 404
    file_path = '/'.join([BASE_DIR, bucket, key])
    if not os.path.exists(file_path):
        return 'File Not Found', 404
    return send_file(file_path)


@app.route('/push', methods=['POST'])
def push():
    bucket = request.args.get('bucket')
    key = request.args.get('key')
    if bucket is None:
        return 'Bucket Must Be Specified', 404
    if key is None:
        return 'Key Must Be Specified', 404
    make_bucket(bucket)
    file_path = '/'.join([BASE_DIR, bucket, key])
    print(request.files)
    if 'upload' not in request.files:
        return 'File Should Be Under "upload"', 404
    file = request.files['upload']
    file.save(file_path)
    return 'Upload Complete', 202
        