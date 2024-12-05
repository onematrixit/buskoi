import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'f7fd58d5d9a0fad34ac36248bc3b8d71'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/bus_management'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
