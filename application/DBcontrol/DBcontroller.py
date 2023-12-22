import mysql.connector

class MysqlOperator:
  def __init__(self, user:str, host:str, database:str, password:str=None):
    self.user = user
    self.host = host
    self.database = database
    self.con = None

    if password is not None:
      self.start_connection(password=password)

  @classmethod
  def connect_mysql(self, user:str, password:str, host:str, database:str):
    con = mysql.connector.connect(user=user, password=password, host=host, database=database)
    
    if not con.is_connected():
      raise Exception("Failed to connect to MySQL server")

    con.ping(reconnect=True)
    con.autocommit = False

    return con

  def __del__(self):
    self.close_connection()

  def start_connection(self, password:str):
    self.con = mysqlOperator.connect_mysql(user=self.user, password=password, host=self.host, database=self.database)

  def close_connection(self):
    self.con.close()
    self.con = None

  def commit(self):
    self.con.commit()
  def rollback():
    self.con.rollback()

  def query(self, stmt, commit=False, args=None, many=False, prepared=True, **kwargs):
    try:
      cur = self.con.cursor(prepared=prepared, **kwargs)
      exefunc = cur.executemany if many else cur.execute
      if args is None:
        exefunc(stmt)
      else:
        if not args:
          return []
        exefunc(stmt, args)

      res = cur.fetchall()
      if commit:
        self.commit()
    except Exception as e:
      self.rollback()
      raise e
    finally:
      cur.close()
    return res

