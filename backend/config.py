import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///lumi.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ORS_API_KEY = os.getenv('ORS_API_KEY')

    LOG_DIR = 'logs'
    MODEL_DIR = '../ml_models'

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Currency
    SUPPORTED_CURRENCIES = ['INR', 'USD', 'EUR', 'GBP']
    DEFAULT_CURRENCY = 'INR'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'



# ═══════════════════════════════════════════════
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}