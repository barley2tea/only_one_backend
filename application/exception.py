
# Exception when there is a problem with the request
class RequestException(Exception):
  def __init__(self, arg=''):
    self.arg = arg

class RequestKeyError(RequestException):
  def __str__(self):
    return f"RequestKeyError: '{self.arg}'"

class RequestValueError(RequestException):
  def __str__(self):
    return f"RequestValueError: '{self.arg}'"

# prosses exception
class ProssesException(Exception):
  def __init__(self, arg=''):
    self.arg = arg
  def __str__(self):
    return f"ProssesException: '{self.arg}'"
