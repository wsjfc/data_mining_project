#!/usr/bin/python3
# -*- coding:UTF-8 -*-
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'statistic_result'
app.config['MONGO_URI'] = 'mongodb://jizhi:pwd123@127.0.0.1:27017/statistic_result'
mongo = PyMongo(app)

@app.route('/stata', methods=['POST'])
def getData():
    para = request.form.to_dict()
    interval = para['interval']
    keyword = para['keyword']
    chartType = para['chartType']
    if interval == 'hour':
        stat = mongo.db.statsByHour
    elif interval == 'day':
        stat = mongo.db.statsByDay
    newTime = list(stat.aggregate([{'$project': {'_id': 0, 'timeId': 1}},
                                       {'$sort': {'timeId': 1}}]))[-1]['timeId']
    s = stat.aggregate([{'$match': {'timeId': newTime, 'keyword': keyword}}])
    output = list(s)[0]
    #print(output)
    if chartType == 'bar':
        accessNumDictArray = [{'data': data['data'], 'type': chartType, 'name': data['name'], 'stack': '总量'} for data in
                              output['data']]
    elif chartType == 'line':
        accessNumDictArray = [{'data': data['data'], 'type': chartType, 'name': data['name']}for data in output['data']]

    return jsonify({'accessTime': output['accessTime'], 'data': accessNumDictArray, 'legend': [data['name'] for data in output['data']]})

if __name__ == '__main__':
    app.run(debug=True)