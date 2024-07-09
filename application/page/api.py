from application import app, bcrypt
from application.page import catchError, HTTP_STAT
from application.page.prosses import IotProssesing
from application.DBcontrol import default_ope
from flask import request, jsonify
from datetime import datetime as dt, timedelta
import pytz
import re

DORMITORYS = ("CEN", "MOU", "SEA", "SPA")
M_TYPES = ("WA", "DR", "PB", "SW")
PB_MAX_NUM = 3
# BIRST_TIME = timedelta(minutes=5)
BIRST_TIME = timedelta(weeks=9)

# PROPOSAL
# Collect variables into a buffer and INSERT them periodically in application.bot.
# ---------
# Insert IoTData
@app.route("/", methods=['POST'])
@catchError
def root():
  remote_addr = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
  stmt = 'SELECT T.sendIoTID, T.IoTID FROM `send_iot_info` AS T WHERE T.sendIoTIP = %(IP)s;'
  IoT_info = default_ope.query(str(stmt), args={'IP': str(remote_addr)}, prepared=True, dictionary=True)

  if not IoT_info:
    app.logger.info(f'Unauthorized access. ID:IPaddr[{remote_addr}]')
    return HTTP_STAT(403)

  sendIoT = IoT_info[0]['sendIoTID']
  IoTs = [ i['IoTID'] for i in IoT_info ]

  request_data = request.json if request.headers.get('Content-Type') == 'application/json' else request.get_data()
  args = IotProssesing(sendIoT, IoTs, request_data)
  
  if args is None:
    return HTTP_STAT(500)
  elif isinstance(args, int):
    return HTTP_STAT(400)
  elif not isinstance(args, list):
    app.logger.error(f"Unexpected return value: {args}")
    return HTTP_STAT(500)

  if len(args) == 1:
    args = args[0]
    many = False
  else:
    many = True

  app.logger.debug(f'data: "{"bytes" if len(request_data) > 100 else request_data}" stat:"{args}"')

  stmt = " INSERT INTO `IoTData`(`IoTID`, `dataStatus`) VALUES(%(ID)s, %(stat)s);"

  default_ope.query(stmt, commit=True, args=args, many=many, prepared=True)
  return jsonify({'status': 'success', 'data': args}), 200


# get latest dashboard data
@app.route('/api/dashboard', methods=['GET'])
@catchError
def dashboad():
  #一定時間送られていないデバイスはnullを送るようにする
  timeExclusion = request.args.get("timeExclusion", False)
  if timeExclusion:
    app.logger.info("Invalid query parameters")
    return HTTP_STAT(400)

  dormitory = request.args.get('dormitory', 'ALL').upper()
  floor = request.args.get('floor', 'ALL').upper()
  m_type = request.args.get('type', 'ALL').upper()

  if floor == "ALL":
    floor = 0;
  elif re.fullmatch(r"[1-5]", floor):
    floor = int(floor)
  else:
    app.logger.info("Invalid query parameters")
    return HTTP_STAT(400)

  where = ""
  args = dict()
  if m_type in M_TYPES:
    where += " AND T.ID LIKE %(m_type)s"
    args["m_type"] = f"{m_type}_%"
  elif m_type != 'ALL':
    app.logger.info("Invalid query parameters")
    return HTTP_STAT(400)

  if dormitory in DORMITORYS:
    if m_type != "PB":
      where += " AND T.place "
      if floor != 0:
        where += "= %(place)s"
        args["place"] = f"{dormitory}_{floor}"
      else:
        where += "LIKE %(place)s"
        args["place"] = f"{dormitory}_%"
  elif dormitory != 'ALL':
    app.logger.info("Invalid query parameters")
    return HTTP_STAT(400)

  stmt = "SELECT T.ID, T.stat, T.place, T.num, T.time FROM `latest_dashboard` AS T"
  stmt += f" WHERE {where[5:]};" if where else ";"
  # app.logger.debug(f'stmt: {stmt}, args: {args}')

  res = default_ope.query(stmt, args=args, dictionary=True, prepared=True)
  dashboard = dict()
  max_num = dict()

  def add_data(d, m_n, n):
    if len(n) > 3:
      if n[0] not in d.keys():
        d[n[0]] = dict()
        m_n[n[0]] = dict()
      add_data(d[n[0]], m_n[n[0]], n[1:])
    elif len(n) == 3:
      if n[0] not in d.keys():
        d[n[0]] = [None, None, None, None, None]
        m_n[n[0]] = n[1]
      elif m_n[n[0]] < n[1]:
        m_n[n[0]] = n[1]
      add_data(d[n[0]], m_n[n[0]], n[1:])
    else:
      d[n[0] - 1] = n[1]

  def trimming_data(d, d_num, check=lambda x1, x2: [ x1[i] if x1[i] is None else x1[i][0] for i in range(x2) ]):
    if type(d_num) is int:
      return check(d, d_num)
    else:
      return { k: trimming_data(d[k], d_num[k], check=check) for k in d.keys() }

  def check_timelimit(d, d_num):
    print(d, d_num)
    limtime = dt.now(pytz.timezone('Asia/Tokyo')).replace(tzinfo=None) - BIRST_TIME
    return [ None if d[i] is None else d[i][0] if limtime <= d[i][1] else None for i in range(d_num) ]
      
  for d in res:
    if d['ID'][:2] == 'PB':
      add_data(dashboard, max_num, [d['ID'][:2], d['num'], (d['stat'], d['time'])])
    elif d['ID'][:2] == 'SW':
      add_data(dashboard, max_num, [d['place'][:3], d['ID'][:2], d['num'], (d['stat'], d['time'])])
    else:
      add_data(dashboard, max_num, [d['place'][:3], f"F{d['place'][4:]}", d['ID'][:2], d['num'], (d['stat'], d['time'])])

  if timeExclusion:
    dashboard = trimming_data(dashboard, max_num, check=check_timelimit)
  else:
    dashboard = trimming_data(dashboard, max_num)
  # app.logger.debug(f'dashboard: {dashboard}')
  return dashboard

# dashboard = {
#   "MOU" : {
#     "F1": {
#       "WA": [True, False, True, True]
#       "DR": [True, False, True, True]
#     },
#     "F2": {
#       "WA": [True, False, True, True]
#       "DR": [None, False, True, True]
#     }
#   },
#   "SEA" : {},
#   "PB": [2, None, 3]

# }
