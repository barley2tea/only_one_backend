from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class DefaultConfig:
  DEBUG = False
  TESTING = False
  PERMANENT_SESSION_LIFETIME = timedelta(days=2)
  SECRET_KEY = "k0e8gGIgIFiLmGyd4yfjFEYioU4w9Dt2o908zx3EtjGD5UIoljFr45Y004dFh"


class DevelopmentConfig(DefaultConfig):
  DEBUG = True
  TESTING = True


class TestingConfig(DefaultConfig):
  DEBUG = False
  TESTING = True
