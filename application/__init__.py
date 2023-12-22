
import application.config

import os
import flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = flask.Flask(__name__)
app.config.from_object(f'application.config.{os.getenv("FLASK_CONFIGURATION", "DefaultConfig")}')

import application.log

CORS(app, resources={r'/app/*' : {'origins': ['http://mmm-foktm.ishikawa.kosen-nct.ac.jp'], 'methods': ['GET', 'POST']}})
bcrypt = Bcrypt(app)

