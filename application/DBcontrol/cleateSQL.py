# from .sql_dataclass import *
from sql_dataclass import *
from dataclasses import dataclass, field
from functools import reduce
import re

# ------------------conditions------------------

# This is the bace for class sql conditions
@dataclass
class BaceConditions:
  vals: list[VALUE] # COLUMN or ARGUMENT

  def __post_init__(self):
    for i in vals:
      if not isinstance(i, COLUMN) and  not isinstance(i, ARGUMENT):
        raise ValueError(f'{type(i)}')

# Conditions that can be specified in the formula
# e.g table.column=%(arg)s
@dataclass
class FormulaConditions(BaceConditions):
  formula: FORMULA

  def __post_init__(self):
    isformula(self.formula)
    if len(self.vals) != 2:
      raise ValueError(f'vals len must be 2')
    super().__post_init__()

  def __str__(self):
    return f'{str(self.vals[0].name)}{self.formula}{str(self.vals[1].name)}'

#-----------------------------------------------

@dataclass
class ConnectConditions:
  cond: BaceConditions
  connect: CONNECT

  def __post_init__(self):
    isconnect(self.connect)
  
  def __str__(self):
    return f' {connect2str(self.connect)} {str(self.cond)}'

@dataclass
class SQLConditions:
  bace_cond: BaceConditions
  connect_conds: list[ConnectConditions]

  def __post_init__(self):
    if self.bace_cond is None:
      self.bace_cond = 1
      self.tables = set()
    elif not isinstance(self.bace_cond, Conditions):
      raise ValueError(f"{type(self.bace_cond)}")
    if any([ not isinstance(i, ConnectConditions) for i in self.connect_conds ]):
      raise ValueError(f"{self.connect_conds}")

  def __str__(self):
    return reduce(lambda a, x: f'{a}{str(x)}', self.connect_conds, str(self.bace_cond))

  def append(self, cond, condfunc='formula'):
    if not isinstance(cond, ConnectConditions):
      cond = conncond(*cond, condfunc=condfunc)
    self.connect_conds.append(con)

  def expand(self, cons, cond_type='formula'):
    [ self.append(con, cond_type) for con in cons ]

  def connect(self, val, contype):
    self.append([val.bace_cond, contype])
    self.expand(val.connect_conds)

# ---------------------table--------------------

@dataclass
class ConnectTable:
  table: TABLE
  join_type: JOIN
  on: SQLConditions
  def __post_init__(self):
    isjoinon(self.join_type, self.on)
    isvalue(self.table, t='as_table')
 
  def __str__(self):
    s = f'{join2str(self.join_type)} {str(self.table)}'
    return  s if self.on is None else f'{s} ON {str(self.on)}'

@dataclass
class SQLTable:
  bace_table: AS_TABLE
  connect_tables: list[ConnectTable]
  # as_dict: dict = field(init=False, default_factory=dict)#いらんくね？
  # dict_num: int = field(init=False)

  def __post_init__(self):
# Not considering subqueries yet

    isvalue(self.bace_table, t='table')
    if any([ not isinstance(i, ConnectTable) for i in self.connect_tables ]):
      raise ValueError(f"{self.connect_tables}")

    # duplicate check
    # if len(self.connect_tables) + 1 != len(set(self.connect_table) + {self.bace_table}):
      # raise ValueError(f'Duplicate table is exist')

    as_set = {self.bace_table.as_name} if isinstance(self.bace_table, AS_TABLE) else set()
    for c in filter(lambda x: type(x.table) is AS_TABLE, self.connect_tables):
      if c.as_name in as_set:
        raise ValueError(f'Duplicate as_table name:{c.as_name} in "{c}"')
      as_set.add(c.as_name)

  def __str__(self):
   return reduce(lambda a, x:f'{a} {x}', self.connect_tables, str(self.bace_table)) 

  def append(self, a):
    if not isinstance(a, ConnectTable):
      a = conntable(*a)
    if isinstance(a.table, AS_TABLE) and a.table.as_name in self.getAsNameList():
      raise ValueError(f'Duplicate as_table name:{table.as_name} in "{table}"')
    self.connect_tables.append(a)
      

  def expand(self, cons:list):
    [ self.append(con) for con in cons ]

  def connect(self, val, con, on):
    if type(val) is not SQLTable:
      raise TypeError('val is not SQLTable')
    self.append(val.bace_table, con, on)
    self.expand(val.connect_tables)

  def getAsNameList(self):
    ret = [self.bace_table.as_name] if isinstance(self.bace_table, AS_TABLE) else list()
    for c in filter(lambda x: type(x.table) is AS_TABLE, self.connect_tables):
      ret.append(c.as_name)
    return ret
    

  def getAsDict(self):
    ret = {self.bace_table.name: [self.bace_table.as_name]} if isinstance(self.bace_table, AS_TABLE) else dict()
    for c in filter(lambda x: isinstance(x, AS_TABLE), map(lambda x: x.table, self.connect_tables)):
      if c.name in ret.keys():
        ret[c.name].append(c.as_name)
      else:
        ret[c.name] = [c.as_name]
    return ret

# --------------------SQL-----------------------

@dataclass
class SelectSQL:
  columns: list[VALUE] # VALUE or ARGUMENT
  sql_table: SQLTable
  where: SQLConditions
  table_as_dict: dict = field(init=False, default_factory=dict)
  column_as_dict: dict = field(init=False, default_factory=dict)

  def __post_init__(self):
    # type check
    isvalue(*self.columns, ['arg', 'column'])
    if not isinstance(self.sql_table, SQLConditions) or not isinstance(self.where, SQLConditions):
      raise ValueError(f'{self.sql_table}')

    # duplicate check for column
    if len(columns) != len(set(columns)):
      raise ValueError('Duplicate columns exist')

    self.table_as_dict = slef.sql_table.as_dict

    # check and add column_as_dict and change (as_)column to (as_)ch_column
    def check_columns(c):
      ret = None
      if type(c) is CH_COLUMN:
        if c.ch_name not in self.table_as_dict:
          raise ValueError(f'non-existent table: {c.ch_name}')
      elif isinstance(c, COLUMN):
        l = list(filter(lambda x: x.name == c.get_table().name , self.table_as_dict.keys()))
        if len(l) >= 1:
          raise ValueError(f'There is over one table with the corresponding column:{c}')
        elif l:
          ret = get_value([c, l[0].as_name], t='ch_column' if type(c) is COLUMN else 'as_ch_column')
      elif isinstance(c, AS_VALUE):
        if c.as_name in self.column_as_dict.values():
          raise ValueError(f'Duplicate as_column name:{c.as_name} in "{c}"')
        self.column_as_dict[c] = c.as_name
      return c if ret is None else ret

    self.columns = list(map(check_columns, self.columns))

  def __str__(self):
    col = reduce(lambda a, x: f'{a}, {x}', self.columns)
    return f'SELECT {col} FROM {self.sql_table} WHERE {self.where}'

# type check of join_type
# if join_type has NATURAL or CROSS component, set 'on' to 'None'
# otherwise, 'on' must be a subclass of SQLCondition
def isjoinon(join_type, on):
  isjoin(join_type)
  if join_type & (JOIN.NATURAL | JOIN.CROSS):
    on = None
  else:
    if on is None:
      raise TypeError('not set `on`')
    if not isinstance(on, SQLConditions):
      raise TypeError('on have to be SQLCondition')

def str2condfunc(s):
  ret = formulacond if s == 'formula' else None
  if ret is None:
    raise ValueError(f'"{s}"')
  return ret

def _convert_col_arg(v)
  if type(v) is str:
    if '.' in v:
      v = get_val([v, v.replace('.', '_')], t = 'as_column')
    else:
      v = get_val([v, v], t='as_arg')
  elif type(v) is list or type(v) is tuple:
    l_len = len(v)
    v = _convert_col_arg(v[0]) if l_len == 1 else \
        get_val( v,
          t=('as_ch_column' if l_len >= 3 else 'as_column') \
              if '.' in v[0] or not isinstance(v[0], ARGUMENT) else 'as_arg'
        )
  return v

# val1, val2: instance of COLUMN or VALUE. if they are not AS_VALUE or AS_COLUMN, it is converted theses
# formula: if it is string, convert FORMULA
def formulacond(val1, val2, formula):
  vals = list(map(_convert_col_arg, [val1, val2]))
  if isinstance(formula, str):
    formula = str2formula(formula)
  return FormulaConditions(vals, formula)

def conncond(bace, connect, condfunc='formula'):
  if not isinstance(bace, BaceConditions):
    if isinstance(condfunc, str):
      condfunc = str2condfunc(condfunc)
    bace = condfunc(*bace)
  if isinstance(connect, str):
    connect = str2connect(connect)
  return ConnectConditions(bace, connect)

def sqlcond(bace, conn_conds, condfunc='formula'):
  if isinstance(condfunc, str):
    condfunc = str2condfunc(condfunc)
  if not isinstance(bace, BaceConditions):
    bace = condfunc(*bace)
  conn_conds = [ c if isinstance(c, ConnectConditions) else conncond(c*, condfunc=condfunc) for c in conn_conds ]
  return SQLConditions(bace, conn_conds)

def _convert_table(t, dft_as_name=None):
  if type(t) is str:
    if dft_as_name is None:
      return get_val(t, t='table')
    else:
      return get_val([t, dft_as_name], t='as_table')
  elif type(t) == list or type(t) == tuple:
    if len(t) == 1:
      return _convert_table(t[0], dft_as_name=dft_as_name)
    elif isinstance(t[0], TABLE) and dft_as_name is None:
      return t[0]
    else:
      return get_val(t, t='as_table')
  elif isinstance(t, TABLE) and dft_as_name is None:
    return t
  else:
    return get_val([t, dft_as_name], t='as_table')

def conntable(table, join, on=None, on_condfunc='formula'):
  table = _convert_table(table)
  if type(join) == str:
    join = str2join(join)
  if on is not None:
    on = sqlcond(*on, on_condfunc)
  return ConnectTable(table, join, on)
  
def sqltable(bace, conns):
  dfNN = 0
  asNames = {}
  if type(bace) is not AS_TABLE:
    bace = _convert_table(t, dft_as_name=f'T{dfNN}')
  bace = ConnectTable(bace, JOIN.NATURAL_INNER, None)
  conns = [ c if isinstance(ConnectTable) else conntable(*c) for c in conns ]
  for c in conns:
    as_name = f'T{dfNN}'
    while as_name in asNames.keys();
      dfNN += 1
      as_name = f'T{dfNN}'

    if type(c.table) is TABLE:
      c.table = get_val([c.table, as_name], 'as_table')
      asNames[as_name] = c
    elif c.table.as_name in asNames.keys():
      if not re.fullmatch('T\d+', t[1]):
        raise ValueError("Duplicate as_table name:", c.table.as_name)
      asNames[as_name] = asNames[c.table.as_name]
      asNames[as_name].table.as_name = as_name
      asNames[c.table.as_name] = c
    else:
      asNames[c.table.as_name] = c

  return SQLTable(bace.table, conns)


def selectsql(cols, sql_table, where):
  if not isinstance(sql_table, SQLTable):
    sql_table = sqltable(sql_table)
  if not isinstance(where, SQLConditions):
    where = sqlcond(*where)
  cols = list(map(_convert_col_arg, cols))

  as_dict = sql_table.getAsDict()
  as_list = sql_table.getAsList()

  def chval(val):
    if isinstance(val, CH_COLUMN):
      if not val.ch_name in as_list:
        raise ValueError(f"Table not define in SQLTable:{val.ch_name}")
    elif isinstance(val, COLUMN):
      ch_name = as_dict.get(val.get_table().get_name(), False)
      if not ch_name:
        raise ValueError(f"Table not define in SQLTable:{val.get_table().name}")
      val = get_val([val,ch_name], t='as_ch_column' if type(val) is AS_COLUMN else 'ch_column')
    return val

  def addchval(cnd):
    for i in range(len(cnd.vals)):
      cnd.vals[i] = chval(cnd.vals[i])

  [ addchval(c.cond) for c in where.connect_conds ]
  addchval(where.bace_cond)

  for i in range(len(cols)):
    cols[i] = chval(cols[i])

  return SelectSQL(cols, sql_table, where)







