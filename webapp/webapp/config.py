import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    REDIS_PASSWORD = 'ackbar'
    REDIS_HOST = 'localhost'
    STORAGE_HOST = '172.17.0.3'
    STORAGE_PORT = 5000
    POSTGRES_HOST = '172.17.0.2'
    POSTGRES_PASSWORD = 'ackbar'
    POSTGRES_USER = 'postgres'
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