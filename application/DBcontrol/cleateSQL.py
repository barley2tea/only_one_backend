from .sql_dataclass import *
from .sql_dataclass import __all__
from dataclasses import dataclass, field
from functools import reduce
import re

__all__.extend(['formulacond', 'conncond', 'sqlcond', 'sqltable', 'selectsql', 'insertvalsql', 'insertselectsql'])

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

  def get_vals(self): return [ x.show() for x in self.vals ]
  def get_include_table(self):
    tables = filter(lambda x: x is not None, map(lambda x: x.getTable(), self.vals))
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

# Conditions that is always True
@dataclass
class TrueConditions(BaceConditions):
  vals: list[VALUE] = field(init=False, default_factory=list)

  def __post_init__(self):
    super().__post_init__()

  def __str__(self):
    return 'TRUE'
    

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
      self.bace_cond = TrueConditions()
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
    if isinstance(self.bace_cond, TrueConditions):
      self.bace_cond = cond.cond
    else:
      self.connect_conds.append(cond)

  def extend(self, cons, cond_type='formula'):
    [ self.append(con, cond_type) for con in cons ]

  def connect(self, val, contype):
    self.append([val.bace_cond, contype])
    self.extend(val.connect_conds)
  
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
      a.table = getAsVal(a.table, nlist=self.getTableNameList(), p_t='table', pre='T')
    if self.bace_table is None:
      self.bace_table = a.table
      return
    self.connect_tables.append(a)
      

  def extend(self, cons:list):
    [ self.append(con) for con in cons ]

  def connect(self, val, con, on):
    if type(val) is not SQLTable:
      raise TypeError('val is not SQLTable')
    self.append(val.bace_table, con, on)
    self.extend(val.connect_tables)

  def getTables(self):
    if self.bace_table is None: return []
    ret = [self.bace_table]
    ret.extend([ c.table for c in self.connect_tables ])

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
      elif isinstance(c, COLUMN):   name = c.getTableName()
      else:                         continue
      if name not in table_names:   raise ValueError(f'non-existent table: {name}')

  def __str__(self):
    col = reduce(lambda a, x: f'{a}, {x}', self.columns[1:], str(self.columns[0]))
    return f'SELECT {col} FROM ({self.sql_table}) WHERE {self.where}'

@dataclass
class InsertSQL:
  table:  TABLE
  columns:  list[COLUMN]
  ondupulicate: bool = field(default=False, init=False)
  update_columns: str = field(init=False, default='')

  def __post_init__(self):
    isvalue(self.table, t='table')
    isvalue(*self.columns, t='column')
    if any([ self.table != c.getTable() and not isinstance(c, ARGUMENT) for c in self.columns ]):
      raise TypeError('table error')

  def __str__(self):
    return self.show()

  def show(self):
    col = reduce(lambda a, x: f'{a}, `{x.getName()}`', self.columns[1:], f'`{self.columns[0].getName()}`')
    return f'INSERT INTO {str(self.table)}({col})'

  def set_isupdate(self, b:bool):
    self.ondupulicate = b
  def setIsUpdate(self, b:bool):
    self.ondupulicate = b

  def setUpdateCol(self, s:str, b:bool=None):
    self.update_columns = s
    if b is not None: self.ondupulicate = b


@dataclass
class InsertValueSQL(InsertSQL):
  args: list[ARGUMENT]

  def __post_init__(self):
    super(InsertValueSQL, self).__post_init__()
    isvalue(*self.args, t='arg')
    if len(self.args) != len(self.columns):
      raise TypeError('args and columns must be same length')

  def __str__(self):
    if self.ondupulicate:
      if self.update_columns:
        return f'{self.show()} AS nwcol ON DUPLICATE KEY UPDATE {self.update_columns}'
      else:
        b_c = f'`{self.columns[0].getName()}`=nwcol.{self.columns[0].getName()}'
        key_update = reduce(lambda a, x: f'{a}, `{x.getName()}`=nwcol.{x.getName()}', self.columns[1:], b_c)
        return f'{self.show()} AS nwcol ON DUPLICATE KEY UPDATE {key_update}'
    else:
      return self.show()

  def show(self):
    arg = reduce(lambda a, x: f'{a}, {x.show()}', self.args[1:], self.args[0].show())
    return f'{super().show()} VALUE({arg})'

@dataclass
class InsertSelectSQL(InsertSQL):
  select: SelectSQL

  def __post_init__(self):
    super(InsertSelectSQL, self).__post_init__()
    if not isinstance(self.select, SelectSQL):
      raise TypeError('not SelectSQL')

    if len(self.select.columns) != len(self.columns):
      raise TypeError('select.columns and columns must be same length')

    if not all([isinstance(c, AS_VALUE) for c in self.select.columns]):
      raise TypeError(f'SelectSQL\'s column is not as name')

  def __str__(self):
    if self.ondupulicate:
      cols = self.select.columns
      _c = reduce(lambda a, x: f'{a}, nwcol.{x.as_name}', cols[1:], f'nwcol.{cols[0].as_name}')
      # ret = f'{self.show()} SELECT {_c} FROM ({str(self.select)}) AS nwcol ON DUPLICATE KEY UPDATE'
      ret = f'{self.show()} SELECT * FROM ({str(self.select)}) AS nwcol ON DUPLICATE KEY UPDATE'
      if self.update_columns:
        return f'{ret} {self.update_columns}'
      else:
        b_c = f'`{self.columns[0].getName()}`=nwcol.{cols[0].as_name}'
        upcol = reduce(lambda a, x: f'{a}, `{x[0].getName()}`=nwcol.{x[1].as_name}', zip(self.columns[1:], cols[1:]), b_c)
        return f'{ret} {upcol}'
    else:
      return f'{super().__str__()} {str(self.select)}'

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

def _convert_col(col, as_dict, tlist):
  if not isinstance(col, COLUMN): return col
  if isinstance(col, CH_COLUMN):
    if col.ch_name in tlist:  return col

  table_name = col.getTableName()
  if table_name in tlist and not isinstance(col, CH_COLUMN):  return col
  ch_name = as_dict.get(table_name, [])
  if len(ch_name) != 1:
    raise ValueError(f"Table not define in SQLTable:{col.getTable().name}")
  return getVal([col, ch_name[0]], t='as_ch_column' if isinstance(col, AS_VALUE) else 'ch_column')

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
def formulacond(val1, val2, formula='='):
  vals = getVal(val1, val2, p_t='arg', p_c='ch', l=True)
  if isinstance(formula, str): formula = str2formula(formula)
  return FormulaConditions(vals, formula)

def conncond(bace, connect, condfunc='formula'):
  if not isinstance(bace, BaceConditions):
    if isinstance(condfunc, str): condfunc = str2condfunc(condfunc)
    bace = condfunc(*bace)
  if isinstance(connect, str): connect = str2connect(connect)
  return ConnectConditions(bace, connect)

def sqlcond(bace=None, *conn_conds, condfunc='formula', default_connect='and'):
  if bace is None:
    return SQLConditions(None, [])
  if isinstance(condfunc, str):             condfunc = str2condfunc(condfunc)
  if not isinstance(bace, BaceConditions):  bace = condfunc(*bace)

  def convert_conn(c):
    if isinstance(c, ConnectConditions):    return c
    elif isinstance(c[0], BaceConditions):
      if len(c) == 1:   return conncond(c[0], default_connect, condfunc=condfunc)
      else:             return conncond(c[0], c[1], condfunc=condfunc)
    else:
      connect = str2connect(c[-1], e=False)
      if connect is None: return conncond(c, default_connect, condfunc=condfunc)
      else:               return conncond(c[:-1], connect, condfunc=condfunc)
  conn_conds = list(map(convert_conn, conn_conds))
  return SQLConditions(bace, conn_conds)

def conntable(table, join, on=None, on_condfunc='formula'):
  table = getVal(table, p_t='table')
  isvalue(table, t='table')
  if type(join) == str: join = str2join(join)
  if on is not None and not isinstance(on, SQLConditions):
    if type(on) not in (tuple, list): on = [on]
    on = sqlcond(*on, condfunc=on_condfunc)
  return ConnectTable(table, join, on)
  
def sqltable(bace=None, *conns):
  if bace is None:
    return SQLTable(None, [])
  dfNN = 0
  asNames = {}
  if not isinstance(bace, AS_TABLE):
    bace = getAsVal(bace, p_t='table')
    bace = ConnectTable(bace, JOIN.NATURAL_INNER, None)
    asNames[bace.table.as_name] = bace.table
  else: bace = ConnectTable(bace, JOIN.NATURAL_INNER, None)

  conns = [ c if isinstance(c, ConnectTable) else conntable(*c) for c in conns ]
  for c in conns:
    c.table = getAsVal(c.table, nlist=list(asNames.keys()), p_t='table')
    asNames[c.table.as_name] = c.table

    as_set = set(asNames.keys())
    as_dict = {}
    for k in asNames.keys(): as_dict[asNames[k].name] = None if asNames[k].name in as_dict.keys() else k
    for c in [x for r in map(lambda x: x.on.to_list(), filter(lambda x: x.on is not None, conns)) for x in r]:
      for i in [x for x in range(len(c)) if isinstance(c[x], COLUMN) and not isinstance(c[x], CH_COLUMN)]:
        ch_name = as_dict.get(c[i].getTable().name, None)
        if ch_name is None: raise ValueError(f'NameError')
        if type(c[i]) is COLUMN:  c[i] = getVal([c[i].name, ch_name], t='ch_column')
        else: c[i] = getVal([c[i].name, ch_name, c[i].as_name], t='as_ch_column')

  return SQLTable(bace.table, conns)

def selectsql(cols, sql_table, where, default_condfunc='formula'):
  # print(cols)
  # print(sql_table)
  # print(where)
  if not isinstance(sql_table, SQLTable):   sql_table = sqltable(*sql_table)
  if not isinstance(where, SQLConditions):  where = sqlcond(*where, condfunc=default_condfunc)
  cols = getVal(*cols, l=True, p_t='arg')

  _convert_cond(where, sql_table)
  as_dict = sql_table.getAsDict()
  as_list = sql_table.getAsNameList()
  cols = list(map(lambda x: _convert_col(x, as_dict, as_list), cols))

  return SelectSQL(cols, sql_table, where)

def _insertsql(cols, table):
  cols = [ c.split('.')[-1] if type(c) is str else c.getName() for c in cols ]
  table = getVal(table, t='table')
  cols = table.getCol(*cols)
  return cols, table

def insertvalsql(cols, table, vals):
  cols, table = _insertsql(cols, table)
  vals = getVal(*vals, p_t='arg')
  if any([isinstance(c, ARGUMENT) for c in cols]) or any([isinstance(c, COLUMN) for c in vals]):
    raise ValueError('Value error in insertvalsql')

  cols = list(map(lambda c: getVal(c.name, t='column'), cols))
  if isinstance(table, AS_TABLE): table = getVal(table.name, t='table')

  return InsertValueSQL(table, cols, vals)

def insertselectsql(cols, table, select):
  cols, table = _insertsql(cols, table)
  if not isinstance(select, SelectSQL): select = selectsql(*select)
  if any([isinstance(c, ARGUMENT) for c in cols]): raise ValueError('Value error in insertvalsql')

  cols = list(map(lambda c: getVal(c.name, t='column'), cols))
  if isinstance(table, AS_TABLE): table = getVal(table.name, t='table')

  select.columns = getAsVal(*select.columns, pre='C')

  return InsertSelectSQL(table, cols, select)
