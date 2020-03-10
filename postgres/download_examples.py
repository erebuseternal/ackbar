import argparse
import requests
import json
import os
try:
    from concurrent import futures
except ImportError:
    import futures
from tqdm import tqdm


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', help='directory for images')
    parser.add_argument('--count', '-c', help='number of images to download',
                        type=int, default=100)
    args = parser.parse_args()
    if args.output is None:
        parser.error('please specify an output directory with --output')


    web_dir = 'https://lilablobssc.blob.core.windows.net/caltech-unzipped/cct_images'
    local_dir = args.output.strip()
    if not os.path.exists(local_dir):
        os.mkdir(local_dir)
    bbox_annotations = json.load(open('caltech_bboxes_multiclass_20190922.json'))
    image_ids = sorted([d['image_id'] for d in bbox_annotations['annotations']])

    paths = []
    current_paths = set(['%s/%s' % (local_dir, p) for p in os.listdir(local_dir)])
    meta_data = []
    date = '2020-03-04 00:00:00'
    for i, image_id in enumerate(image_ids[:args.count]):
        web_path = '%s/%s.jpg' % (web_dir, image_id)
        local_path = '%s/%s.jpg' % (local_dir, image_id)
        if local_path not in current_paths:
            paths.append((web_path, local_path))
        meta_data.append({
            'upload_id': i,
            'image_path': local_path,
            'observation_time': date
        })
        if i == int(args.count / 2) - 1:
            with open('first_meta_data.json', 'w') as fh:
                json.dump(meta_data, fh)
            date = '2020-03-05 00:00:00'
            meta_data = []
    with open('second_meta_data.json', 'w') as fh:
        json.dump(meta_data, fh)

    with futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_path = {
            executor.submit(
                requests.get, web_path
            ): local_path
            for web_path, local_path in paths
        }
        for future in tqdm(futures.as_completed(future_to_path)):
            r = future.result()
            local_path = future_to_path[future]
            with open(local_path, 'wb') as file:
                file.write(r.content)