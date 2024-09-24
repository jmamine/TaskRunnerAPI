import logging
import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Base configuration class.
    """
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    DEBUG =os.environ.get('DEBUG').lower() in ('true', '1')
    TESTING = os.environ.get('TESTING').lower() in ('true', '1')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PORT = int(os.environ.get('PORT'))
    # Add other configuration options as needed

class DevelopmentConfig(Config):
    """
    Development configuration class.
    """
    DEBUG = os.environ.get('DEBUG').lower() in ('true', '1')
    # Add development-specific configuration options if needed

class ProductionConfig(Config):
    """
    Production configuration class.
    """
    # Add production-specific configuration options if needed
    

class TestingConfig(Config):
    """
    Testing configuration class.
    """
    TESTING = os.environ.get('TESTING').lower() in ('true', '1')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    # Add testing-specific configuration options if needed

# Dictionary to hold the different configuration classes
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# Select the configuration class based on the environment 
def get_config(env):
    try:
        return config_dict.get(env, Config)()
    except Exception as e:
        logging.exception('An error occurred while getting configuration: %s', e)
        return Config()
