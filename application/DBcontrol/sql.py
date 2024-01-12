from .cleateSQL import *
from . import default_ope
import re
from functools import reduce
COL_LIST = {
  'grade':  'student.grade',
  'course': 'courses.course',
  'name':   'student.name',
  'stId':   'student.studentID',
  'dorm':   'dormitory.dormitory',
  'floor':  'dormitoryPlace.floor',
  'stStat': 'studentStatus.studentStatus',
  'clId':   'cleaningType.cleaningID',
  'clType': 'cleaningType.cleaningType',
  'times':  'cleaning.times',
  'date':   'cleaning.year_month',
  'day':    'cleaning.day',
  'clStat': 'cleaning.status'
}
stNPattern = re.compile(r'([12345])(EM|AC|[MEIAC])(.*)')

# f"{grade}{couse}{name}" -> [grade, couse, name]
def stData(stD, d=False):
  m = stNPattern.fullmatch(stD)
  if not m: return {'grade': None, 'course': None, 'name': None} if d else None
  return  { 'grade':m.group(1), 'course': m.group(2), 'name': m.group(3) } if d else \
          (int(m.group(1)), m.group(2), m.group(3))

# studentID -> f"{grade}{course}{name}", list or dict
def getStName(studentId, ope=default_ope, d=False, j=False):
  t = sqltable('student', ['courses', JOIN.NATURAL_INNER])
  w = sqlcond(['student.studentID', 'stId', '='])
  cols = getVal(['student.grade', 'grade'], ['courses.course', 'course'], ['student.name', 'name'], t='as_column')
  stmt = selectsql(cols, t, w)
  res = ope.query(str(stmt), args={'stId':studentId}, prepared=True, dictionary=d)
  if len(res) != 1: return {'grade': None, 'course': None, 'name': None} if d else None
  else:             return f'{res[0][0]}{res[0][1]}{res[0][2]}' if not d and j else res[0]

# {grade}{course}{name} -> studentID
def getStId(grade, course=None, name=None, ope=default_ope):
  if None in [course, name]:
    args = stData(grade, d=True)
    if None in args.values(): raise ValueError(f'{grade}, {course}, {name}')
  else:                       args = {'grade': grade, 'course': course, 'name': name}

  t = sqltable('student', ['courses', JOIN.NATURAL_INNER])
  w = sqlcond(['student.grade', 'grade', '='], ['courses.course', 'course', '=', CONNECT.AND], ['student.name', 'name', '=', CONNECT.AND])
  stmt = selectsql(['student.studentID'], t, w)
  res = ope.query(str(stmt), commit=False, args=args, prepared=True)
  return None if len(res) != 1 else res[0][0]

def _select_col_as(col, key_is_colname):
  if not isinstance(col, AS_COLUMN):
    name = col.name if isinstance(col, COLUMN) else col
    as_name = [k for k, v in COL_LIST.items() if v == name] if key_is_colname else []
    if not as_name: as_name = [name.split('.')[1]]
    col = getVal([name, as_name[0]], t='as_column')
  return col

def getStData(select_col, ope=default_ope, key_is_colname=True, dictionaly=True, **kwargs):
  conds = sqlcond()
  tables = sqltable('student', ['dormitoryBelong', JOIN.NATURAL_INNER, None])
  args = {}
  if type(select_col) not in [list, tuple]: select_col = [select_col]

  select_col = list(map(lambda x: _select_col_as(x, key_is_colname), select_col))

  def append_tables(key, col, join=JOIN.NATURAL_INNER, on=None, cond_connect='and'):
    if col is None: return
    _table = getVal(col.split('.')[0], t='table')
    if _table.name not in tables.getTableNameList(ch=False): tables.append([_table, join, on])
    conds.append((col, key, '=', cond_connect))
    args[key] = kwargs[key]

  if 'stId' in kwargs.keys():
    append_tables('stId', COL_LIST('stId'))
  else:
    [ append_tables(k, COL_LIST.get(k, None)) for k in kwargs.keys() ]

    if 'dorm' in kwargs.keys():
      tables.append(getVal('dormitoryBelong', t='table'))
      if 'floor' in kwargs.keys():  append_tables('floor', 'dormitoryPlace.floor')
      else:                         tables.append(['dormitoryPlace', JOIN.NATURAL_INNER, None])
      append_tables('dorm', 'dormitory.dormitory')
    elif 'floor' in kwargs.keys():
      append_tables('floor', 'dormitoryPlace.floor')
    
  add_table = reduce(lambda a, x: a | {x.getTable().name}, select_col, set()) - set(tables.getTableNameList(ch=False))
  if 'dormitory' in add_table and 'dormitoryPlace' not in tables.getTableNameList(ch=False):
    tables.append(['dormitoryPlace', JOIN.NATURAL_LEFT_OUTER, None])
    add_table.discard('dormitoryPlace')

  for t in add_table:
    tables.append([t, JOIN.NATURAL_LEFT_OUTER, None])

  stmt = selectsql(select_col, tables, conds)
  # print(stmt)
  res = ope.query(str(stmt), commit=False, args=args, prepared=True, dictionary=True)
  return res


def getClData(select_col, ope=default_ope, key_is_colname=True, **kwargs):
  conds = sqlcond()
  tables = sqltable('cleaning')
  args = {}
  if type(select_col) not in [list, tuple]: select_col = [select_col]

  select_col = list(map(lambda x: _select_col_as(x, key_is_colname), select_col))

  def append_tables(key, col, join=JOIN.NATURAL_INNER, on=None, cond_connect='and'):
    if col is None:
      # print('not setting', key) # debug
      return
    _table = getVal(col.split('.')[0], t='table')
    if _table.name not in tables.getTableNameList(ch=False): tables.append([_table, join, on])
    conds.append((col, key, '=', cond_connect))
    args[key] = kwargs[key]

  if 'clId' in kwargs.keys():
    append_tables('clId', 'cleaing.cleaningID')
  else:
    [ append_tables(k, COL_LIST.get(k, None)) for k in kwargs.keys() ]

    if 'dorm' in kwargs.keys():
      if 'floor' in kwargs.keys():  append_tables('floor', 'dormitoryPlace.floor')
      else:                         tables.append(getVal('dormitoryPlace', t='table'))
      append_tables('dorm', 'dormitory.dormitory')
    elif 'floor' in kwargs.keys():
      append_tables('floor', 'dormitoryPlace.floor')
    
  add_table = reduce(lambda a, x: a | {x.getTable().name}, select_col, set()) - set(tables.getTableNameList(ch=False))

  if 'dormitory' in add_table and 'dormitoryPlace' not in tables.getTableNameList(ch=False):
    tables.append(['dormitoryPlace', JOIN.NATURAL_LEFT_OUTER, None])
    add_table.discard('dormitoryPlace')
  if 'teacher' in add_table and 'teacherReport' not in tables.getTableNameList(ch=False):
    tables.append(['teacherReport', JOIN.NATURAL_LEFT_OUTER, None])
    add_table.discard('teacherReport')

  for t in add_table:
    tables.append([t, JOIN.NATURAL_LEFT_OUTER, None])

  stmt = selectsql(select_col, tables, conds)
  # print(stmt)
  res = ope.query(str(stmt), commit=False, args=args, prepared=True, dictionary=True)
  return res




