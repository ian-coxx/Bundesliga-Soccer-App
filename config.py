import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')  # Use an environment variable or default value
    DATABASE_URI = 'sqlite:///bundesliga.db'  # Path to your SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking in Flask-SQLAlchemy
