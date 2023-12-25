from enum import Enum, Flag, auto

__all__ = ['JOIN', 'FORMULA', 'CONNECT', 'str2formula', 'formula2str', 'join2str', 'str2connect', 'connect2str', 'isjoin', 'isformula', 'isconnect']

# enum class
class JOIN(Flag):
  INNER = auto()
  OUTER = auto()
  CROSS = auto()
  NATURAL = auto()
  RIGHT = auto()
  LEFT = auto()
  FULL = auto()
  NATURAL_INNER = INNER | NATURAL
  RIGHT_OUTER = RIGHT | OUTER
  LEFT_OUTER = LEFT | OUTER
  FULL_OUTER = FULL | OUTER
  NATURAL_RIGHT_OUTER = NATURAL | OUTER | RIGHT
  NATURAL_LEFT_OUTER = NATURAL | OUTER | LEFT
  NATURAL_FULL_OUTER = NATURAL | OUTER | FULL
class FORMULA(Enum):
  EQ = auto()
  NE = auto()
  LT = auto()
  LE = auto()
  GT = auto()
  GE = auto()
  IS = auto()
  ISNOT = auto()
class CONNECT(Enum):
  AND = auto()
  OR = auto()

def str2formula(s:str):
  s = s.upper()
  ret = FORMULA.EQ if s == '='  else \
        FORMULA.NE if s == '!=' else \
        FORMULA.LT if s == '<'  else \
        FORMULA.LE if s == '<=' else \
        FORMULA.GT if s == '>'  else \
        FORMULA.GE if s == '>=' else \
        FORMULA.IS if s == 'IS' else \
        FORMULA.ISNOT if s == 'IS NOT' else None
  if ret is None:
    raise ValueError(f'"{s}"')
  return ret
def formula2str(f:FORMULA):
  ret = '='   if f == FORMULA.EQ  else \
        '!='  if f == FORMULA.NE  else \
        '<'   if f == FORMULA.LT  else \
        '<='  if f == FORMULA.LE  else \
        '>'   if f == FORMULA.GT  else \
        '>='  if f == FORMULA.GE  else \
        'IS'  if f == FORMULA.IS  else \
        'IS NOT'  if f == FORMULA.ISNOT else None
  if ret is None:
    raise ValueError(f'"{f}"')
  return ret
def join2str(j:JOIN):
  ret = 'INNER JOIN'  if j == JOIN.INNER else \
        'OUTER JOIN'  if j == JOIN.OUTER else \
        'CROSS JOIN'  if j == JOIN.CROSS else \
        'RIGHT OUTER JOIN'  if j == JOIN.RIGHT_OUTER else \
        'LEFT OUTER JOIN'   if j == JOIN.LEFT_OUTER else \
        'FULL OUTER JOIN'   if j == JOIN.FULL_OUTER else \
        'NATURAL INNER JOIN'  if j == JOIN.NATURAL_INNER else \
        'NATURAL RIGHT OUTER JOIN'  if j == JOIN.NATURAL_RIGHT_OUTER else \
        'NATURAL LEFT OUTER JOIN'   if j == JOIN.NATURAL_LEFT_OUTER else \
        'NATURAL FULL OUTER JOIN'   if j == JOIN.NATURAL_FULL_OUTER else None
  if ret is None:
    raise ValueError(f'"{f}"')
  return ret
def str2connect(s:str):
  ret = CONNECT.AND if s == 'and' else \
        CONNECT.OR  if s == 'or'  else None
  if ret is None:
    raise ValueError(f'"{s}"')
  return ret
def connect2str(c:CONNECT):
  ret = 'AND' if c == CONNECT.AND else \
        'OR'  if c == CONNECT.OR  else None
  if ret is None:
    raise ValueError(f'"{s}"')
  return ret

# check arg
def isjoin(join_type):
  if not (join_type & (JOIN.INNER | JOIN.OUTER | JOIN.CROSS)):
    raise TypeError('join_type must has INNER, OUTER or CROSS')
def isformula(f):
  if not isinstance(f, FORMULA):
    raise TypeError(f'this is not {FORMULA.__class__.__name__} instance:{f}')
def isconnect(c):
  if not isinstance(c, CONNECT):
    raise TypeError(f'this is not {FORMULA.__class__.__name__} instance:{f}')
