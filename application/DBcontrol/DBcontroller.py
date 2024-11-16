import mysql.connector
from mysql.connector import Error
import threading
import json
import time

class MysqlOperator:
  def __init__(self, config_path:str):
    self.config_path = config_path
    self.con = None
    self.query_lock = threading.Lock()
    self.start_connection(config_path)

  @classmethod
  def connect_mysql(self, user:str, password:str, host:str, database:str):
    for _ in range(10):
      try:
        con = mysql.connector.connect(user=user, password=password, host=host, database=database)
      except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
    if not con.is_connected():
      raise Exception("Failed to connect to MySQL server")
    con.ping(reconnect=True)
    con.autocommit = False
    return con

  @classmethod
  def load_config(self, path:str):
    return json.load(open(path, 'r'))
    
  def __del__(self):
    self.close_connection()

  def start_connection(self, path):
    password = self.set_config(path)
    self.con = MysqlOperator.connect_mysql(user=self.user, password=password, host=self.host, database=self.database)

  def set_config(self, path:str):
    config = MysqlOperator.load_config(path)
    self.user = config['user']
    self.host = config['host']
    self.database = config['database']
    return config['password']

  def close_connection(self):
    self.query_lock.acquire()
    if self.con is not None:
      self.con.close()
      self.con = None
    self.query_lock.release()

  def commit(self):
    self.con.commit()
  def rollback(self):
    self.con.rollback()

  def query(self, stmt:str, commit=False, args=None, many=False, prepared=True, debug=False, **kwargs):
    self.query_lock.acquire()
    try:
      if self.con is None or not self.con.is_connected():
        self.start_connection(self.config_path)
      cur = self.con.cursor(prepared=prepared, **kwargs)
      exefunc = cur.executemany if many else cur.execute
      exefunc(stmt, args) if args else exefunc(stmt)

      if debug:
        print('----executed----')
        print(cur._executed)
        print('----------------')

      res = cur.fetchall()
      if commit:
        self.commit()
    except Exception as e:
      self.rollback()
      raise e
    finally:
      cur.close()
      self.query_lock.release()
    return res

