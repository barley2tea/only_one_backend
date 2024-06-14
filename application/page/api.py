from application import app, bcrypt
from application.page import catchError, HTTP_STAT
from application.page.prosses import IotProssesing
from application.DBcontrol import (
  MysqlOperator,
  default_ope,
  stData,
  getStName,
  getStId,
  getStData,
  getClData,
  getVal,
  selectsql,
  sqltable,
  sqlcond,
  insertvalsql,
  insertselectsql
)
from flask import request, jsonify, abort, session, send_file
import re
import json

# PROPOSAL
# Collect variables into a buffer and INSERT them periodically in application.bot.
# ---------
# Insert IoTData
@app.route("/", methods=['POST'])
@catchError
def root():
  remote_addr = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
  stmt = 'SELECT T.sendIoTDevicesID FROM sendIoTDevices AS T WHERE T.IP = %(IP)s;'
  IoT_id = default_ope.query(str(stmt), args={'IP': str(remote_addr)}, prepared=True)

  if len(IoT_id) != 1:
    if not IoT_id:
      app.logger.info(f'Unauthorized access. ID:IPaddr[{remote_addr}]')
      return HTTP_STAT(403)
    else:
      app.logger.error('Duplicate ID:addr[{remote_addr}], ID{str(IoT_id)}')
      return HTTP_STAT(500)

  IoT_id = IoT_id[0][0]
  request_data = request.get_data() if request.json is None else request.json
  stat = IotProssesing(IoT_id, request_data)
  if isinstance(stat, int):
    args = {'ID': IoT_id, 'stat': stat}
    many = False
  else:
    args = stat
    many = True
  table = getVal('IoTData', t='table')
  stmt = insertvalsql(table.getCol('IoTID', 'dataStatus'), table, ['ID', 'stat'])

  default_ope.query(stmt, commit=True, args=args, many=many, prepared=True)
  app.logger.debug(f'data: "{"bytes" if len(request_data) > 100 else request_data}" stat:"{args}"')
  return jsonify({'stat': 'success', 'data': stat}), 200

# Set student password
@app.route("/api/register", methods=["POST"])
@catchError
def register_user():
  try:
    stId = request.json["studentId"]
    password = request.json["password"]
  except (TypeError, KeyError) as e:
    app.logger.debug('request json error: "{request.get_data()}"')
    return HTTP_STAT(400)
  res = getStName(stId)
  if res is None: return HTTP_STAT(400)
  args = { 'pass': bcrypt.generate_password_hash(password), 'stID': stId }
  default_ope.query('UPDATE student SET pass=%(pass)s WHERE studentID=%(stID)s;', commit=True, args=args, prepared=True)
  session["studentId"] = stId
  app.logger.info(f"setting password of '{stId}'")
  return jsonify({"studentId": stId}), 200

# login and add session['studentId']
@app.route("/api/login", methods=['POST'])
@catchError
def login():
  try:
    stId = request.json["studentId"]
    password = request.json["password"]
  except (TypeError, KeyError) as e:
    app.logger.debug('request json error: "{request.get_data()}"')
    return HTTP_STAT(400)

  res = getStData(['student.pass', 'student.grade', 'courses.course', 'student.name'], stId=stId)
  if not res: return HTTP_STAT(401)
  res = res[0]
  if not bcrypt.check_password_hash(res['pass'], password): return HTTP_STAT(401)

  session["studentId"] = stId
  account = f"{res['grade']}{res['course']}{res['name']}"
  app.logger.info("login of '{stId}'")
  return jsonify({"studentId": stId, "account": account})

# remove session['studentId']
@app.route('/api/logout', methods=["POST"])
def logout_user():
  stId = session.get('studentId', False)
  if stId: session.pop("studentId")
  app.logger.debug('logout of "{stId}"')
  return HTTP_STAT(200)

# check aleady login
@app.route('/api/@me', methods=['GET', 'POST'])
@catchError
def get_current_user():
  stId = session.get('studentId', None)
  if stId is None:  return HTTP_STAT(401)
  return jsonify({"studentId": studentId, "account": getStName(stId)})

# get latest dashboard data
@app.route('/api/dashboard', methods=['GET'])
@catchError
def dashboad():
  stmt = " SELECT T1.IoTID, T1.dataStatus FROM ( `IoTData` AS T1 NATURAL INNER JOIN ( SELECT T3.IoTID, MAX(T3.time) AS 'time' FROM `IoTData` AS T3 GROUP BY T3.IoTID) AS T2);"
  res = default_ope.query(stmt, dictionary=True)

  def getdata(purpos, place):
    if purpos == 'PB':
      return list(map(lambda x: x['dataStatus'], filter(lambda x: x['IoTID'][:2] == purpos, res)))
    ret = (list(filter(lambda x: x['IoTID'][:4] == f'{purpos}_{place}', res)))
    ret.sort(key=lambda x: int(x['IoTID'][4:]))
    return list(map(lambda x: bool(x['dataStatus']), ret))

  dashboard = {
      "yamaWasherData"    : getdata('WA', 2),
      "umiWasherData"     : getdata('WA', 3),
      "yamaDryerData"     : getdata('DR', 2),
      "umiDryerData"      : getdata('DR', 3),
      "yamaShowerData"    : getdata('SW', 2),
      "umiShowerData"     : getdata('SW', 3),
      "numberOfUsingBathData" : getdata('PB', None)
  }

  return jsonify(dashboard)

# insert rollcall
@app.route('/api/rollcall', methods=['POST'])
@catchError
def add_rollcall():
  try:
    dormitory = request.json['dormitory']
    year_month = request.json['date']
    rSt = request.json['register']
    tableData = request.json['tableData']
  except (KeyError, TypeError) as e:
    return HTTP_STAT(400)

  rStID = getStudentID(default_ope, rSt)
  args = [
    { 'date': f'{year_month}-{td["day"]}',
      'rStID': rStID,
      'dorm': dormitory,
      **stData(td['account'], d=True)
    } for td in tableData
  ]
  seltab = sqltable('dormitory', ['student', JOIN.CROSS], ['courses', JOIN.NATURAL_INNER])
  selwhe = sqlcond(['dormitory.dormitory', 'dorm'], ['student.grade', 'grade'], ['courses.course', 'course'], ['student.name', 'name'])
  select = selectsql(['dormitory.dormitoryID', 'student.studentID', 'date', 'rStID'], seltab, selwhe)
  stmt = insertselectsql(['dormitoryID', 'studentID', 'day', 'registeredStudentID'], 'rollCall', select)
  stmt = str(stmt).replace('%(date)s', "STR_TO_DATE(%(date)s, '%Y-%m-%d')")

  default_ope.query(stmt, commit=True, args=args, many=True, prepared=True)
  app.logger.info('add rollcall table: register:"{rStID}"')
  return HTTP_STAT(200)

# insert cleaning
@app.route('/api/cleaning', methods=['POST'])
@catchError
def add_cleaning():
  try:
    rSt = request.json['register']
    year_month = request.json['date']
    dormitory = request.json['dormitory']
    wCTD = request.json['weeklyCleaningTableData']
    mCTD = request.json['monthlyCleaningTableData']
    rStID = getStudentID(default_ope, rSt)
  except KeyError as e:
    return HTTP_STAT(400)

  wtargs = []
  wdtargs = []
  for wt in wCTD:
    for i in wt['studentAccounts']:
      b_d = { 'place': f'{dormitory}_{i[1:]}', 'y_m': year_month, 'times': int(wt['times']), 'clType': 'weekly' }
      d = b_d.copy()
      d.update(day=int(wt['day']))
      dd = b_d.copy()
      dd.update(rStID=rStID)
      wtargs.append(d)
      for j in wt['studentAccounts'][i]:
        ddd = dd.copy()
        ddd.update(**studentData(j, d=True))
        wdtargs.append(ddd)

  mtargs = []
  mdtargs = []
  for mt in mCTD:
    d_b = {'y_m': year_month, 'day': int(mt['day']), 'clType': 'monthly'}
    mta_d = d_b.copy()
    mta_d.update(place=mt['place'])
    mdta_d = d_b.copy()
    mdta_d.update(rStID=rStID)
    mtargs.append(mta_d)
    for st in mt['accounts']:
      mdta_d_add = mdta_d.copy()
      mdta_d_add.update(**studentData(st, d=True))
      mdtargs.append(mdta_d_add)

  select = selectsql(['cleaningType.cleaningTypeID', 'place', 'y_m', 'day', 'times'], 'cleaningType', ['cleaningType.cleaningType', 'clType'])
  INSERT_CLEANING = insertselectsql(['cleaningTypeID', 'place', 'year_month', 'day', 'times'], 'cleaning', select)

  INSERT_CLEANING_MONTHLY = '''
INSERT INTO `cleaning`(`cleaningTypeID`, `place`, `year_month`, `day`, `times`)
SELECT T1.cleaningTypeID, %(place)s, %(y_m)s, %(day)s,
CASE
	WHEN NOT EXISTS( SELECT * FROM `cleaning` AS T WHERE T.cleaningTypeID=2 AND T.year_month=%(y_m)s AND T.times=1) THEN 1
	WHEN NOT EXISTS( SELECT * FROM `cleaning` AS T WHERE T.cleaningTypeID=2 AND T.year_month=%(y_m)s AND T.times=2) THEN 2
	ELSE 3
END
FROM `cleaningType` AS T1
WHERE T1.cleaningType='monthly' AND NOT EXISTS(SELECT * FROM `cleaning` AS T WHERE T.year_month=%(y_m)s AND T.day=%(day)s);
'''

  sqlt = sqltable('cleaning', ['cleaningType', JOIN.NATURAL_INNER], ['student', JOIN.CROSS], ['courses', JOIN.NATURAL_INNER])
  scond = [['cleaning.year_month', 'y_m'], ['cleaningType.cleaningType', 'clType'], ['student.grade', 'grade'], ['courses.course', 'course'], ['student.name', 'name']]
  wcond = sqlcond(*scond, ['cleaning.place', 'place'], ['cleaning.times', 'times'])
  wselect = selectsql(['student.studentID', 'cleaning.cleaningID', 'rStID'], sqlt, wcond)
  mcond = sqlcond(*scond, ['cleaning.day', 'day'])
  mselect = selectsql(['student.studentID', 'cleaning.cleaningID', 'rStID'], sqlt, mcond)
  insert = [['studentID', 'cleaningID', 'registeredStudentID'], 'cleaningDuty']

  INSERT_CLEANING_DUTY = insertselectsql(*insert, wselect)
  INSERT_CLEANING_DUTY_MONTHLY = insertselectsql(*insert, mselect)

  default_ope.query(INSERT_CLEANING, commit=False, args=wtargs, many=True, prepared=True)
  default_ope.query(INSERT_CLEANING_MONTHLY, commit=False, args=mtargs, many=True, prepared=True)
  default_ope.query(INSERT_CLEANING_DUTY, commit=False, args=wdtargs, many=True, prepared=True)
  default_ope.query(INSERT_CLEANING_DUTY_MONTHLY, commit=True, args=mdtargs, many=True, prepared=True)
  # if these query fails, it will be rollback

  app.logger.info('add cleaning table: register:"{rStID}"')
  return HTTP_STAT(200)



