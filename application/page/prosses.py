from application import app
from application.exception import ( 
  ProssesException,
  RequestTypeError,
  RequestValueError,
  RequestException
)
from ultralytics import YOLO
import os
import io
import glob
import numpy as np
from PIL import Image, UnidentifiedImageError

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
    except RequestException as e:
      app.logger.info(str(e))
      return -1
    except Exception as e:
      app.logger.error(str(e))
      return None

    if not isinstance(ret, list):
      app.logger.error('Invalid return value in "{pros.__name__}"')
      return None

    return ret
  return wrapper

@doing_prosses
def IotProssesing(sendIoT:str, IoTs:list, data:str):
  return  normal_process    if sendIoT[:2] == 'WD' else\
          PB_prosses        if sendIoT[:2] == 'PB' else\
          normal_process    if sendIoT[:2] == 'SW' else\
          DR_prosses        if sendIoT[:2] == 'DR' else None

def normal_process(sendIoT:str, IoTs:list, data:dict):
  if not isinstance(data, dict):
    raise RequestTypeError(f'JSON is not being sent. sendIoT:{sendIoT}')

  unexpected_iot = set(data.keys()) - set(IoTs)
  if unexpected_iot:
    raise RequestValueError(f'Unexpected IoT devices:{unexpected_iot}, sendIoT:{sendIoT}')

  return [ {'ID': k, 'stat': data[k]} for k in data.keys() ]

def PB_prosses(sendIoT:str, IoTs:list, data:bytes):
  unexpected_iot = set([sendIoT]) - set(IoTs)
  if unexpected_iot:
    raise RequestValueError(f'Unexpected IoT devices:{unexpected_iot}, sendIoT:{sendIoT}')

  PB_model = YOLO(os.getenv('MODEL_PATH'))
  if PB_model is None:  raise ProssesException('model is not include')

  try:
    with Image.open(io.BytesIO(data)) as pil_img:
      img = np.asarray(pil_img)
  except UnidentifiedImageError as e:
    raise RequestTypeError(f'Cannt identify image file')

  if not (len(img.shape) == 3 and img.shape[2] == 3):
    raise RequestValueError(f'Bad image. shape={img.shape}')

  #test
  if os.getenv('SAVE_IMAGE', 'False') == 'True':
    test_dir = os.getenv('TEST_DIRECTORY', '.')
    num = len(glob.glob(f'{test_dir}/*'))
    with open(f"{test_dir}/{num}.jpg", 'wb') as f:
      f.write(data)

  res = PB_model(img)
  return [ {'ID': sendIoT, 'stat': int((len(res) + 1) // 2)} ]


  
