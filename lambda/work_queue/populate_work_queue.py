import os
import redis
import psycopg2
from datetime import datetime


if __name__ == '__main__':
    redis_client = redis.Redis(
        host=os.environ['REDIS_HOSTNAME'],
        port=6379,
        password=os.environ['REDIS_PASSWORD']
    )
    
    conn = psycopg2.connect('host=%s dbname=postgres user=postgres password=%s' 
                            % (os.environ['POSTGRES_HOSTNAME'], 
                               os.environ['POSTGRES_PASSWORD']))
    
    # first we need to grab a list of all of all of the projects
    cursor = conn.cursor()
    sql = '''
    SELECT DISTINCT(project) FROM classifications
    '''
    cursor.execute(sql)
    projects = [result[0] for result in cursor]
    print('Found projects ', projects)
    
    # next we can update the streams for each project
    time_format = '%Y-%m-%d %H:%M:%S.%f'
    field_to_index = {
        'upload_id': 0,
        'detection_id': 1,
        'observation_time': 2,
        'class_name': 3,
        'c0': 4, 'c1': 5,
        'c2': 6, 'c3': 7,
        'c4': 8,
        'y0': 9, 'y1': 10,
        'x0': 11, 'x1': 12,
    }
    for project in projects:
        print('Working on project ', project)
        stream_name = '%s_validation_work_stream' % project
        # first we check to see if the stream has anything in it
        if redis_client.xlen(stream_name) == 0:
            latest_time = datetime(1970, 1, 1)
            print('Stream currently empty')
        else:
            # if the stream does exist we grab the latest entry
            latest_entry = redis_client.xrevrange(stream_name, count=1)[0][1]
            latest_time = \
                datetime.strptime(latest_entry[b'observation_time'].decode("utf-8"),
                                  time_format)
            print('Latest time ', latest_time)
        # next we query all the validations that come after this point in
        # time
        sql = '''
        SELECT
        c.upload_id,
        c.detection_id,
        c.observation_time,
        c.class_name,
        c.c0, c.c1, c.c2, 
        c.c3, c.c4,
        d.y0, d.y1, d.x0, d.x1
        FROM 
        classifications as c
        LEFT JOIN detections as d
        ON c.upload_id = d.upload_id 
        AND c.detection_id = d.detection_id
        WHERE not c.validated AND c.project = '%s'
        AND c.observation_time > '%s'
        ORDER BY c.observation_time ASC
        ''' % (project, latest_time)
        cursor = conn.cursor()
        cursor.execute(sql)
        records = []
        for result in cursor:
            record = {
                k: result[v] for k, v in field_to_index.items()
            }
            record['observation_time'] = \
                record['observation_time'].strftime(time_format)
            records.append(record)
        # now we can add to the stream
        for record in records:
            redis_client.xadd(stream_name, record)
        print('Added ', len(records), ' to stream')

        # now we just ensure that the validation_workers group
        # had been created for this stream
        groups_info = redis_client.xinfo_groups(stream_name)
        group_names = [group['name'].decode('utf-8') for group in groups_info]
        if 'validation_workers' not in group_names:
            print('creating validation_workers group for stream')
            redis_client.xgroup_create(stream_name, 'validation_workers', id=0)
