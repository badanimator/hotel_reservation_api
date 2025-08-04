import os, secrets
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    PROPAGATE_EXCEPTIONS = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_BLACKLIST_ENABLED = True
    SECRET_KEY = secrets.token_hex(64)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MIGRATION_PATH = os.environ.get("MIGRATION_PATH") or "migrations"
    CACHE_STORAGE = os.environ.get("CACHE_STORAGE")
    SESSION_TYPE = 'sqlalchemy'
    CACHE_TYPE = "SimpleCache"

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    }
