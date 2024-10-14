
from mysql.connector import Error
from application import app
from application.exception import *
from flask import jsonify, request


def catchError(func=None, req_json=False):
  def _catchError(_func):
    def wrapper(*args, **kwargs):
      if req_json and request.json is None:
        app.logger.debug("Send not JSON")
        return HTTP_STAT(400)
      try:
        return _func(*args, **kwargs)
      except Error as e:
        app.logger.warning(str(e))
        return jsonify({'error': 'SQLError'}), 400
      except RequestException as e:
        app.logger.warning(str(e))
        return HTTP_STAT(400)
    wrapper.__name__ = _func.__name__
    return wrapper
  return _catchError if func is None else _catchError(func)

def getReqJson(k):
  try:
    return request.json[k]
  except KeyError:
    raise RequestKeyError(k)

def HTTP_STAT(stat, message=None):
  if message is None:
    message = 'success' if stat == 200 else \
              'Bad Request' if stat == 400 else \
              'Unauthorized' if stat == 401 else \
              'Forbidden' if stat == 401 else \
              'Not Found' if stat == 404 else \
              'Internal Server Error'
  status = 'message' if stat == 200 else 'error'
  return jsonify({status: message}), stat

__all__ = ['api']
