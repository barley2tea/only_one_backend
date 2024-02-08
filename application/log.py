from application import app
from werkzeug.serving import WSGIRequestHandler
from werkzeug.urls import uri_to_iri
import logging
import flask
import os
# change WSGIRequestHandler.log_request

# --handler--
# app_handler
# weakzeug_handler
# bots_handler

# --logger--
# app.logger
# weakzeug_logger
# bot_logger

# --class--
# AppLogFormatter

DEFAULT_LOG_FORMAT = '[%(asctime)s] %(levelname)-8s %(name)s in %(module)s: %(message)s'
APP_LOG_FORMAT = '[%(asctime)s] %(levelname)-8s %(name)s in %(module)s %(remote_addr)s \"%(url)s\": %(message)s'

class AppLogFormatter(logging.Formatter):
  def format(self, record):
    if flask.has_request_context():
      record.url = flask.request.url
      record.remote_addr = flask.request.remote_addr
    else:
      record.url = '-'
      record.remote_addr = '-'
    return super().format(record)

str2logLevel = lambda x:  logging.DEBUG if x == 'debug' else logging.INFO  if x == 'info'  else logging.WARNING if x == 'warning' else logging.ERROR if x == 'error' else logging.CRITICAL if x == 'critical' else None

app_handler = logging.StreamHandler()
app_handler.setLevel(str2logLevel(os.getenv('APP_LOG_LEVEL', 'info')))
app_handler.setFormatter(AppLogFormatter(APP_LOG_FORMAT))

werkzeug_handler = logging.StreamHandler()
werkzeug_handler.setLevel(str2logLevel(os.getenv('WERKZEUG_LOG_LEVEL', 'info')))
werkzeug_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))

bot_handler = logging.StreamHandler()
bot_handler.setLevel(str2logLevel(os.getenv('BOT_LOG_LEVEL', 'warning')))
bot_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))

app.logger.removeHandler(flask.logging.default_handler)
app.logger.addHandler(app_handler)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addHandler(werkzeug_handler)

bot_logger = logging.getLogger('bot')
bot_logger.addHandler(bot_handler)

def _custom_log_request(self, code="-", size="-"):
  path = uri_to_iri(self.path)
  code = str(code)

  werkzeug_logger.info(
    "\'%(remote_addr)s\' %(command)s %(request_version)s \"%(url)s\" [%(size)s] %(code)s: "
    % {
      'remote_addr': self.address_string(),
      'url': path,
      'size': size,
      'command': self.command,
      'request_version': self.request_version,
      'code': code,
    }
  )

WSGIRequestHandler.log_request = _custom_log_request



