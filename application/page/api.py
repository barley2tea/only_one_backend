from application import app
from application.page import catchError, HTTP_STAT
from application.util import IotProssesing, getRequest
from application.DBcontrol import default_ope, iotdata_ope
from flask import request, jsonify
from datetime import datetime as dt, timedelta
from functools import reduce
import pandas as pd
import pytz
import re


# Insert IoTData
@app.route("/", methods=['POST'])
@catchError
def root():
  # IP filtering.
  remote_addr = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
  stmt = 'SELECT T.sendIoTID, T.IoTID FROM `send_iot_info` AS T WHERE T.sendIoTIP = %(IP)s;'
  IoT_info = iotdata_ope.query(str(stmt), args={'IP': str(remote_addr)}, prepared=True, dictionary=True)

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
  iotdata_ope.query(stmt, commit=True, args=args, many=many, prepared=True)
  return jsonify({'status': 'success', 'data': args}), 200


# Get latest dashboard data.
@app.route('/api/dashboard', methods=['GET'])
@catchError
def dashboad():
  # Get arguments and return 400 if the argument is invalid.
  # The parameters are case-insensitive.
  timeExclusion = request.args.get("timeExclusion", None)
  reqargs = getRequest(request.args, ["dormitory", "floor", "type"])
  if reqargs is None or timeExclusion is not None and timeExclusion.upper() != "TRUE":
    app.logger.info("Invalid request parameters")
    return HTTP_STAT(400)

  timeExclusion = bool(timeExclusion)
  dormitory = reqargs["dormitory"]
  floor = reqargs["floor"]
  m_type = reqargs["type"]

  # Create the where clause of the query in parallel
  where = ""
  args = dict()
  if m_type != "ALL":
    where += " AND T.ID LIKE %(m_type)s"
    args["m_type"] = f"{m_type}_%"

  if dormitory != "ALL" and m_type != "PB":
    where += " AND T.place "
    if floor == "ALL":
      where += "LIKE %(place)s"
      args["place"] = f"{dormitory}_%"
    else:
      where += "= %(place)s"
      args["place"] = f"{dormitory}_{floor}"

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
          (lambda s, t: None if dt.now(pytz.timezone('Asia/Tokyo')).replace(tzinfo=None) - timedelta(minutes=5) > t else s)
  for d in res:
    ID = d['ID'][:2]
    status = check(d['stat'], d['time'])
    key_list = [ID, d['num'], status] if ID == 'PB' else\
               [d['place'][:3], ID, d['num'], bool(status)] if ID == 'SW' else\
               [d['place'][:3], f"F{d['place'][4:]}", ID, d['num'], bool(status)]
    format_dashboard(key_list, dashboard)

  # app.logger.debug(f'dashboard: {dashboard}')
  return dashboard

@app.route('/api/dashboard_details', methods=['GET'])
@catchError
def dashboard_details():
  timeExclusion = request.args.get("timeExclusion", None)
  reqargs = getRequest(request.args, ["id", "dormitory", "floor", "type"], default=None)
  if reqargs is None or timeExclusion is not None and timeExclusion.upper() != "TRUE":
    app.logger.info("Invalid request parameters")
    return HTTP_STAT(400)

  stmt = """
SELECT T1.IoTID, T1.dataStatus AS status, T5.dormitory, T4.floor, T3.No , DATE_FORMAT(T1.time, "%Y-%m-%d %H:%i:%s") AS time, T6.type
FROM
  `IoTData` AS T1
  INNER JOIN (
    SELECT ST1.IoTID AS IoTID, MAX(ST1.time) AS time
    FROM `IoTData` AS ST1
    GROUP BY ST1.IoTID
  ) AS T2 ON T1.IoTID = T2.IoTID AND T1.time = T2.time
  INNER JOIN `IoT` AS T3 ON T1.IoTID = T3.IoTID
  LEFT OUTER JOIN `dormitoryPlace` AS T4 ON T3.dormitoryPlaceID = T4.dormitoryPlaceID
  LEFT OUTER JOIN `dormitory` AS T5 ON T4.dormitoryID = T5.dormitoryID
  INNER JOIN IoTType AS T6 ON T3.IoTTypeID = T6.IoTTypeID
WHERE
  ( %(id)s IS NULL OR T1.IoTID = %(id)s )
  AND ( %(floor)s IS NULL OR T4.floor = %(floor)s )
  AND ( %(dormitory)s IS NULL OR T5.dormitory = %(dormitory)s )
  AND ( %(type)s IS NULL OR T6.type = %(type)s )
"""
  res = default_ope.query(stmt, args=reqargs, dictionary=True, prepared=True)

  stmt = """
SELECT T3.IoTID, DATE_FORMAT(MIN(T3.time), "%Y-%m-%d %H:%i:%s") AS time
FROM
  IoTData T2
  INNER JOIN IoTData T3
    ON T2.IoTID = T3.IoTID AND T2.time < T3.time AND T2.dataStatus = 1 AND T3.dataStatus = 0
  INNER JOIN ( SELECT T.IoTID, MAX(T.time) time FROM IoTData T WHERE T.dataStatus = 1 GROUP BY T.IoTID) T4
    ON T2.IoTID = T4.IoTID AND T2.time = T4.time
  INNER JOIN IoT T5 ON T3.IoTID = T5.IoTID
  INNER JOIN IoTType T6 ON T5.IoTTypeID = T6.IoTTypeID AND T6.type != "PB"
GROUP BY T2.IoTID, T2.time
"""
  get_started = default_ope.query(stmt, dictionary=True, prepared=True)
  get_started = { v['IoTID']: v['time'] for v in get_started }
  result = [ {
    "type": r["type"],
    "dormitory": r['dormitory'],
    "floor": r['floor'],
    "No": r['No'],
    "status": r["status"] if r['type'] == "PB" else bool(r['status']),
    "startedTime": get_started.get(r['IoTID'], None),
    "latestDataTime": r['time']
  } for r in res ]
  return result

 
@app.route('/api/transitions', methods=['GET'])
@catchError
def changes():
  reqargs = getRequest(request.args, ['id', 'dormitory', 'floor', 'type', 'weekday'], default=None)
  if reqargs is None:
    app.logger.info("Invalid request parameters 0")
    return HTTP_STAT(400)

  stime = request.args.get('startTime', None)
  etime = request.args.get('endTime', None)

  flags = {
    "monthly": request.args.get('monthly', None),
    "weekly": request.args.get('weekly', None),
    "halfYear": request.args.get('halfYear', None),
    "groupByDormitory": request.args.get('groupByDormitory', None),
    "groupByFloor": request.args.get('groupByFloor', None),
    "groupByID": request.args.get('groupByID', None)
  }

  if stime is not None and etime is not None:
    time_pattern = re.compile(r'\d{4}-[0-1]\d-\d{2}-[0-2]\d:[0-6]\d:[0-6]\d')
    if not time_pattern.fullmatch(stime):
      app.logger.info("Invalid request parameters A")
      return HTTP_STAT(400)
    else:
      stime = dt.strptime(stime, '%Y-%m-%d-%H:%M:%S')
    if not time_pattern.fullmatch(etime):
      if etime.upper() != "NOW":
        app.logger.info("Invalid request parameters B")
        return HTTP_STAT(400)
      etime = dt.now(pytz.timezone('Asia/Tokyo')).replace(tzinfo=None)
    else:
      etime = dt.strptime(etime, '%Y-%m-%d-%H:%M:%S')
  elif not (stime is None and etime is None):
      app.logger.info("Invalid request parameters C")
      return HTTP_STAT(400)

  for flk in flags:
    if flags[flk] is None:
      flags[flk] = False
    elif flags[flk].upper() == 'TRUE':
      flags[flk] = True
    else:
      app.logger.info("Invalid request parameters D")
      return HTTP_STAT(400)

  sub_stmt1 = ""
  sub_stmt2 = ""
  if flags["groupByID"]:
    sub_stmt1 = ", T4.dormitory, T3.floor, T2.No"
    sub_stmt2 = ", T0.dormitory, T0.floor, T0.No"
  elif flags["groupByFloor"]:
    sub_stmt1 = ", T4.dormitory, T3.floor"
    sub_stmt2 = ", T0.dormitory, T0.floor"
  elif flags["groupByDormitory"]:
    sub_stmt1 = ", T4.dormitory"
    sub_stmt2 = ", T0.dormitory"

  stmt = f"""
SELECT T0.sector, AVG(T0.value) AS value, T0.type{sub_stmt2}
FROM (
  SELECT T5.time, T5.sector, SUM(T5.value) AS value, T2.type{sub_stmt1}
  FROM
    IoT AS T1
    INNER JOIN IoTType AS T2
      ON T1.IoTTypeID = T2.IoTTypeID AND ( %(type)s IS NULL OR T2.type = %(type)s )
        AND ( %(id)s IS NULL OR T1.IoTID = %(id)s )
    LEFT OUTER JOIN dormitoryPlace AS T3
      ON T1.dormitoryPlaceID = T3.dormitoryPlaceID AND ( %(floor)s IS NULL OR T3.floor = %(floor)s )
    LEFT OUTER JOIN dormitory AS T4
      ON T3.dormitoryID = T4.dormitoryID AND ( %(dormitory)s IS NULL OR T4.dormitory = %(dormitory)s )
    LEFT OUTER JOIN parsedIoTData AS T5
      ON T5.IoTID = T1.IoTID AND T5.time >= %(stime)s AND T5.time < %(etime)s
        AND ( %(weekday)s IS NULL OR T5.week = %(weekday)s )
  GROUP BY T2.type, T5.time, T5.sector{sub_stmt1}
) AS T0
GROUP BY T0.type, T0.sector{sub_stmt2}
"""
  
  times = []
  now = dt.now(pytz.timezone('Asia/Tokyo')).replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
  if flags['weekly']:
    times.append([ now - timedelta(days=7), now, "一週間" ])
  if flags['monthly']:
    times.append([ now - timedelta(days=30), now, "1ヶ月" ])
  if flags['halfYear']:
    times.append([ now - timedelta(days=182), now, "半年" ])
  if stime is not None:
    times.append([ stime, etime, f"{stime} ~ {etime}" ])

  if not times:
    app.logger.info("Invalid request parameters E")
    return HTTP_STAT(400, 'No period set.')

  labels = [ str(timedelta(minutes=5) * i) for i in range(288) ]
  result = dict()
  for stime, etime, label in times:
    reqargs['stime'] = stime
    reqargs['etime'] = etime
    ope_result = default_ope.query(stmt, args=reqargs, dictionary=True, prepared=True)

    # Specify the grouping key
    groups = ["type", "dormitory", "floor", "No"]
    groups =  groups if flags["groupByID"] else\
              groups[:-1] if flags["groupByFloor"] else\
              groups[:-2] if flags["groupByDormitory"] else groups[:-3]

    for res in ope_result:
      k = ( res[key] for key in groups )
      if k not in result:
        result[k] = {"data": { "datasets": [], "labels": labels }}
        for g in ("type", "dormitory", "floor", "No"):
          result[k][g] = res.get(g, None)

      i = next( ( i for i, l in enumerate(result[k]["data"]["datasets"]) if l == label), None )

      if i is None:
        result[k]["data"]["datasets"].append({"data": [None] * 288, "label": label})
        i = len(result[k]["data"]["datasets"]) - 1

      result[k]["data"]["datasets"][i]["data"][res["sector"]] = res["value"]
# 時間設定ない場合エラー、データが存在しない場合nullにして送る

  result = [ v for v in result.values() ]
  return jsonify(result), 200


