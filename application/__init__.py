
import application.config

import os
import flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = flask.Flask(__name__)
app.config.from_object(f'application.config.{os.getenv("FLASK_CONFIGURATION", "DefaultConfig")}')

import application.log

CORS(app, supports_credentials=True, resources={r'/api/*' : {'origins': os.getenv("FRONTEND_DOMAIN", "http://127.0.0.1:3000"), 'methods': ['GET', 'POST']}})
bcrypt = Bcrypt(app)

