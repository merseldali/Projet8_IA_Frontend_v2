import os

import io
import base64

from flask import Flask, flash, jsonify, render_template, request
import requests

import zipfile

app = Flask(__name__)

app.secret_key = "secret key"  # for encrypting the session
# It will allow below 16MB contents only, you can change it
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index(image_id=""):
    predicted_img, labels_img, raw_img = (
        None,
        None,
        None,
    )

    if request.args.get("image_id"):
        resp = requests.get("https://p8ai-api.herokuapp.com/segmentation/"+request.args.get("image_id"))
        print('ok api')
        if resp.status_code == 200:
            data = resp.content
            s = io.BytesIO(data)
            zf = zipfile.ZipFile(s)
            print(zf.namelist())
            raw_img = base64.b64encode(zf.read('raw.png'))
            predicted_img = base64.b64encode(zf.read('predicted.png'))
            labels_img = base64.b64encode(zf.read('labels.png'))
            print('success')

        else:
            flash('Error calling external API : ' + str(resp.status_code))

    return render_template(
        "index.html",
        image_id=image_id,
        predicted_img=predicted_img.decode('utf-8') if predicted_img is not None else None,
        labels_img=labels_img.decode('utf-8') if labels_img is not None else None,
        raw_img=raw_img.decode('utf-8') if raw_img is not None else None,
    )


if __name__ == '__main__':
    app.run()
