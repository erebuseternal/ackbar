import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    REDIS_PASSWORD = 'ackbar'
    REDIS_HOST = 'localhost'
    STORAGE_HOST = '172.17.0.3'
    STORAGE_PORT = 5000
    POSTGRES_HOST = os.environ['POSTGRES_HOSTNAME']
    POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
    POSTGRES_USER = 'ackbar@ackbar-postgres'
    POSTGRES_DB = 'postgres'
    SQLALCHEMY_DATABASE_URI = ('postgresql+psycopg2://%s:%s@%s/%s' 
                               % (POSTGRES_USER, POSTGRES_PASSWORD, 
                                  POSTGRES_HOST, POSTGRES_DB))
    @staticmethod
    def init_app(app):
        pass

    
config = {
    'development': Config,
}