from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
import os

class DefaultConfig:
  DEBUG = False
  TESTING = False
  PERMANENT_SESSION_LIFETIME = timedelta(days=2)
  SECRET_KEY = os.environ['SECRET_KEY']


class DevelopmentConfig(DefaultConfig):
  DEBUG = True
  TESTING = True


class TestingConfig(DefaultConfig):
  DEBUG = False
  TESTING = True
