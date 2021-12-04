from flask import Flask, render_template, request, jsonify
from flask.helpers import url_for
from werkzeug.utils import redirect, secure_filename
from werkzeug.wrappers.response import Response
import os
import json
import csv
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = os.path.dirname(
    os.path.abspath(__file__)) + '/uploads/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keywords.db'

db = SQLAlchemy(app)

## MODELS ##


class KeywordFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    file = db.Column(db.LargeBinary(), nullable=False)

    def __repr__(self) -> str:
        return self.name


## VIEWS ##
from extract import Extract


@app.route("/", methods=["POST", "GET"])
def upload():
    data = []
    if request.method == "POST":
        files = request.files.getlist("files[]")

        for file in files:
            if file.filename == '':
                continue
            tempdata = {}
            filename = secure_filename(file.filename)
            tempdata["filename"] = filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            Extract(filepath, tempdata)
            os.unlink('uploads/' + filename)
            data.append(tempdata)

    try:
        field_names = data[0].keys()
        with open('data/data.csv', mode='a', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            if not os.stat('data/data.csv').st_size > 0:
                writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(e)

    # return jsonify(data)
    return render_template('home.html', data=data, files=KeywordFile.query.all())


@app.route('/addname', methods=["POST", "GET"])
def addName():
    if request.method == 'POST':
        name = request.form.get('name')
        try:
            with open('data/names/newNames.txt', mode='a') as file:
                file.write(name + ' ')
            return Response(json.dumps({'message': 'success'}), status=201, mimetype='application/json')
        except Exception as e:
            print(e)
    return redirect(url_for('upload'))


@app.route('/uploadKeywords', methods=['GET', 'POST'])
def uploadKeywords():

    if request.method == 'POST':
        keyword = request.form.get('keyword')
        filename = request.form.get('filename')
        file = request.files.get('file')

        if file.filename[-3:] != 'txt':
            return Response(json.dumps({'message': 'Only .txt files allowed'}), status=406, mimetype='application/json')
        try:

            keyword = KeywordFile(name=filename, file=file.read())
            db.session.add(keyword)
            db.session.commit()

        except Exception as e:
            print(e)
            return Response(json.dumps({'message': 'Error'}), status=500, mimetype='application/json')

    return render_template('addKeyword.html', files=KeywordFile.query.all())
    # return Response(data, status=200, mimetype='application/json')


@app.route('/deleteKeywords/<int:id>')
def deleteKeywords(id):
    try:
        file = KeywordFile.query.get(id)
        db.session.delete(file)
        db.session.commit()
        return redirect(url_for('uploadKeywords'))
    except Exception as e:
        print(e)
        return Response(json.dumps({'message': 'error'}), status=500, mimetype='application/json')


@app.route('/downloadCSV')
def downloadCSV():
    file = open('data/data.csv', mode='r', encoding="utf-8").read()
    return Response(
        file,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=data.csv"})


@app.route('/clearCSV')
def clearCSV():
    try:
        with open('data/data.csv', mode='w', encoding="utf-8") as csvfile:
            csvfile.truncate(0)
        return redirect(url_for('upload'))
    except Exception as e:
        print(e)
        return Response(json.dumps({'message': 'error'}), status=500, mimetype='application/json')


@app.route('/addstopword', methods=['POST', 'GET'])
def addStopwords():
    data = open('data/stopwords/newStopwords.txt', mode='r').read()

    if request.method == 'POST':
        file = request.files.get('file')

        if file.filename[-3:] != 'txt':
            return Response(json.dumps({'message': 'Only .txt files allowed'}), status=406, mimetype='application/json')

        file.save('data/stopwords/newStopwords.txt')
        data = open('data/stopwords/newStopwords.txt', mode='r').read()

    return render_template('uploadStopwords.html', data=data)
