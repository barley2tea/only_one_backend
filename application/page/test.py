from flask import request, jsonify, abort, session, send_file
from application.DBcontrol import default_ope as ope, iotdata_ope
from application.page import catchError
from application import app
from ultralytics import YOLO
import io
import glob
import numpy as np
from PIL import Image, UnidentifiedImageError
import os

GET_DATA_SAVE_FILE = os.getenv('TEST_DIRECTORY', '.') + '/get_data.txt'
SEND_FILE_NAME = os.getenv('TEST_DIRECTORY', '.') + '/send.zip'
UPLOAD_DATA_FILE = os.getenv('TEST_DIRECTORY', '.') + '/uploaded.zip'

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

@app.route('/test/upload_data', methods=['GET', 'POST'])
def get_data():
  if request.method=='POST':
    file = request.files['file']
    file.save(os.getenv('TEST_DIRECTORY', '.') + '/' + file.filename)
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

@app.route('/test/img_upload', methods=['POST'])
def img_upload():
  data = request.get_data()
  if os.getenv('SAVE_IMAGE', 'False') == 'True':
    test_dir = os.getenv('TEST_DIRECTORY', '.')
    with open(f"{test_dir}/{len(glob.glob(test_dir))}.jpg", 'wb') as f:
      f.write(data)
  return jsonify({'stat': 'success'}), 200
  

@app.route('/test/add_data', methods=['POST'])
def add_data():
  if request.headers.get('Content-Type') == 'application/json':
    request_data = request.json
  else:
    request_data = request.get_data()
    try:
      with Image.open(io.BytesIO(request_data)) as pil_img:
        img = np.asarray(pil_img)
    except UnidentifiedImageError as e:
      raise RequestTypeError(f'Cannt identify image file')

    if not (len(img.shape) == 3 and img.shape[2] == 3):
      raise RequestValueError(f'Bad image. shape={img.shape}')

    if os.getenv('SAVE_IMAGE', 'False') == 'True':
      test_dir = os.getenv('TEST_DIRECTORY', '.')
      num = len(glob.glob(f'{test_dir}/*'))
      with open(f"{test_dir}/{num}.jpg", 'wb') as f:
        f.write(request_data)

    PB_model = YOLO(os.getenv('MODEL_PATH'))
    if PB_model is None:  raise ProssesException('model is not include')
    res = PB_model(img, save=True)[0]
    request_data = {"PB_34": int((len(res.boxes.cls) + 1) // 2)}


  stmt = " INSERT INTO `IoTData`(`IoTID`, `dataStatus`) VALUES(%(ID)s, %(stat)s);"
  for k, v in request_data.items():
    try:
      iotdata_ope.query(stmt, commit=True, args={"ID": k, "stat": v}, prepared=True)
      app.logger.info(f"Insert: ID={k}, stat={v}")
    except Exception as e:
      app.logger.error(f"Test insert error: ID={k}, stat={v}")

  return jsonify({'status': 'success'}), 200

