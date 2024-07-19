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

# Insert IoTData
@app.route("/", methods=['POST'])
@catchError
def root():
  # IP filtering.
  remote_addr = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
  stmt = 'SELECT T.sendIoTID, T.IoTID FROM `send_iot_info` AS T WHERE T.sendIoTIP = %(IP)s;'
  IoT_info = default_ope.query(str(stmt), args={'IP': str(remote_addr)}, prepared=True, dictionary=True)

  if not IoT_info:
    app.logger.info(f'Unauthorized access. ID:IPaddr[{remote_addr}]')
    return HTTP_STAT(403)

  # Get sendIoT's ID and Device IDs that are allowed to send.
  sendIoT = IoT_info[0]['sendIoTID']
  IoTs = [ i['IoTID'] for i in IoT_info ]

  # Get request data and format it for DB
  request_data = request.json if request.headers.get('Content-Type') == 'application/json' else request.get_data()
  args = IotProssesing(sendIoT, IoTs, request_data)
  
  if type(args) is int:
    return HTTP_STAT(args)

  # Insert IoTData
  if len(args) <= 1:
    args = args[0]
    many = False
  else:
    many = True

  app.logger.debug(f'data: "{"bytes" if len(request_data) > 100 else request_data}" stat:"{args}"')
  stmt = " INSERT INTO `IoTData`(`IoTID`, `dataStatus`) VALUES(%(ID)s, %(stat)s);"
  default_ope.query(stmt, commit=True, args=args, many=many, prepared=True)
  return jsonify({'status': 'success', 'data': args}), 200


# Get latest dashboard data.
@app.route('/api/dashboard', methods=['GET'])
@catchError
def dashboad():
  # Get arguments and return 400 if the argument is invalid.
  # The parameters are case-insensitive.
  timeExclusion = request.args.get("timeExclusion", None)
  if timeExclusion is not None and timeExclusion.upper() != "TRUE":
    app.logger.info("Invalid request parameters")
    return HTTP_STAT(400)
  else:
    timeExclusion = bool(timeExclusion)

  dormitory = request.args.get('dormitory', 'ALL').upper()
  floor = request.args.get('floor', 'ALL').upper()
  m_type = request.args.get('type', 'ALL').upper()

  if re.fullmatch(r"[1-5]", floor):
    floor = int(floor)
  elif floor != "ALL":
    app.logger.info("Invalid request parameters")
    return HTTP_STAT(400)

  # Create the where clause of the query in parallel
  where = ""
  args = dict()
  if m_type in M_TYPES:
    where += " AND T.ID LIKE %(m_type)s"
    args["m_type"] = f"{m_type}_%"
  elif m_type != 'ALL':
    app.logger.info("Invalid request parameters")
    return HTTP_STAT(400)

  if dormitory in DORMITORYS:
    if m_type != "PB":
      where += " AND T.place "
      if floor != "ALL":
        where += "= %(place)s"
        args["place"] = f"{dormitory}_{floor}"
      else:
        where += "LIKE %(place)s"
        args["place"] = f"{dormitory}_%"
  elif dormitory != 'ALL':
    app.logger.info("Invalid request parameters")
    return HTTP_STAT(400)

  stmt = "SELECT T.ID, T.stat, T.place, T.num, T.time FROM `latest_dashboard` AS T"
  stmt += f" WHERE {where[5:]};" if where else ";"

  # Fetch responce from DB.
  res = default_ope.query(stmt, args=args, dictionary=True, prepared=True)

  def format_dashboard(kl, board):
    if len(kl) == 2:
      if len(board) <= kl[0] - 1:
        [ board.append(None) for _ in range(kl[0] - len(board)) ]
      board[kl[0] - 1] = kl[1]
    elif len(kl) > 2:
      if kl[0] not in board.keys():
        board[kl[0]] = dict() if len(kl) > 3 else list()
      format_dashboard(kl[1:], board[kl[0]])
    else:
      raise ValueError(f"invalid key_list: {kl}")
  
  dashboard = dict()
  check = (lambda s, t: s) if timeExclusion else\
          (lambda s, t: None if dt.now(pytz.timezone('Asia/Tokyo')).replace(tzinfo=None) - BIRST_TIME > t else s)
  for d in res:
    ID = d['ID'][:2]
    status = check(d['stat'], d['time'])
    key_list = [ID, d['num'], status] if ID == 'PB' else\
               [d['place'][:3], ID, d['num'], bool(status)] if ID == 'SW' else\
               [d['place'][:3], f"F{d['place'][4:]}", ID, d['num'], bool(status)]
    format_dashboard(key_list, dashboard)

  # app.logger.debug(f'dashboard: {dashboard}')
  return dashboard
