
from mysql.connector import Error
from application import app
from application.exception import *
from flask import jsonify, request


def catchError(func=None, req_json=False):
  def _catchError(_func):
    def wrapper(*args, **kwargs):
      if req_json and request.json is None:  return HTTP_STAT(400)
      try:
        return _func(*args, **kwargs)
      except Error as e:
        app.logger.warning(str(e))
        return jsonify({'error': 'SQLError'}), 400
      except RequestException as e:
        app.logger.debug(str(e))
        return HTTP_STAT(400)
    wrapper.__name__ = _func.__name__
    return wrapper
  return _catchError if func is None else _catchError(func)

def getReqJson(k):
  try:
    return request.json[k]
  except KeyError:
    raise RequestKeyError(k)

def HTTP_STAT(stat):
  return  (jsonify({'state': 'success'}), 200) if stat == 200 else \
          (jsonify({'error': 'Bad Request'}), 400) if stat == 400 else \
          (jsonify({'error': 'Unauthorized'}), 401) if stat == 401 else \
          (jsonify({'error': 'Forbidden'}), 403) if stat == 403 else \
          (jsonify({'error': 'Not Found'}), 404) if stat == 404 else \
          (jsonify({'error': 'Internal Server Error'}), 500)

__all__ = ['api', 'manage', 'test']
