import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    REDIS_PASSWORD = 'ackbar'
    REDIS_HOST = 'localhost'
    @staticmethod
    def init_app(app):
        pass

    
config = {
    'development': Config,
}