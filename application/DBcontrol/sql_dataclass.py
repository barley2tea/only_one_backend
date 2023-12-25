# from .sql_enum import *
import sql_enum
from sql_enum import *
from dataclasses import dataclass, field
import re

__all__ = ['isvalue', 'get_val', 'VALUE', 'COLUMN', 'TABLE', 'ARGUMENT', 'AS_VALUE', 'AS_COLUMN', 'AS_TABLE', 'AS_ARGUMENT', 'CH_COLUMN', 'AS_CH_COLUMN']
__all__.extend(sql_enum.__all__)

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

# select by 't:str' and get subclass of VALUE with name
# if you want to get asvalue,
# you can set [name:str or VALUE, as_name:str, ch_name:str(if t='as_ch_column' and type(name) != CH_COLUMN)]
def get_val(*args, t:str, l:bool=False):
  if not args: return []
  valclass = str2valclass(t)

  ret = [ _get_val(*a, valclass=valclass) if type(a) is list else _get_val(a, valclass=valclass) for a in args ]

  return ret if len(ret) != 1 or l else ret[0]

# bace class
@dataclass(frozen=True)
class VALUE:
  name: str
  def __str__(self):    return self.show()
  def get_table(self):  return None
  def get_name(self):   return self.name
  def show(self):       return self.name
@dataclass(frozen=True)
class AS_VALUE(VALUE):
  as_name: str
  def __post_init__(self):
    _check_name(self.as_name)
  def __str__(self):  return f"{self.show()} AS '{self.as_name}'"
  def show(self):     return super(AS_VALUE, self).show()

# sql value class
@dataclass(frozen=True)
class ARGUMENT(VALUE):
  def __post_init__(self):
    _check_name(self.name)
  def show(self): return f'%({self.name})s'
@dataclass(frozen=True)
class TABLE(VALUE):
  def __post_init__(self):
    _check_name(self.name)
  def show(self):       return f'`{self.name}`'
  def get_table(self):  return self
@dataclass(frozen=True)
class COLUMN(VALUE):
  def __post_init__(self):
    if not re.fullmatch('^[a-zA-Z_][\da-zA-Z_]*\.[a-zA-Z_][\da-zA-Z_]*$', self.name): raise ValueError(f'Wrong column format: {self.name}')
  def get_table(self):  return TABLE(self.name.split('.')[0])
  def get_name(self):   return self.name.split('.')[1]

@dataclass(frozen=True)
class CH_COLUMN(COLUMN):
  ch_name: str
  def __post_init__(self):
    super().__post_init__()
    _check_name(self.ch_name)
  def get_table(self): return AS_TABLE(self.name.split('.')[0], self.ch_name)
  def show(self): return f'{self.ch_name}.{self.get_name()}'
  
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
@dataclass(frozen=True)
class AS_COLUMN(AS_VALUE, COLUMN):
  def __post_init__(self):
    COLUMN.__post_init__(self)
    AS_VALUE.__post_init__(self)
  def get_table(self): return TABLE(self.name.split('.')[0])
@dataclass(frozen=True)
class AS_CH_COLUMN(AS_VALUE, CH_COLUMN):
  def __post_init__(self):
    CH_COLUMN.__post_init__(self)
    AS_VALUE.__post_init__(self)

