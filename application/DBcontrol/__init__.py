import os
import json
from application.DBcontrol.DBcontroller import MysqlOperator

default_ope = MysqlOperator(os.getenv('DB_CONFIG_JSON'))

