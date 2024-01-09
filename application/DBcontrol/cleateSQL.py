from .sql_dataclass import *
from .sql_dataclass import __all__
from dataclasses import dataclass, field
from functools import reduce
import re

__all__.extend(['formulacond', 'conncond', 'sqlcond', 'sqltable', 'selectsql'])

# ------------------conditions------------------

# This is the bace for class sql conditions
@dataclass
class BaceConditions:
  vals: list[VALUE] # COLUMN or ARGUMENT

  def __post_init__(self):
    for i in filter(lambda x: not isinstance(x, (COLUMN, ARGUMENT)), self.vals):
      raise ValueError(f'{type(i)}')
  def __len__(self):
    return len(self.vals)
  def __getitem__(self, k):
    return self.vals[k]
  def __setitem__(self, k, v):
    if not isinstance(v, (COLUMN, ARGUMENT)):
      raise ValueError(f'{type(i)}')
    self.vals[k] = v

  def get_vals(self): return list(map(lambda x: x.show(), self.vals))
  def get_include_table(self):
    tables = filter(lambda x: x is not None, map(lambda x: x.get_table(), self.vals))
    return { i.as_name if isinstance(i, AS_TABLE) else i.name for i in tables }
    

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
    v = self.get_vals()
    return f'{str(v[0])}{formula2str(self.formula)}{str(v[1])}'

#-----------------------------------------------

@dataclass
class ConnectConditions:
  cond: BaceConditions
  connect: CONNECT

  def __post_init__(self):
    isconnect(self.connect)
  
  def __str__(self): return f' {connect2str(self.connect)} {str(self.cond)}'

@dataclass
class SQLConditions:
  bace_cond: BaceConditions
  connect_conds: list[ConnectConditions]

  def __post_init__(self):
    if self.bace_cond is None:
      self.bace_cond = 1
      self.tables = set()
    elif not isinstance(self.bace_cond, BaceConditions):
      raise ValueError(f"{type(self.bace_cond)}")
    if any([ not isinstance(i, ConnectConditions) for i in self.connect_conds ]):
      raise ValueError(f"{self.connect_conds}")

  def __str__(self):
    return reduce(lambda a, x: f'{a}{str(x)}', self.connect_conds, str(self.bace_cond))
  def __iter__(self):
    self.iter_count = -1
    return self
  def __next__(self):
    if self.iter_count == len(self.connect_conds): raise StopIteration()
    ret = self.bace_cond if self.iter_count == -1 else self.connect_conds[self.iter_count].cond
    self.iter_count += 1
    return ret
    

  def append(self, cond, condfunc='formula'):
    if not isinstance(cond, ConnectConditions):
      cond = conncond(cond[:-1], cond[-1], condfunc=condfunc)
    if type(self.bace_cond) is int:
      self.bace_cond = cond.cond
    else:
      self.connect_conds.append(cond)

  def expand(self, cons, cond_type='formula'):
    [ self.append(con, cond_type) for con in cons ]

  def connect(self, val, contype):
    self.append([val.bace_cond, contype])
    self.expand(val.connect_conds)
  
  def get_include_table(self):
    return reduce(lambda a, x: a.union(x.cond.get_include_table()), self.connect_conds, self.bace_cond.get_include_table())
  def to_list(self):
    return [self.bace_cond] + [x.cond for x in self.connect_conds]

# ---------------------table--------------------

@dataclass
class ConnectTable:
  table: TABLE
  join_type: JOIN
  on: SQLConditions
  def __post_init__(self):
    self.on = isjoinon(self.join_type, self.on)
    isvalue(self.table, t='table')
 
  def __str__(self):
    s = f'{join2str(self.join_type)} {str(self.table)}'
    return  s if self.on is None else f'{s} ON {str(self.on)}'

@dataclass
class SQLTable:
  bace_table: AS_TABLE
  connect_tables: list[ConnectTable]

  def __post_init__(self):
# Not considering subqueries yet
    if self.bace_table is None:
      self.connect_tables = []
      return

    isvalue(self.bace_table, t='table')
    if any([ not isinstance(i, ConnectTable) for i in self.connect_tables ]):
      raise ValueError(f"{self.connect_tables}")

    # duplicate check
    as_set = {self.bace_table.as_name} if isinstance(self.bace_table, AS_TABLE) else set()
    for c in self.connect_tables:
      tn = c.table.as_name if isinstance(c.table, AS_TABLE) else c.table.name
      if tn in as_set: raise ValueError(f'Duplicate as_table name:{tn} in "{c}"')
      as_set.add(tn)

    # 'on' check
    for c in filter(lambda x: x.on is not None, self.connect_tables):
      if not c.on.get_include_table() <= as_set:
        raise ValueError(f"'ON' statement has non-existent table:{c}")
      
  def __str__(self):
   return reduce(lambda a, x:f'{a} {x}', self.connect_tables, str(self.bace_table)) 

  def append(self, a):
    if not isinstance(a, ConnectTable):
      a = conntable(*a)
    if type(a.table) is TABLE:
      a.table = _convert_as_table(a.table, self.getTableNameList())
    if self.bace_table is None:
      self.bace_table = a.table
      return
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

  def getTableNameList(self, ch=True):
    if self.bace_table is None: return []
    ret = [self.bace_table.as_name] if isinstance(self.bace_table, AS_TABLE) and ch else [self.bace_table.name]
    for c in self.connect_tables:
      ret.append(c.table.as_name if isinstance(c.table, AS_TABLE) and ch else c.table.name)
    return ret

  def getAsNameList(self):
    ret = [self.bace_table.as_name] if isinstance(self.bace_table, AS_TABLE) else list()
    for c in filter(lambda x: type(x.table) is AS_TABLE, self.connect_tables):
      ret.append(c.table.as_name)
    return ret
    

  def getAsDict(self):
    ret = {self.bace_table.name: [self.bace_table.as_name]} if isinstance(self.bace_table, AS_TABLE) else dict()
    for c in filter(lambda x: isinstance(x, AS_TABLE), map(lambda x: x.table, self.connect_tables)):
      if c.name in ret.keys():  ret[c.name].append(c.as_name)
      else:                     ret[c.name] = [c.as_name]
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
    isvalue(*self.columns, t=['arg', 'column'])
    if not isinstance(self.sql_table, SQLTable) or not isinstance(self.where, SQLConditions):
      raise ValueError(f'{self.sql_table}')

    # duplicate check for column
    if len(self.columns) != len(set(self.columns)): raise ValueError('Duplicate columns exist')

    table_names = self.sql_table.getTableNameList()
    table_as_dict = self.sql_table.getAsDict()

    # check and add column_as_dict
    for c in self.columns:
      if isinstance(c, CH_COLUMN):  name = c.ch_name
      elif isinstance(c, COLUMN):   name = c.get_table().name
      if name not in table_names:   raise ValueError(f'non-existent table: {name}')

  def __str__(self):
    col = reduce(lambda a, x: f'{a}, {x}', self.columns)
    return f'SELECT {col} FROM ({self.sql_table}) WHERE {self.where}'

# type check of join_type
# if join_type has NATURAL or CROSS component, set 'on' to 'None'
# otherwise, 'on' must be a subclass of SQLCondition
def isjoinon(join_type, on):
  isjoin(join_type)
  if join_type & (JOIN.NATURAL | JOIN.CROSS): return None
  else:
    if on is None:                        raise TypeError('not set `on`')
    if not isinstance(on, SQLConditions): raise TypeError('on have to be SQLCondition')
  return on

def str2condfunc(s):
  ret = formulacond if s == 'formula' else None
  if ret is None:
    raise ValueError(f'"{s}"')
  return ret

def _convert_col_arg(v):
  if type(v) is str:
    if '.' in v:
      v = get_val([v, v.replace('.', '_')], t = 'as_column')
    else:
      v = get_val([v, v], t='as_arg')
  elif type(v) is list or type(v) is tuple:
    l_len = len(v)
    if l_len < 2:
      v = _convert_col_arg(*v)
    else:
      t = ( ('as_ch_column' if l_len >= 3 else 'ch_column') if '.' in v[0] else \
            'as_arg') if type(v[0]) is str else \
          'as_arg' if isinstance(v[0], ARGUMENT) else \
          'as_ch_column' if l_len > 2 or isinstance(v[0], (AS_COLUMN, CH_COLUMN)) else \
          'ch_column'
      v = get_val(v, t=t)

  return v

def _convert_table(t, dft_as_name=None):
  if type(t) is str:
    return get_val(t, t='table') if dft_as_name is None else get_val([t, dft_as_name], t='as_table')
  elif type(t) in [list, tuple]:
    return  _convert_table(t[0], dft_as_name=dft_as_name) if len(t) == 1 else \
            t[0] if isinstance(t[0], TABLE) and dft_as_name is None else get_val(t, t='as_table')
  elif isinstance(t, TABLE) and dft_as_name is None:
    return t
  else:
    return get_val([t, dft_as_name], t='as_table')

def _convert_as_table(table, table_list, pre='T'):
  if isinstance(table, AS_TABLE):
    if table.as_name in table_list: pre = table.as_name
    else:                           return table
  name = table.name if isinstance(table, TABLE) else table
  i = 0
  as_name = f'{pre}0'
  while as_name in table_list:
    i += 1
    as_name = f'{pre}{i}'
  return get_val([name, as_name], t='as_table')

def _convert_col(col, as_dict, tlist):
  if not isinstance(col, COLUMN): return col
  if isinstance(col, CH_COLUMN):
    if col.ch_name in tlist:  return col

  table_name = col.name.split('.')[0]
  if table_name in tlist and not isinstance(col, CH_COLUMN):  return col
  ch_name = as_dict.get(table_name, [])
  if len(ch_name) != 1:
    raise ValueError(f"Table not define in SQLTable:{col.get_table().name}")
  return get_val([col,ch_name[0]], t='as_ch_column' if isinstance(col, AS_VALUE) else 'ch_column')

def _convert_cond(sqlc, sqlt):
  as_dict = sqlt.getAsDict()
  tlist = sqlt.getTableNameList()
  def addchval(cnd):
    for i in range(len(cnd.vals)):
      cnd.vals[i] = _convert_col(cnd.vals[i], as_dict, tlist)
  [ addchval(c.cond) for c in sqlc.connect_conds ]
  addchval(sqlc.bace_cond)


# val1, val2: instance of COLUMN or VALUE. if they are not AS_VALUE or AS_COLUMN, it is converted theses
# formula: if it is string, convert FORMULA
def formulacond(val1, val2, formula):
  vals = list(map(_convert_col_arg, [val1, val2]))
  if isinstance(formula, str): formula = str2formula(formula)
  return FormulaConditions(vals, formula)

def conncond(bace, connect, condfunc='formula'):
  if not isinstance(bace, BaceConditions):
    if isinstance(condfunc, str):
      condfunc = str2condfunc(condfunc)
    bace = condfunc(*bace)
  if isinstance(connect, str):
    connect = str2connect(connect)
  return ConnectConditions(bace, connect)

def sqlcond(bace=None, *conn_conds, condfunc='formula'):
  if bace is None:
    return SQLConditions(None, [])
  if isinstance(condfunc, str):             condfunc = str2condfunc(condfunc)
  if not isinstance(bace, BaceConditions):  bace = condfunc(*bace)

  def convert_conn(c):
    if isinstance(c, ConnectConditions):    return c
    elif isinstance(c[0], BaceConditions):  return conncond(c[0], c[1], condfunc=condfunc)
    else:                                   return conncond(c[:3], c[3], condfunc=condfunc)
  conn_conds = list(map(convert_conn, conn_conds))
  return SQLConditions(bace, conn_conds)

def conntable(table, join, on=None, on_condfunc='formula'):
  table = _convert_table(table)
  if type(join) == str:
    join = str2join(join)
  if on is not None and not isinstance(on, SQLConditions):
    on = sqlcond(*on, condfunc=on_condfunc)
  return ConnectTable(table, join, on)
  
def sqltable(bace=None, *conns):
  if bace is None:
    return SQLTable(None, [])
  dfNN = 0
  asNames = {}
  if not isinstance(bace, AS_TABLE):
    bace = _convert_table(bace, dft_as_name='T0')
    bace = ConnectTable(bace, JOIN.NATURAL_INNER, None)
    asNames[bace.table.as_name] = bace.table
  else: bace = ConnectTable(bace, JOIN.NATURAL_INNER, None)

  conns = [ c if isinstance(c, ConnectTable) else conntable(*c) for c in conns ]
  for c in conns:
    c.table = _convert_as_table(c.table, asNames.keys())
    asNames[c.table.as_name] = c.table

    as_set = set(asNames.keys())
    as_dict = {}
    for k in asNames.keys(): as_dict[asNames[k].name] = None if asNames[k].name in as_dict.keys() else k
    for c in [x for r in map(lambda x: x.on.to_list(), filter(lambda x: x.on is not None, conns)) for x in r]:
      for i in [x for x in range(len(c)) if isinstance(c[x], COLUMN) and not isinstance(c[x], CH_COLUMN)]:
        ch_name = as_dict.get(c[i].get_table().name, None)
        if ch_name is None: raise ValueError(f'NameError')
        if type(c[i]) is COLUMN:  c[i] = get_val([c[i].name, as_name], t='ch_column')
        else: c[i] = get_val([c[i].name, ch_name, c[i].as_name], t='as_ch_column')

  return SQLTable(bace.table, conns)


def selectsql(cols, sql_table, where, default_condfunc='formula'):
  if not isinstance(sql_table, SQLTable):   sql_table = sqltable(*sql_table)
  if not isinstance(where, SQLConditions):  where = sqlcond(*where, condfunc=default_condfunc)
  cols = list(map(_convert_col_arg, cols))

  # as_dict = sql_table.getAsDict()
  # as_list = sql_table.getAsNameList()

  # def chval(val):
  #   if isinstance(val, CH_COLUMN):
  #     if not val.ch_name in as_list:
  #       raise ValueError(f"Table not define in SQLTable:{val.ch_name}")
  #   elif isinstance(val, COLUMN):
  #     ch_name = as_dict.get(val.get_table().get_name(), [])
  #     if not ch_name:
  #       return val
  #     if len(ch_name) != 1:
  #       raise ValueError(f"Table not define in SQLTable:{val.get_table().name}")
  #     val = get_val([val,ch_name[0]], t='as_ch_column' if type(val) is AS_COLUMN else 'ch_column')
  #   return val

  # def addchval(cnd):
  #   for i in range(len(cnd.vals)):
  #     cnd.vals[i] = chval(cnd.vals[i])

  # [ addchval(c.cond) for c in where.connect_conds ]
  # addchval(where.bace_cond)
  _convert_cond(where, sql_table)
  as_dict = sql_table.getAsDict()
  as_list = sql_table.getAsNameList()
  cols = list(map(lambda x: _convert_col(x, as_dict, as_list), cols))

  # for i in range(len(cols)): cols[i] = chval(cols[i])

  return SelectSQL(cols, sql_table, where)







