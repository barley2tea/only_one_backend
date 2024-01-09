from .cleateSQL import *
from . import default_ope
import re
from functools import reduce
stNPattern = re.compile(r'([12345])(EM|AC|[MEIAC])(.*)')

# f"{grade}{couse}{name}" -> [grade, couse, name]
def stData(stD, d=False):
  m = stNPattern.fullmatch(stD)
  if not m: return {'grade': None, 'course': None, 'name': None} if d else None
  return  { 'grade':m.group(1), 'course': m.group(2), 'name': m.group(3) } if d else \
          (int(m.group(1)), m.group(2), m.group(3))

# studentID -> f"{grade}{course}{name}", list or dict
def getStudentName(studentId, ope=default_ope, d=False, j=False):
  t = sqltable('student', ['courses', JOIN.NATURAL_INNER])
  w = sqlcond(['student.studentID', 'stId', '='])
  cols = get_val(['student.grade', 'grade'], ['courses.course', 'course'], ['student.name', 'name'], t='as_column')
  stmt = selectsql(cols, t, w)
  res = ope.query(str(stmt), args={'stId':studentId}, prepared=True, dictionary=d)
  if len(res) != 1: return {'grade': None, 'course': None, 'name': None} if d else None
  else:             return f'{res[0][0]}{res[0][1]}{res[0][2]}' if not d and j else res[0]

# {grade}{course}{name} -> studentID
def getStudentId(grade, course=None, name=None, ope=default_ope):
  if None in [course, name]:
    args = stData(grade, d=True)
    if None in args.values(): raise ValueError(f'{grade}, {course}, {name}')
  else:                       args = {'grade': grade, 'course': course, 'name': name}

  t = sqltable('student', ['courses', JOIN.NATURAL_INNER])
  w = sqlcond(['student.grade', 'grade', '='], ['courses.course', 'course', '=', CONNECT.AND], ['student.name', 'name', '=', CONNECT.AND])
  stmt = selectsql(['student.studentID'], t, w)
  res = ope.query(str(stmt), commit=False, args=args, prepared=True)
  return None if len(res) != 1 else res[0][0]

def cleaningSql(select_col, ope=default_ope, **kwargs):
  COL_LIST = {'cltype': 'cleaningType.cleaningType', 'date': 'cleanig.year_month', 'times': 'cleaning.times'}
  conds = sqlcond()
  tables = sqltable('cleaning')
  args = {}
  if type(select_col) not in [list, tuple]: select_col = [select_col]

  _aslist = []
  def select_col_as(col):
    if not isinstance(col, AS_COLUMN):
      name = col.name if isinstance(col, COLUMN) else col
      as_name = name.split('.')[1]
      col = get_val([col, as_name], t='as_column')
    _aslist.append(col.as_name)
    return col

  select_col = list(map(select_col_as, select_col))

  def append_tables(key, col, join=JOIN.NATURAL_INNER, on=None, cond_connect='and'):
    if col is None:
      # print('not setting', key) # debug
      return
    _table = get_val(col.split('.')[0], t='table')
    if _table.name not in tables.getTableNameList(ch=False): tables.append([_table, join, on])
    conds.append((col, key, '=', cond_connect))
    args[key] = kwargs[key]

  if 'clid' in kwargs.keys():
    append_tables('clid', 'cleaing.cleaningID')
  else:
    [ append_tables(k, COL_LIST.get(k, None)) for k in kwargs.keys() ]

    if 'dorm' in kwargs.keys():
      if 'floor' in kwargs.keys():  append_tables('floor', 'dormitoryPlace.floor')
      else:                         tables.append(get_val('dormitoryPlace', t='table'))
      append_tables('dorm', 'dormitory.dormitory')
    elif 'floor' in kwargs.keys():
      append_tables('floor', 'dormitoryPlace.floor')
    
  add_table = reduce(lambda a, x: a | {x.get_table().name}, select_col, set()) - set(tables.getTableNameList(ch=False))

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




