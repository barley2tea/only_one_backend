import os
import json
from application.DBcontrol.DBcontroller import MysqlOperator

default_ope = MysqlOperator(**json.load(open(os.getenv('DB_CONFIG_JSON'), 'r')))

