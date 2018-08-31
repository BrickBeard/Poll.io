import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'poll_io.db')
SECRET_KEY = 'fajita_nachos_supreme'  # Keep this key secret in production
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
SQLALCHEMY_TRACK_MODIFICATIONS = True
DEBUG = True
