from application import app
from application.page import catchError, HTTP_STAT
from application.exception import RequestKeyError
from application.DBcontrol import (
  default_ope,
  JOIN,
  getVal,
  selectsql,
  insertvalsql,
  insertselectsql,
  getStIds,
  getClData,
  getClId,
  setCleaningStat
)
from flask import request, jsonify
import json
import re

def _get_cleaning_args(j, default_remove=True):
  res = {'clId': j.get('cleaningID', None)}
  res['clType'] = j.get('cleanType', None)
  res['date'] = j.get('date', None)
  res['times'] = j.get('cleanTimes', None)
  if res['clType'] == 'weekly':
    res['dormitory'] = j.get('dormitory', None)
    res['floor'] = j.get('floor', None)
  else:
    res['dormitory'] = None
    res['floor'] = None
  if not res:
    raise RequestKeyError('_get_cleaning_args')
  return { k:v for (k, v) in res.items() if v is not None } if default_remove else res

def _manage_getarg(getarg):
  args = _get_cleaning_args(request.json)

  if getarg >= 0:
    _col = [
      ['cleaningType.cleaningType', 'cleanType'],
      ['cleaning.year_month', 'date'],
      ['cleaning.times', 'cleanTimes'],
      ['dormitory.dormitory', 'dormitory'],
      ['dormitoryPlace.floor', 'floor'],
      ['cleaningStatus.cleaningStatus', 'status'],
      ['cleaning.place', 'place']
    ]
    if getarg >= 1:
      _col.extend([
        ['studentReport.report', 'studentReport'],
        ['studentReport.studentID', 'registerdStudent'],
        ['studentReport.reportedTime', 'registerdTimeSt'],
        ['teacherReport.report', 'teacherReport'],
        ['teacher.name', 'registerdTeacher'],
        ['teacherReport.reportedTime', 'registerdTimeTe']
      ])
  else:
    return HTTP_STAT(500)

  col = getVal(*_col ,p_c='as')

  select_col, tables, conds, arg = getClData(col, get_response=False, **args)

  def _get_on(c1, c2, s):
    return formulacond(c1.getCol(s), c2.getCol(s), '=')

  _stcol = getVal(
    ['student.grade', 'stSt', 'stGr'], ['courses.course', 'couSt', 'stCo'], ['student.name', 'stSt', 'stNa'],
    ['student.grade', 'stAg', 'agGr'], ['courses.course', 'couAg', 'agCo'], ['student.name', 'stAg', 'agNa'],
    t='as_ch_column')
  select_col.extend(_stcol)
  _nt = getVal(['cleaningDuty', 'clDt'], ['cleaningDutyAgent', 'clDA'], ['student', 'stSt'], ['courses', 'couSt'], ['student', 'stAg'], ['courses', 'couAg'], t='as_table')
  _on = [_get_on(*a) for a in ([_nt[2], _nt[0], 'studentID'], [_nt[3], _nt[2], 'courseID'], [_nt[4], _nt[1], 'studentID'], [_nt[5], _nt[4], 'courseID'])]
  tables.extend([[_nt[0], JOIN.NATURAL_LEFT_OUTER], [_nt[1], JOIN.NATURAL_LEFT_OUTER]])
  tables.extend([ [_nt[i+2], JOIN.LEFT_OUTER, _on[i]] for i in range(len(_on)) ])

  stmt = selectsql(select_col, tables, conds)
  
  res = default_ope.query(str(stmt), args=arg, prepared=True, dictionary=True)
  def _response_data(res):
    ret = { k: v for (k, v) in res.items() if k not in ('stCo', 'stGr', 'stNa', 'agGr', 'agCo', 'agNa')}
    ret['student'] = f"{res['stGr']}{res['stCo']}{res['stNa']}" if res['stGr'] is not None else None
    if 'agGr' in res.keys(): ret['agent'] = f"{res['agGr']}{res['agCo']}{res['agNa']}" if res['agGr'] is not None else None
    return ret

  res = list(map(_response_data, res))
  return res[0] if len(res) == 1 else res

@app.route('/api/manage/getcleaningid/<cltype>', methods=['POST'])
@catchError(req_json=True)
def manage_getcleaningid(cltype):
  args = _get_cleaning_args(request.json)

  if cltype in ['weekly', 'monthly']:
    res = getClData(getVal(['cleaning.cleaningID', 'celaningId'], p_c='as', l=True), **args)
    if not res: return HTTP_STAT(400)
    return jsonify(res[0] if len(res) == 1 else res)
  elif cltype == 'special':
    res = getClData(getVal(['cleaning.cleaningID', 'celaningId'], ['cleaning.place', 'place'], p_c='as', l=True), **args)
    if not res: return HTTP_STAT(400)
    return jsonify({'data': res[0] if len(res) == 1 else res}), 200
  else: return HTTP_STAT(404)

@app.route('/api/manage/cleaningstatus/', methods=['POST'])
@catchError(req_json=True)
def manage_cleaningstatus():
  args = _get_cleaning_args(request.json)
  res = getClData(getVal(['cleaning.status', 'cleaningStatus'], p_c='as', l=True), **args)
  if not res: return HTTP_STAT(400)
  return jsonify(res[0] if len(res) == 1 else res)


@app.route('/api/manage/cleaningstudent/', methods=['POST'])
@catchError(req_json=True)
def manage_cleaningstudent():
  return jsonify(_manage_getarg(0))

@app.route('/api/manage/cleaninginformation/', methods=['POST'])
@catchError(req_json=True)
def manage_cleaninginfomation():
  return jsonify(_manage_getarg(1))


@app.route('/api/manage/cleaningreport', methods=['POST'])
@catchError(req_json=True)
def manage_cleaningreport():
  getDict = lambda d, k: d.get(k, k)
  clDA_args = []
  stNames = []

  def _getst(st):
    cldtargs = {'stId': st['student'], 'clst': st['cleaningStatus']}
    stNames.append(cldtargs['stId'])
    if st['agent'] is not None:
      clDA_args.append({'astId': st['agent'], 'stId': cldtargs['stId']})
      stNames.append(st['agent'])
    return cldtargs

  cl_args = _get_cleaning_args(request.json)
  clD_args = list(map(_getst, getReqJson('studentStatus')))
  stNames = getStIds(*stNames)
  args_bace = {'rstId': getDict(stNames, getReqJson('registerdStudent'))}
  rep_args = {'rep': json.dumps(getReqJson('cleanReport'))}

  clId = getClId(**cl_args)
  if len(clId) != 1: return HTTP_STAT(400)

  # set statement
  args_bace['clId'] = clId[0]['cleaningID']
  rep_args['clId'].update(args_bace)
  [ c.update(stId=getDict(stNames, c['stId']), **args_bace) for c in clD_args ]
  [ c.update( clId=args_bace['clId'], stId=getDict(stNames, c['stId']), astId=getDict(stNames, c['astId'])) for c in clDA_args ]
  
  #insert to studentReport
  clR_stmt = insertvalsql(['cleaningID', 'studentID', 'report'], 'studentReport', ['clId', 'rstId', 'rep'])
  clR_stmt.setIsUpdate(True)
  default_ope.query(str(clR_stmt), commit=False, args=rep_args, prepared=True)

  #update or insert to cleaningDuty
  sel_col = getVal('clId', 'stId', 'cleaningStatus.cleaningStatusID', 'rstId', p_t='arg')
  select = selectsql(sel_col, ['cleaningStatus'], [['cleaningStatus.cleaningStatus', 'clst', '=']])
  clD_stmt = insertselectsql(['cleaningID', 'studentID', 'cleaningStatusID', 'registeredStudentID'], 'cleaningDuty', select)
  clD_stmt.setIsUpdate(True)

  default_ope.query(clD_stmt, commit=False, many=True, args=clD_args, prepared=True)

  #insert to cleaningDutyAgent
  if clDA_args:
    sel_wh = [['cleaningDuty.cleaningID', 'clId', '='], ['cleaningDuty.studentID', 'stId', '=']]
    select = selectsql(['cleaningDuty.cleaningDutyID', 'astId'],[ 'cleaningDuty'], sel_wh)
    clDA_stmt = insertselectsql(['cleaningDutyID', 'studentID'], 'cleaningDutyAgent', select)
    clDA_stmt.setIsUpdate(True)

    default_ope.query(clDA_stmt, commit=False, many=True, args=clDA_args, prepared=True)

  default_ope.commit()
  return HTTP_STAT(200)


@app.route('/api/manage/teachercleaningreport', methods=['POST'])
@catchError(req_json=True)
def manage_teachercleaningreport():
  cl_args = _get_cleaning_args(request.json)
  tR_args = {'rep': json.dumps(getReqJson('cleanReport')), 'tr': getReqJson('registerdTeacher')}

  tR_args['clId'] = getClId(only=True, **cl_args)
  tR_stmt = [['cleaningID', 'teacherID', 'report'], 'teacherReport']
  tR_stmt = insertval(*tR_stmt, ['clId', 'tr', 'rep']) if re.fullmatch('\d+', tR_args['tr']) else \
            insertselect(*tR_stmt, [['clId', 'teacher.teacherID', 'rep'], ['teacher'], ['teacher.name', 'tr']])

  tR_stmt.setIsUpdate(True)
  default_ope.query(tR_stmt, commit=True, many=False, args=tR_args, prepared=True)

  setCleaningStat(3, tR_args['clId'], ope=default_ope)
  return HTTP_STAT(200)

@app.route('/api/manage/reportread/', methods=['POST'])
@catchError(req_json=True)
def manage_reported():
  cl_args = _get_cleaning_args(request.json)
  clId = getClId(only=True, **cl_args)
  setCleaningStat(2, clId, ope=default_ope)
  return HTTP_STAT(200)

# cleaningreportと一部が同じ
@app.route('/api/manage/monthlyattend/', methods=['POST'])
@catchError(req_json=True)
def manage_monthlyattend():
  clDA_args = []
  stNames = []

  def _getst(st):
    cldtargs = {'stId': st['student'], 'clst': st['status']}
    stNames.append(cldtargs['stId'])
    if st['agent'] is not None:
      clDA_args.append({'astId': st['agent'], 'stId': cldtargs['stId']})
      stNames.append(st['agent'])
    return cldtargs

  cl_args = _get_cleaning_args(request.json)
  clD_args = list(map(_getst, getReqJson('studentStatus')))
  stNames = getStIds(*stNames)
 
  # set statement
  clId = getClId(only=True, **cl_args)
  [ c.update(stId=getDict(stNames, c['stId']), rstId=getDict(stNames, c['stId']), clId=clId) for c in clD_args ]
  [ c.update( clId=clId, stId=getDict(stNames, c['stId']), astId=getDict(stNames, c['astId'])) for c in clDA_args ]

   #update or insert to cleaningDuty
  sel_col = getVal('clId', 'stId', 'cleaningStatus.cleaningStatusID', 'rstId', p_t='arg')
  select = selectsql(sel_col, ['cleaningStatus'], [['cleaningStatus.cleaningStatus', 'clst', '=']])
  clD_stmt = insertselectsql(['cleaningID', 'studentID', 'cleaningStatusID', 'registeredStudentID'], 'cleaningDuty', select)
  clD_stmt.setIsUpdate(True)

  default_ope.query(clD_stmt, commit=False, many=True, args=clD_args, prepared=True)

  #insert to cleaningDutyAgent
  if clDA_args:
    sel_wh = [['cleaningDuty.cleaningID', 'clId', '='], ['cleaningDuty.studentID', 'stId', '=']]
    select = selectsql(['cleaningDuty.cleaningDutyID', 'astId'],[ 'cleaningDuty'], sel_wh)
    clDA_stmt = insertselectsql(['cleaningDutyID', 'studentID'], 'cleaningDutyAgent', select)
    clDA_stmt.setIsUpdate(True)

    default_ope.query(clDA_stmt, commit=False, many=True, args=clDA_args, prepared=True)

  default_ope.commit()
  return HTTP_STAT(200)

@app.route('/api/manage/getstudentdata/', methods=['POST'])
@catchError(req_json=True)
def manage_getstudentdata():
  dormitory = getReqJson('dormitory')

  stmt = '''
  SELECT CONCAT(CONVERT(T0.grade, CHAR(1)), T4.course, T0.name), T2.floor
  FROM(
    `student` AS T0
    NATURAL INNER JOIN `dormitoryBelong` AS T1
    NATURAL INNER JOIN `dormitoryPlace` AS T2
    NATURAL INNER JOIN `dormitory` AS T3
    NATURAL INNER JOIN `courses` AS T4
  ) WHERE T3.dormitory=%(dorm)s;
  '''
  res = default_ope.query(stmt, commit=False, args={'dorm': dormitory}, many=False, prepared=True)
  ret = {
    "studentData":{
      "f1": [ s[0] for s in res if s[1] == 1 ],
      "f2": [ s[0] for s in res if s[1] == 2 ],
      "f3": [ s[0] for s in res if s[1] == 3 ],
      "f4": [ s[0] for s in res if s[1] == 4 ],
      "f5": [ s[0] for s in res if s[1] == 5 ]
    }
  }
  return jsonify(ret), 200


