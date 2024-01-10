
from mysql.connector import Error
from .. import app
from flask import jsonify

def catchError(func):
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Error as e:
      app.logger.warning(str(e))
      return jsonify({'error': 'SQLError'}), 400
  wrapper.__name__ = func.__name__
  return wrapper


def HTTP_STAT(stat):
  return  (jsonify({'state': 'success'}), 200) if stat == 200 else \
          (jsonify({'error': 'Bad Request'}), 400) if stat == 400 else \
          (jsonify({'error': 'Unauthorized'}), 401) if stat == 401 else \
          (jsonify({'error': 'Forbidden'}), 403) if stat == 403 else \
          (jsonify({'error': 'Not Found'}), 404) if stat == 404 else \
          (jsonify({'error': 'Internal Server Error'}), 500)

__all__ = ['api', 'test']
