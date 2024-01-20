from application.bot import bot_logger, bots, fixedIntervalThread
from application.DBcontrol import default_ope, insertvalsql
import requests
import time
import hashlib
import hmac
import base64
import threading
import json
import os
__all__ = []

SW_BOT_INTERVAL = 180000

# Convert to format to save in DB
def swStatFormat(res):
  return 1 if res['erectricCurrent'] > 1000 else 0

class switchBotController:
  def __init__(self, IoTID, url, headers):
    self.IoTID = IoTID
    self.url = url
    self.headers = headers

  @classmethod
  def make_sign(self, token, secret):
    nonce = ''
    t = int(round(time.time() * 1000))
    string_to_sign = bytes(f'{token}{t}{nonce}', 'utf-8')
    secret = bytes(secret, 'utf-8')
    sign = base64.b64encode(
      hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256)  \
          .digest()
    )
    return sign, str(t), nonce

  @classmethod
  def make_request_header(self, token: str,secret: str) -> dict:
    sign,t,nonce = self.make_sign(token, secret)
    headers={
      "Authorization": token,
      "sign": sign,
      "t": str(t),
      "nonce": nonce
    }
    return headers

  def command(self, com):
    pass

  def status(self):
    try:
      res = requests.get(f"{self.url}/status", headers=self.headers)
      res.raise_for_status()
      return json.loads(res.text)
    except requests.exceptions.RequestException as e:
      bot_logger.warning(str(e))
      return None


# def get_device_list(deviceListJson='deviceList.json'):
#   # tokenとsecretを貼り付ける
#   token = ""
#   secret = ""
#   base_url = 'https://api.switch-bot.com'

#   devices_url = base_url + "/v1.1/devices"

#   headers = switchBotController.make_request_header(token, secret)

#   try:
#     # APIでデバイスの取得を試みる
#     res = requests.get(devices_url, headers=headers)
#     res.raise_for_status()

#     print(res.text)
#     deviceList = json.loads(res.text)
#     # 取得データをjsonファイルに書き込み
#     with open(deviceListJson, mode='wt', encoding='utf-8') as f:
#       json.dump(deviceList, f, ensure_ascii=False, indent=2)

#   except requests.exceptions.RequestException as e:
#     print('response error:',e)


SWITCHBOT_CONFIG = json.load(open(os.getenv('SWITCHBOT_CONFIG_JSON'), 'r'))
_header = switchBotController.make_request_header( SWITCHBOT_CONFIG['token'], SWITCHBOT_CONFIG['secret'])

INSERT_DORMITORY_DATA = str(insertvalsql(['IoTID', 'dataStatus'], 'IoT_Data', ['id', 'stat']))

botLeaders = [
  switchBotController(
    IoTID=conf['IoTID'],
    url=f"{SWITCHBOT_CONFIG['url']}/{conf['deviceid']}",
    headers=_header
  )
  for conf in SWITCHBOT_CONFIG['devices']
]


def sw_work():
  global botLeaders
  state = [ s for s in [  (st.IoTID, st.status()) for st in botLeaders ] if s[1] is not None and s[1]['body']]
  if not state: return

  try:
    args = [ { "id": st[0], "stat": swStatFormat(st[1]) } for st in state]
    ope.query(INSERT_DORMITORY_DATA, commit=True, args=args, many=True, prepared=True)
  except KeyError as e:
    bot_logger.error(f'KeyError: {str(e)}')
    bot_logger.error(f'response: {str(state)}')
  except Exception as e:
    bot_logger.error(str(e))
    bot_logger.error(f'response: {str(state)}')

# add bot
bots['switch_bot'] = fixedIntervalThread(sw_work, SW_BOT_INTERVAL)


del _header
del SWITCHBOT_CONFIG
