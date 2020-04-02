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
        'project': 0,
        'upload_id': 1,
        'observation_time': 2,
        'detection_id': 3,
        'class_name': 4,
        'c0': 6, 'c1': 7,
        'c2': 8, 'c3': 9,
        'c4': 10
    }
    for project in projects:
        print('Working on project ', project)
        stream_name = '%s_validation_work_stream' % project
        # first we check to see if the stream has anything in it
        if redis_client.xlen(stream_name) == 0:
            latest_time = datetime.datetime(1970, 1, 1)
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
        SELECT * FROM classifications
        WHERE NOT validated AND project = '%s'
        AND observation_time > '%s'
        ORDER BY observation_time ASC
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
        group_names = [group['name'].decode('utf-8') for group in groups]
        if stream_name not in group_names:
            print('creating validation_workers group for stream')
            redis_client.xgroup_create(stream_name, 'validation_workers', id=0)
