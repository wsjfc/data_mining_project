#!/usr/bin/python3
# -*- coding:UTF-8 -*-
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import datetime

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'statistic_result'
app.config['MONGO_URI'] = 'mongodb://jizhi:pwd123@127.0.0.1:27017/statistic_result'
mongo = PyMongo(app)

@app.route('/stata', methods=['POST'])
def getData():
    para = request.form.to_dict()
    interval = para['interval']
    keyword = para['keyword']
    if interval == 'hour':
        stat = mongo.db.statsByHour
    elif interval == 'day':
        stat = mongo.db.statsByDay
    if 'startTime' not in para.keys():
        newTime = list(stat.aggregate([{'$project': {'_id': 0, 'timeId': 1}},
                                       {'$sort': {'timeId': 1}}]))[-1]['timeId']
        s = stat.aggregate([{'$match': {'timeId': newTime, 'keyword': keyword}}])
        output = list(s)[0]
        # print(output)
        if 'chartType' in para.keys():
            chartType = para['chartType']
            if chartType == 'bar':
                accessNumDictArray = [{'data': data['data'], 'type': chartType, 'name': data['name'], 'stack': '总量'} for
                                      data in
                                      output['data']]
            elif chartType == 'line':
                accessNumDictArray = [{'data': data['data'], 'type': chartType, 'name': data['name']} for data in
                                      output['data']]

            return jsonify({'accessTime': output['accessTime'], 'data': accessNumDictArray,
                            'legend': [data['name'] for data in output['data']]})
        else:
            accessNumDictArray = [{'data': data['data'], 'name': data['name']} for
                                  data in output['data']]

        return jsonify({'accessTime': output['accessTime'], 'data': accessNumDictArray})
    else:
        time1 = datetime.datetime.strptime(para['startTime'],'%Y,%m,%d')
        time2 = datetime.datetime.strptime(para['endTime'],'%Y,%m,%d')
        s = stat.find({'timeId':{'$gte':time1,'$lte':time2},'keyword':keyword},{'_id':0})
        output = list(s)
        accessTime,accessData = [],[{}] * len(output[0]['data'])
        for result in output:
            for i in range(len(result['accessTime'])):
                try:
                    t = datetime.datetime.strptime(result['accessTime'][i],'%Y-%m-%d')
                except:
                    t = datetime.datetime.strptime(result['accessTime'][i], '%Y-%m-%d %H:%M')
                if datetime.datetime.strptime(para['startTime'],'%Y,%m,%d') <= t:
                    if result['accessTime'][i] not in accessTime:
                        accessTime.append(result['accessTime'][i])
                        for j in range(len(result['data'])):
                            try:
                                accessData[j]['data'].append(result['data'][j]['data'][i])
                                accessData[j]['name'] = result['data'][j]['name']
                            except:
                                accessData[j] = {'data': [result['data'][j]['data'][i]],
                                                 'name': result['data'][j]['name']}

    return jsonify({'accessTime':accessTime,'accessData':accessData,'keyword':keyword})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)