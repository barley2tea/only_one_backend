

from application.util.prosses import IotProssesing
from application.util.api_util import *

from ultralytics import settings
import os
settings.update({'runs_dir': f"{os.getenv('TEST_DIRECTORY')}/result"})
