import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'  # Hoặc dùng MySQL, PostgreSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False