#!/usr/bin/python3
# -*- coding:UTF-8 -*-
import pymongo as pm
import datetime
from collections import Counter

# 以小时为间隔，统计每个小时每个统计量的情况
def statsByHour():
    client = pm.MongoClient('mongodb://jizhi:pwd123@127.0.0.1:27017/statistic_result')
    db = client.statistic_result
    col = db.statsByHour
    stat = db.stat
    newTime = datetime.datetime.utcnow()  # utc format
    oldTime = datetime.datetime.utcnow() - datetime.timedelta(days=3)  # utc format
    latestDate1 = datetime.datetime(oldTime.year, oldTime.month, oldTime.day, oldTime.hour, 0, 0)  # utc format
    latestDate2 = datetime.datetime(newTime.year, newTime.month, newTime.day, newTime.hour, 0, 0)  # utc format
    for keyword in ['regionInfo', 'cityInfo', 'accessBrowser', 'accessPlatform', 'accessSource',
                    'accessNum','uniqIpNum','uniqUserNum']:
        s = stat.aggregate([{'$match': {'accessTime': {'$gte': latestDate1, '$lte': latestDate2}}},
                            {'$project': {'_id': 0, keyword: 1, 'accessTime': {
                                '$dateToString': {'format': '%Y-%m-%d %H:00', 'date': '$accessTime',
                                                  'timezone': '+08:00'}}}},
                            {'$sort': {'accessTime': 1}}])

        output = list(s)
        accessTime = [a['accessTime'] for a in output]
        if keyword in ['regionInfo', 'cityInfo', 'accessBrowser', 'accessPlatform', 'accessSource']:
            processedData = dateProcess1(keyword, output, accessTime)
            #print(processedData)
        else:
            processedData = dateProcess2(keyword, output, accessTime)
            #print(processedData)
        # 只插入原有数据库中不存在的数据，避免重复
        if not list(col.find({'timeId': processedData['timeId'],'keyword':processedData['keyword']})):
            col.insert_one(processedData)

# 以天为间隔，统计每天每个统计量的情况
def statsByDay():
    client = pm.MongoClient('mongodb://jizhi:pwd123@127.0.0.1:27017/statistic_result')
    db = client.statistic_result
    col = db.statsByDay
    stat = db.stat
    newTime = datetime.datetime.now() - datetime.timedelta(days=1)
    oldTime = datetime.datetime.now() - datetime.timedelta(days=8)
    # utc format
    latestDate1 = datetime.datetime(oldTime.year, oldTime.month, oldTime.day, 16, 0, 0)
    # utc format  相差8小时，查询前先进行时区转化
    latestDate2 = datetime.datetime(newTime.year, newTime.month, newTime.day, 16, 0, 0)
    for keyword in ['regionInfo', 'cityInfo', 'accessBrowser', 'accessPlatform', 'accessSource',
                    'accessNum', 'hashUserIp', 'hashUserId']:
        if keyword in ['hashUserIp', 'hashUserId']:
            s = stat.aggregate([{'$match': {'accessTime': {'$lte': latestDate2, '$gt': latestDate1}}},
                                {'$unwind': '$' + keyword},
                                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$accessTime',
                                                                      'timezone': '+08:00'}},
                                            keyword: {'$addToSet': '$' + keyword}}},
                                {'$unwind': '$' + keyword},
                                {'$group': {'_id': '$_id', keyword: {'$sum': 1}}},
                                {'$sort': {'_id': 1}}])
            output = list(s)
            accessTime = [a['_id'] for a in output]
            processedData = dateProcess2(keyword,output,accessTime)
            #print(processedData)

        elif keyword in ['accessNum']:
            s = stat.aggregate([{'$match': {'accessTime': {'$lte': latestDate2, '$gt': latestDate1}}},
                                {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$accessTime',
                                                                      'timezone': '+08:00'}},
                                            keyword: {'$sum': '$' + keyword}}},
                                {'$sort': {'_id': 1}}])
            output = list(s)
            accessTime = [a['_id'] for a in output]
            processedData = dateProcess2(keyword, output, accessTime)
            #print(processedData)

        else:
            s = stat.aggregate([{'$match':{'accessTime':{'$lte':latestDate2,'$gt':latestDate1}}},
                                {'$project': {'_id': 0, keyword: 1, 'accessTime': {
                                    '$dateToString': {'format': '%Y-%m-%d', 'date': '$accessTime',
                                                      'timezone': '+08:00'}}}},
                                {'$unwind':'$'+keyword},
                                {'$sort': {'accessTime': 1}}])
            output = list(s)
            accessTime = []
            for a in output:
                if a['accessTime'] not in accessTime:
                    accessTime.append(a['accessTime'])
            mergedDataList = []
            for time in accessTime:
                accessDatas = [a[keyword] for a in output if a['accessTime'] == time]
                mergedDataDict = {}
                for accessData in accessDatas:
                    mergedDataDict = dict(Counter(mergedDataDict) + Counter(accessData))
                mergedDataList.append({'accessTime':time,keyword:mergedDataDict})
            processedData = dateProcess1(keyword,mergedDataList,accessTime)
            #print(processedData)

        if not list(col.find({'timeId': processedData['timeId'],'keyword':processedData['keyword']})): 
            col.insert_one(processedData)

# 返回echarts需要的数据格式
def dateProcess1(keyword,output,accessTime):
    try:
        accessInfo = [a[keyword][0] for a in output]
    except:
        accessInfo = [a[keyword] for a in output]
    keys = []
    accessNumDict = {}
    totalNumList = []
    # 找到所有的对象名,eg:找到具体有哪些浏览器或具体有哪些访问来源
    for pieceInfo in accessInfo:
        totalNum = 0
        for key in pieceInfo.keys():
            totalNum += pieceInfo[key]
            if key not in keys:
                keys.append(key)
        totalNumList.append(totalNum)

    count = 0
    # 找到各个key对应的时间序列数量值,eg:{chrome:[0.6,0.8,0.3]}
    for pieceInfo in accessInfo:
        for key in keys:
            if key in pieceInfo.keys():
                if key not in accessNumDict.keys():
                    if totalNumList[count] == 0:
                        accessNumDict[key] = [pieceInfo[key]]
                    else:
                        accessNumDict[key] = [round(pieceInfo[key] / totalNumList[count], 2)]
                else:
                    if totalNumList[count] == 0:
                        accessNumDict[key].append(pieceInfo[key])
                    else:
                        accessNumDict[key].append(round(pieceInfo[key] / totalNumList[count], 2))
            else:
                if key not in accessNumDict.keys():
                    accessNumDict[key] = [0]
                else:
                    accessNumDict[key].append(0)
        count += 1

    accessNumDictArray = [{'name': key, 'data': accessNumDict[key],
                           } for key in accessNumDict.keys()]
    try:
        timeId = datetime.datetime.strptime(accessTime[-1],"%Y-%m-%d %H:%M") - datetime.timedelta(hours=8)
    except:
        timeId = datetime.datetime.strptime(accessTime[-1],"%Y-%m-%d")

    return {'timeId':timeId,'keyword':keyword,'accessTime': accessTime, 'data': accessNumDictArray}

# 返回echarts需要的数据格式
def dateProcess2(keyword,output,accessTime):
    if keyword == 'hashUserIp':
        name = 'uniqIpNum'
    elif keyword == 'hashUserId':
        name = 'uniqUserNum'
    else:
        name = keyword
    accessNumDictArray = [{'data': [a[keyword] for a in output],'name': name}]
    try:
        timeId = datetime.datetime.strptime(accessTime[-1],"%Y-%m-%d %H:%M")- datetime.timedelta(hours=8)
    except:
        timeId = datetime.datetime.strptime(accessTime[-1],"%Y-%m-%d")

    return {'timeId':timeId,'keyword':keyword,'accessTime': accessTime, 'data': accessNumDictArray}

if __name__ =='__main__':
    statsByHour()
    statsByDay()