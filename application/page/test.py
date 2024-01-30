from flask import request, jsonify, abort, session, send_file
from application.DBcontrol import default_ope as ope, MysqlOperator
from application.page import catchError
from application import app

GET_DATA_SAVE_FILE = './test./get_data.txt'
SEND_FILE_NAME = './test/send.zip'

@app.route('/test/testDB', methods=['GET'])
def testDB():
  pass

@app.route('/test/show_send', methods=['GET', 'POST'])
def show_send():
  d = request.args if request.method == 'GET' else request.get_data()
  return f'<p>ip address</p><p>{request.remote_addr}</p><p>header</p><p>{request.headers}</p><p>data</p><p>{d}</p>'

@app.route('/test/save_send', methods=['GET', 'POST'])
def save_send():
  d = request.args if request.method == 'GET' else request.get_data()
  with open(GET_DATA_SAVE_FILE, mode='a') as f:
    f.write(d)
    f.write('\n')
  return f'<p>ip address</p><p>{request.remote_addr}</p><p>header</p><p>{request.headers}</p><p>data</p><p>{d}</p>'

@app.route('/test/add_data', methods=['GET'])
def add_data():
  return '''
  <html lang="ja">
  <head>
    <title>add</title>
  </head>
  <h1>form</h1>
  <form action="/" method="POST">
    <input name="n"></input>
    <button type="submit">submit</button>
  </form>
  '''
@app.route('/test/upload_data', methods=['GET', 'POST'])
def get_data():
  if request.method=='POST':
    file = request.files['file']
    file.save('/var/www/flask_app/test/get_data')
    return f'{file.filename}'
  else:
    return '''
    <h1>send file</h1>
    <form action="" method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="uplode">
    </form>
    '''

@app.route('/test/download_data', methods=['GET'])
def send_data():
  fname = 'send_file.zip'
  file = SEND_FILE_NAME
  return send_file(downloadFile, as_attachment=True, attachment_filename=fname, mimetype='application/zip')


