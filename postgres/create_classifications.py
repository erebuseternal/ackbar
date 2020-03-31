import psycopg2
import argparse
import requests
import datetime
import random


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sql', help='hostname of postgres server',
                        type=str, default='172.17.0.2')
    parser.add_argument('--password', help='password for postgres tables',
                        type=str, default='ackbar')
    args = parser.parse_args()
    
    class_names = ['badger', 'bird', 'bobcat', 'car', 'cat', 'coyote', 'deer', 'dog', 
    'fox', 'insect', 'lizard', 'mountain_lion', 'opossum', 'rabbit',
    'raccoon', 'rodent', 'skunk', 'squirrel']
    
    conn = psycopg2.connect('host=%s dbname=postgres user=postgres password=%s' %
                                (args.sql, args.password))
    
    sql = """
    SELECT observation_time FROM classifications 
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
    SELECT project, upload_id, observation_time, detection_id FROM detections
    WHERE observation_time > '%s'
    """ % latest_date
    cursor = conn.cursor()
    cursor.execute(sql)
    records = []
    for result in cursor:
        top_five = random.sample(class_names, 5)
        record = list(result) + [top_five[0], False] + top_five
        records.append(record)
        
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO classifications VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        records
    )
    conn.commit()
    print(cursor.rowcount, ' records committed')
    
    