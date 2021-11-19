from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from extract import Extract
from pdfminer.high_level import extract_text
import os
import shutil

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["POST", "GET"])
def upload():
    data = []
    if request.method == "POST":
        files = request.files.getlist("file[]")
        for file in files:
            tempdata = {}
            filename = secure_filename(file.filename)
            tempdata["filename"] = filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            Extract(filepath, tempdata)
            os.unlink('uploads/' + filename)
            data.append(tempdata)
    print("Data", data)
    return render_template('home.html', data=data)
