import json

with open('config_ex.json') as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    STATIC_FOLDER = config.get('STATIC_FOLDER')
    S3_BUCKET = config.get('S3_BUCKET')
    S3_ACCESS = config.get('S3_ACCESS')
    S3_PRIVATE = config.get('S3_PRIVATE')
