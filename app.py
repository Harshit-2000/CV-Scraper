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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


if __name__ == '__main__':
    app.run()
