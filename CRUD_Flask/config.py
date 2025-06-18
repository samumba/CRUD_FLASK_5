import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'FLSDKFGLWSDKFGWERP2O34I23O5JKTO2'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False