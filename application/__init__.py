
import application.config

import os
import flask
from flask_cors import CORS

app = flask.Flask(__name__)
app.config.from_object(f'application.config.{os.getenv("FLASK_CONFIGURATION", "DefaultConfig")}')

import application.log

CORS(app, supports_credentials=True, resources={r'/api/*' : {'origins': os.getenv("FRONTEND_URL", "http://localhost:3000"), 'methods': ['GET', 'POST']}})

