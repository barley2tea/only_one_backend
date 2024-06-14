from application import app
from application.exception import ProssesException
from ultralytics import YOLO
import os
import json
import io
import glob
import re
from PIL import Image

PB_model = YOLO(os.getenv('MODEL_PATH'))

def doing_prosses(func):
  def wrapper(*args, **kwargs):
    pros = func(*args, **kwargs)
    if pros is None:
      app.logger.warning('No action is defined for this id')
      return None

    try:
      ret = pros(*args, **kwargs)
    except ProssesException as e:
      app.logger.warning(str(e))
      return None
    except Exception as e:
      app.logger.error(str(e))
      return None

    return ret
  return wrapper

@doing_prosses
def IotProssesing(IoT_id:str, data:str):
  return  normal_process    if IoT_id[:2] == 'WD' else\
          PB_prosses        if IoT_id[:2] == 'PB' else\
          SW_prosses        if IoT_id[:2] == 'SW' else\
          DR_prosses        if IoT_id[:2] == 'DR' else None

def normal_process(IoT_id:str, data:dict):
  if not isinstance(data, dict):
    raise ProssesException('JSON is not being sent.')

  return [ {'ID': k, 'stat': data[k]} for k in data.keys() ]

def SW_prosses(IoT_id:str, data:dict):
  if not isinstance(data, dict):
    raise ProssesException('JSON is not being sent.')

  PARAMETER_DICT = {'2': 3700, '3': 3000}#山は3700海は3000
  return int(PARAMETER_DICT.get(IoT_id[3], 3700) > data['sensorValue'])
 
def DR_prosses(IoT_id:str, data:dict):
  data = data['sensorValue']
  data = [ int(d, 10) if re.fullmatch('\d+', d) else None for d in data ]
  if None in data:
    status = [0, 0, 0]
  else:
    status = [0, data[3], data[4]]
    status[0] = int(0.1 < abs(data[0]) and 0.1 < abs(data[1]))
  return [ {'ID': f'{IoT_id[:-1]}{i}', 'stat': stat} for (i, stat) in enumerate(status) ]

def PB_prosses(IoT_id:str, data:bytes):
  if PB_model is None:  raise ProssesException('model is not include')

  #test
  if os.getenv('SAVE_IMAGE', 'False') == 'True':
    test_dir = os.getenv('TEST_DIRECTORY', '.')
    with open(f"{test_dir}/{len(glob.glob(test_dir))}.jpg", 'wb') as f:
      f.write(data)
  
  with Image.open(io.BytesIO(data)) as pil_img:
    img = np.asarray(pil_img)

  res = PB_model(img)
  return int((len(res) + 1) // 2)


  
