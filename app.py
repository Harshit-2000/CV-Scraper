from flask import Flask, render_template, request, jsonify
from flask.helpers import url_for
from werkzeug.utils import redirect, secure_filename
from werkzeug.wrappers.response import Response
from extract import Extract
import os
import json
import csv


UPLOAD_FOLDER = os.path.dirname(
    os.path.abspath(__file__)) + '/uploads/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["POST", "GET"])
def upload():
    data = []
    if request.method == "POST":
        keywordFile = request.form.get('keyword')

        files = request.files.getlist("files[]")

        for file in files:
            if file.filename == '':
                continue
            tempdata = {}
            filename = secure_filename(file.filename)
            tempdata["filename"] = filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            Extract(filepath, tempdata, keywordFile)
            os.unlink('uploads/' + filename)
            data.append(tempdata)

    try:
        field_names = data[0].keys()
        with open('data/data.csv', mode='w', encoding="utf-8") as csvfile:
            csvfile.truncate(0)
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(e)

    # return jsonify(data)
    return render_template('home.html', data=data)


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
    data = {}
    data['keyword1'] = open('uploads/keyword1.txt', mode='r').read()
    data['keyword2'] = open('uploads/keyword2.txt', mode='r').read()
    data['keyword3'] = open('uploads/keyword3.txt', mode='r').read()
    if request.method == 'POST':
        keywordFile = request.form.get('keyword')
        file = request.files.get('file')

        if file.filename[-3:] != 'txt':
            return Response(json.dumps({'message': 'Only .txt files allowed'}), status=406, mimetype='application/json')
        try:
            if keywordFile == '1':
                filepath = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'keyword1.txt')
            elif keywordFile == '2':
                filepath = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'keyword2.txt')
            elif keywordFile == '3':
                filepath = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'keyword3.txt')

            file.save(filepath)

            data['keyword1'] = open('uploads/keyword1.txt', mode='r').read()
            data['keyword2'] = open('uploads/keyword2.txt', mode='r').read()
            data['keyword3'] = open('uploads/keyword3.txt', mode='r').read()

        except Exception as e:
            print(e)
            return Response(json.dumps({'message': 'Error'}), status=500, mimetype='application/json')

    return render_template('addKeyword.html', data=data)
    # return Response(data, status=200, mimetype='application/json')


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    pass


@app.route('/downloadCSV')
def downloadCSV():
    file = open('data/data.csv', mode='r', encoding="utf-8").read()
    return Response(
        file,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=data.csv"})
