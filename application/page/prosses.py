
def doing_prosses(func):
  def wrapper(*args, **kwargs):
    pros = func(*args, **kwargs)
    if pros is None:
      raise Exception('No action is defined for this id')
    return None if pros is None else pros(*args, **kwargs)
  return wrapper


@doing_prosses
def IotProssesing(IoT_id:str, data:str):
  return  test_prosses if IoT_id[:3] == 'PCt' else  None

PARA = {'1': 100, '2': 200, '3': 300}

def test_prosses(IoT_id:str, data:str):
  try:
    d = int(data)
  except Exception as e:
    d = 0
  return 1 if d > PARA.get(IoT_id[3]) else 0
 
