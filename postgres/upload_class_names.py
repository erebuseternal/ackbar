import psycopg2
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sql', help='hostname of postgres server',
                        type=str, default='172.17.0.2')
    parser.add_argument('--password', help='password for postgres tables',
                        type=str, default='ackbar')
    args = parser.parse_args()
    
    conn = psycopg2.connect('host=%s dbname=postgres user=postgres password=%s' %
                                (args.sql, args.password))
    
    class_names = ['badger', 'bird', 'bobcat', 'car', 'cat', 'coyote', 'deer', 'dog', 
    'fox', 'insect', 'lizard', 'mountain_lion', 'opossum', 'rabbit',
    'raccoon', 'rodent', 'skunk', 'squirrel']
    records = [('caltech', name) for name in class_names]
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO class_names VALUES (%s, %s)",
        records
    )
    conn.commit()
    print(cursor.rowcount, ' records committed')