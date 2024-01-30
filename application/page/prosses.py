from application import app
from application.exception import ProssesException
from ultralytics import YOLO
import os
import json

PB_model = YOLO(os.getenv('MODEL_PATH'))

def doing_prosses(func):
  def wrapper(*args, **kwargs):
    try:
      pros = func(*args, **kwargs)
    except ProssesException as e:
      app.warning(str(e))
    if pros is None:
      app.warning('No action is defined for this id')
    return None if pros is None else pros(*args, **kwargs)
  return wrapper


@doing_prosses
def IotProssesing(IoT_id:str, data:str):
  return  PB_prosses        if IoT_id[:2] == 'PB' else\
          SW_prosses        if IoT_id[:2] == 'SW' else\
          DR_prosses        if IoT_id[:2] == 'DR' else None



def SW_prosses(IoT_id:str, data:bytes):
  PARAMETER_DICT = {'2': 3700, '3': 3000}#山は3700海は3000
  # prosses
  parameter = PARAMETER_DICT.get(IoT_id[3], 3700)
  status = 'True' if parameter > int(data) else 'False'
  # prosses
  return status
 
def DR_prosses(IoT_id:str, data:bytes):
  PARAMETER_DICT = {'211': 3700, '212': 3000}#特殊な加速度の値が出力されたidはここに条件と3ケタ数字書く
  # prosses                         
  str_data=data.decode("utf-8")
  json_data=json.loads(str_data)
  parameterx = PARAMETER_DICT.get(IoT_id[3:], 0.1)
  parametery = PARAMETER_DICT.get(IoT_id[3:], 0.1)
  datax=json_data["datax"]
  datay=json_data["datay"]
  status = 'True' if parameterx < abs(int(datax)) and parametery < abs(int(datay)) else 'False'
  # prosses
  return status

def PB_prosses(IoT_id:str, data:bytes):
  if PB_model is None:  raise ProssesException('model is not include')
  #dataのエンコード(確かjpegで送られてくる)

  
