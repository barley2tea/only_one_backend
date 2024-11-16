# 1日単位でデータを集計し、結果をparsedIoTDataテーブルへINSERTする。
# データの存在しない区間は最後のデータから25分までは最後のデータが続いているものとする。
# 1日の始まりから最初のデータまではデータが存在しないものとして扱われる
# OSの機能で毎日0時に実行させる

import mysql.connector
import datetime as dt
import pytz
import pandas as pd
from copy import copy
# stmt0 = "SELECT MAX(T.time) + INTERVAL %(span)s MINUTE AS stime, MAX(T.time) + INTERVAL %(span)s MINUTE + INTERVAL 1 DAY AS etime FROM parsedIoTData AS T;"
stmt0 = "SELECT MAX(T.time) + INTERVAL %(span)s MINUTE AS stime FROM parsedIoTData T;"
# stmt1 = 'SELECT DATE_FORMAT(MIN(T.time),%(tf)s) stime, DATE_FORMAT(DATE(MIN(T.time)), %(tf)s) + INTERVAL 1 DAY etime FROM IoTData T'
stmt1 = 'SELECT MIN(T.time) + INTERVAL %(span)s MINUTE AS stime FROM IoTData T'

# データ(境界値は考えない)の取得
stmt2 = """
SELECT
  T1.time AS o_time,
  T1.dataStatus,
  DATE_SUB(T1.time, INTERVAL MINUTE(T1.time) % %(span)s MINUTE) - INTERVAL SECOND(T1.time) SECOND AS time,
  T1.dataStatus * TIME_TO_SEC( TIMEDIFF( LEAD(T1.time, 1, %(etime)s) OVER(PARTITION BY T1.IoTID ORDER BY T1.time), T1.time)) AS value,
  FLOOR((HOUR(T1.time) * 60 + MINUTE(T1.time)) / %(span)s) AS sector,
  T1.IoTID
FROM IoTData AS T1
WHERE
  ( %(etime)s IS NULL OR T1.time < %(etime)s )
  AND ( %(stime)s IS NULL OR T1.time >= %(stime)s)
ORDER BY T1.time;
"""

stmt3 = "INSERT INTO parsedIoTData(`time`, `value`, `sector`, `IoTID`) VALUE(%(time)s, %(value)s, %(sector)s, %(IoTID)s);"

parsedUser = {
  "user": "parsedInserter",
  "host": "localhost",
  "password": "password3",
  "database": "only1DB"
}

tf = "%Y-%m-%d %H:%i:%s"
span = 5
span_time = dt.timedelta(minutes=span)
LOOP_LIMIT = 5

con = mysql.connector.connect(**parsedUser)
def query(stmt, params=None, many=False, commit=False):
  with con.cursor(prepared=True, dictionary=True) as cur:
    if many:
      cur.executemany(stmt, params)
    else:
      cur.execute(stmt, params)
    if commit:
      con.commit()
    return cur.fetchall()


# parsedIoTDataに登録されたデータが最も最新の時刻を取得する
stime = query(stmt0, {"span": span})[0]['stime']
if stime is None:
  stime = query(stmt1, {"span": span})[0]['stime']
  stime -= dt.timedelta(minutes=stime.minute % span, seconds=stime.second)

etime = copy(stime) - dt.timedelta(hours=stime.hour, minutes=stime.minute) + dt.timedelta(days=1)

def insert_data(stime, etime):
  def new_dict(copy_dict, ta, status):
    copy_dict.update({
      'time': ta,
      'o_time': ta,
      'sector': int((ta.hour * 60 + ta.minute) / 5),
      'value': status * span_time.total_seconds()})
    return copy_dict

  dat = query(stmt2, {"stime": stime, "etime": etime, "span": span, "tf": tf})
  # print("-----dat-----")
  # for d in dat:
  #   print({ k: str(v) for k, v in d.items() })
  if len(dat) == 0:
    return etime, etime + dt.timedelta(days=1)

  buf = dict()
  add_list = list()
  for i, d in enumerate(dat):
    b = buf.get(d['IoTID'], None)
    buf[d['IoTID']] = i
    if b is not None and d['time'] > dat[b]['time'] and d['o_time'] != d['time']:
      status = dat[b]['dataStatus']
      ta, tb = dat[b]['time'] + span_time, dat[b]['o_time']
      dat[b]['value'] = status * (ta - tb).total_seconds()
      loopNo = 0
      while ta <= d['time'] and loopNo < LOOP_LIMIT:
        add_list.append(new_dict(d.copy(), ta, status))
        tb, ta = ta, ta + span_time
        loopNo += 1

      if add_list[-1]['time'] == ta:
        add_list[-1]['value'] = status * (d['o_time'] - ta).total_seconds()

  # print("-----exe1-----")
  # for d in dat:
  #   print({ k: str(v) for k, v in d.items() })
  # print()
  # for d in add_list:
  #   print({ k: str(v) for k, v in d.items() })

  for i in buf.values():
    ta, tb = dat[i]['time'] + span_time, dat[i]['o_time']
    if ta < etime:
      dat[i]['value'] = dat[i]['dataStatus'] * (ta - tb).total_seconds()
      loopNo = 0
      while ta < etime and loopNo < LOOP_LIMIT:
        add_list.append(new_dict(dat[i].copy(), ta, dat[i]['dataStatus']))
        tb, ta = ta, ta + span_time
        loopNo += 1

  dat.extend(add_list)

  # print("-----exe2-----")
  # for d in dat:
  #   print({ k: str(v) for k, v in d.items() })

  dat = { k: [ dat[i][k] for i in range(len(dat)) ] for k in dat[0].keys() if k in ('time', 'value', 'sector', 'IoTID')}

  dat = pd.DataFrame(dat).dropna(subset='value')
  dat_parsed = dat.groupby(['time', 'IoTID', 'sector']).sum()
  dat_parsed['value'] /= 300
  dat_parsed = dat_parsed['value'].to_dict()
  ins_args = [ {'time': k[0].to_pydatetime(), 'sector': k[2], 'value': v, 'IoTID': k[1] } for k, v in dat_parsed.items() ]

  # print("-----result-----")
  # for d in ins_args:
  #   print({ k: str(v) for k, v in d.items() })
  query(stmt3, ins_args, many=True, commit=True)

  return etime, etime + dt.timedelta(days=1)

now = dt.datetime.now(pytz.timezone('Asia/Tokyo')).replace(tzinfo=None)
while etime <= now:
  stime, etime = insert_data(stime, etime)

con.close()
