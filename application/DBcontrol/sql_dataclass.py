from .sql_enum import *
from .sql_enum import __all__
from dataclasses import dataclass, field
import re
__all__.extend(['isvalue', 'getVal', 'getAsVal', 'VALUE', 'COLUMN', 'TABLE', 'ARGUMENT', 'AS_VALUE', 'AS_COLUMN', 'AS_TABLE', 'AS_ARGUMENT', 'CH_COLUMN', 'AS_CH_COLUMN'])

def _check_name(s:str):
  if s is None: raise ValueError(f'Wrong format: {s}')
  if not re.fullmatch('[a-zA-Z_][\da-zA-Z_]*', s): raise ValueError(f'Wroung format: {s}')

# type convertion
def str2valclass(s:str):
  ret = VALUE     if s == 'value'   else \
        COLUMN    if s == 'column'  else \
        TABLE     if s == 'table'   else \
        ARGUMENT  if s == 'arg'     else \
        CH_COLUMN    if s == 'ch_column'  else \
        AS_VALUE     if s == 'as_value'  else \
        AS_COLUMN    if s == 'as_column'  else \
        AS_TABLE     if s == 'as_table'   else \
        AS_ARGUMENT  if s == 'as_arg'     else \
        AS_CH_COLUMN if s == 'as_ch_column' else None
  if ret is None:
    raise ValueError(f'"{s}"')
  return ret

# type check of VALUE's subclass
def isvalue(*val, t:str):
  v_class = tuple([str2valclass(tt) for tt in t]) if isinstance(t, list) else str2valclass(t)
  if not any([ isinstance(v, v_class) for v in val ]):
    raise TypeError(f'these have not {v_class} instance:{val}')

# get asval e.g. AS_COLUMN
def _get_val(name, *args, valclass=None):
  as_name, ch_name = None, None
  if isinstance(name, VALUE):
    if isinstance(name, AS_VALUE): as_name = name.as_name
    if isinstance(name, CH_COLUMN): ch_name = name.ch_name
    name = name.name

  if valclass is AS_CH_COLUMN:
    if ch_name is None:
      ch_name = args[0]
      if as_name is None: as_name = args[1]
    elif as_name is None: as_name = args[0]
    return valclass(name, ch_name, as_name)
  elif valclass is CH_COLUMN:
    if ch_name is None: ch_name = args[0]
    return valclass(name, ch_name)
  elif issubclass(valclass, AS_VALUE):
    if as_name is None: as_name = args[0]
    return valclass(name, as_name)
  else: return valclass(name)

def _convert_val(v, p_t:str, p_c:str):
  if type(v) is str:  t = 'column' if '.' in v else p_t
  elif isinstance(v, VALUE):  return v
  else:
    v_l = len(v)
    if v_l == 1:  return _convert_val(v[0], p_t=p_t, p_c=p_c)
    elif v_l == 2:
      if type(v[0]) is str: t = f'{p_c}_column' if '.' in v[0] else f'as_{p_t}'
      elif type(v[0]) is TABLE: t = 'as_table'
      elif type(v[0]) is COLUMN: t = f'{p_c}_column'
      elif type(v[0]) is ARGUMENT: t = f'as_arg'
      elif type(v[0]) in (AS_COLUMN, CH_COLUMN):  t = 'as_ch_column'
    else: t = 'as_ch_column'
  return getVal(v, t=t)

# *args: str or list[str]
# t:  valtype. e.g. 'table', 'arg'. if None, automatically interpreted
# l: if true, The return value is guaranteed to be a list
# p_t: 'table' or 'arg'. Priority for automatic interpretation. 
# p_c: 'ch' or 'as'. Indicates whether 'as_column' or 'ch_column' is given priority.
def getVal(*args, t:str=None, l:bool=False, p_t:str='arg', p_c='ch'):
  if not args: return []
  args = map(lambda a: a if type(a) in (list, tuple) else [a], args)

  if t is None:
    ret = [ _convert_val(v, p_t=p_t, p_c=p_c) for v in args ]
  else:
    valclass = str2valclass(t)
    ret = [ _get_val(*a, valclass=valclass) for a in args ]

  return ret if len(ret) != 1 or l else ret[0]

# t: String without 'as_' or None
# nlist: black list
def getAsVal(*args, nlist=[], t:str=None, l:bool=False, p_t:str='arg', p_c='ch', pre='T'):
  args = getVal(*args, t=t, l=True, p_t=p_t, p_c=p_c)
  def n_check(n):
    if n.as_name in nlist: raise f"Dupulicate Error: {repr(n)} in {nlist}"
  as_val_list = filter(lambda x: isinstance(x, AS_VALUE), args)
  map(n_check, as_val_list)
  nlist.extend([x.as_name for x in as_val_list])

  def _f(v):
    if isinstance(v, AS_VALUE): return v
    as_name, i = f'{pre}0', 0
    while as_name in nlist:
      i += 1
      as_name = f'{pre}{i}'
    nlist.append(as_name)
    return getVal([v, as_name], p_c='as')
  ret = list(map(_f, args))
  return ret if len(ret) != 1 or l else ret[0]


# bace class
@dataclass(frozen=True)
class VALUE:
  name: str
  def __str__(self):      return self.show()
  def getTable(self):     return None
  def getTableName(self): return None
  def getName(self):      return self.name
  def show(self):         return self.name
@dataclass(frozen=True)
class AS_VALUE(VALUE):
  as_name: str
  def __post_init__(self):
    _check_name(self.as_name)
  def __str__(self):    return f"{self.show()} AS `{self.as_name}`"

# sql value class
@dataclass(frozen=True)
class ARGUMENT(VALUE):
  def __post_init__(self):
    _check_name(self.name)
  def show(self):       return f'%({self.name})s'
@dataclass(frozen=True)
class TABLE(VALUE):
  def __post_init__(self):
    _check_name(self.name)
  def getTable(self):     return self
  def getTableName(self): return self.name
  def show(self):         return f'`{self.name}`'
  def getCol(self, *cols): return [ COLUMN(f'{self.name}.{c}') for c in cols ]
@dataclass(frozen=True)
class COLUMN(VALUE):
  def __post_init__(self):
    if not re.fullmatch('^[a-zA-Z_][\da-zA-Z_]*\.[a-zA-Z_][\da-zA-Z_]*$', self.name): raise ValueError(f'Wrong column format: {self.name}')
  def getTable(self):     return TABLE(self.name.split('.')[0])
  def getTableName(self): return self.name.split('.')[0]
  def getName(self):      return self.name.split('.')[1]

@dataclass(frozen=True)
class CH_COLUMN(COLUMN):
  ch_name: str
  def __post_init__(self):
    super().__post_init__()
    _check_name(self.ch_name)
  def getTable(self): return AS_TABLE(self.getTableName(), self.ch_name)
  def show(self): return f'{self.ch_name}.{self.getName()}'
  
# class whith 'as_name' added to name class
@dataclass(frozen=True)
class AS_ARGUMENT(AS_VALUE, ARGUMENT):
  def __post_init__(self):
    ARGUMENT.__post_init__(self)
    AS_VALUE.__post_init__(self)
class AS_TABLE(AS_VALUE, TABLE):
  def __post_init__(self):
    TABLE.__post_init__(self)
    AS_VALUE.__post_init__(self)
  def getCol(self, cols):  return [ CH_COLUMN(f'{self.name}.{c}', self.as_name) for c in cols ]
@dataclass(frozen=True)
class AS_COLUMN(AS_VALUE, COLUMN):
  def __post_init__(self):
    COLUMN.__post_init__(self)
    AS_VALUE.__post_init__(self)
@dataclass(frozen=True)
class AS_CH_COLUMN(AS_VALUE, CH_COLUMN):
  def __post_init__(self):
    CH_COLUMN.__post_init__(self)
    AS_VALUE.__post_init__(self)

