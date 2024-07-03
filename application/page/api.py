from application import app, bcrypt
from application.page import catchError, HTTP_STAT
from application.page.prosses import IotProssesing
from application.DBcontrol import default_ope
from flask import request, jsonify

# PROPOSAL
# Collect variables into a buffer and INSERT them periodically in application.bot.
# ---------
# Insert IoTData
@app.route("/", methods=['POST'])
@catchError
def root():
  remote_addr = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
  stmt = 'SELECT T.sendIoTID, T.IoTID FROM `send_iot_info` AS T WHERE T.sendIoTIP = %(IP)s;'
  IoT_info = default_ope.query(str(stmt), args={'IP': str(remote_addr)}, prepared=True, dictionary=True)

  if not IoT_info:
    app.logger.info(f'Unauthorized access. ID:IPaddr[{remote_addr}]')
    return HTTP_STAT(403)

  sendIoT = IoT_info[0]['sendIoTID']
  IoTs = [ i['IoTID'] for i in IoT_info ]

  request_data = request.json if request.headers.get('Content-Type') == 'application/json' else request.get_data()
  args = IotProssesing(sendIoT, IoTs, request_data)
  
  if args is None:
    return HTTP_STAT(500)
  elif isinstance(args, int):
    return HTTP_STAT(400)
  elif not isinstance(args, list):
    app.logger.error(f"Unexpected return value: {args}")
    return HTTP_STAT(500)

  if len(args) == 1:
    args = args[0]
    many = False
  else:
    many = True

  app.logger.debug(f'data: "{"bytes" if len(request_data) > 100 else request_data}" stat:"{args}"')

  stmt = " INSERT INTO `IoTData`(`IoTID`, `dataStatus`) VALUES(%(ID)s, %(stat)s);"

  default_ope.query(stmt, commit=True, args=args, many=many, prepared=True)
  return jsonify({'stat': 'success', 'data': args}), 200


# get latest dashboard data
@app.route('/api/dashboard', methods=['GET'])
@catchError
def dashboad():
  stmt = " SELECT T1.IoTID, T1.dataStatus FROM ( `IoTData` AS T1 NATURAL INNER JOIN ( SELECT T3.IoTID, MAX(T3.time) AS 'time' FROM `IoTData` AS T3 GROUP BY T3.IoTID) AS T2);"
  res = default_ope.query(stmt, dictionary=True)

  def getdata(purpos, place):
    if purpos == 'PB':
      return list(map(lambda x: x['dataStatus'], filter(lambda x: x['IoTID'][:2] == purpos, res)))
    ret = (list(filter(lambda x: x['IoTID'][:4] == f'{purpos}_{place}', res)))
    ret.sort(key=lambda x: int(x['IoTID'][4:]))
    return list(map(lambda x: bool(x['dataStatus']), ret))

  dashboard = {
      "yamaWasherData"    : getdata('WA', 2),
      "umiWasherData"     : getdata('WA', 3),
      "yamaDryerData"     : getdata('DR', 2),
      "umiDryerData"      : getdata('DR', 3),
      "yamaShowerData"    : getdata('SW', 2),
      "umiShowerData"     : getdata('SW', 3),
      "numberOfUsingBathData" : getdata('PB', None)
  }

  return jsonify(dashboard)

