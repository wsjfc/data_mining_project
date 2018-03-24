#!/usr/bin/python3
# -*- coding:UTF-8 -*-
from preprocess import AccessingData
import pymongo as pm
import pandas as pd
import datetime

def readMongo(timeInterval):
    client = pm.MongoClient('mongodb://betatest:Jizhi1024test@139.199.22.219:27017/test')
    db = client.test
    col = db.stats
    if timeInterval == 'day':
        # utc time
        newTime = list(col.aggregate([{'$project':{'_id': 0, 'date': 1}},
                                      {'$sort':{'date':1}}]))[-1]['date']
        oldTime = newTime - datetime.timedelta(days=30)
        latestDate1 = datetime.datetime(oldTime.year, oldTime.month, oldTime.day, 0, 0, 0)
        # 找到最新的时间区间（精度到day）/前一天
        latestDate2 = datetime.datetime(newTime.year,newTime.month,newTime.day,newTime.hour,0,0)

    if timeInterval == 'hour':
        newTime = list(col.aggregate([{'$project': {'_id': 0, 'date': 1}},
                                      {'$sort': {'date': 1}}]))[-1]['date']        # utc time
        oldTime = newTime - datetime.timedelta(hours=1)
        latestDate1 = datetime.datetime(oldTime.year, oldTime.month, oldTime.day, oldTime.hour, 0, 0)
        latestDate2 = datetime.datetime(newTime.year, newTime.month, newTime.day, newTime.hour, 0,0)  # 找到最新的时间区间（精度到day）/前一小时
    cursor = col.find({'date':{'$gte':latestDate1,'$lte':latestDate2}},{'_id':0,'url':0,'__v':0})
    df = pd.DataFrame(list(cursor))
    client.close()

    return df

def statInfo(timeInterval):
    # 每小时运行一次统计上一个小时的数据
    if timeInterval == 'hour':
        rawData = readMongo('hour')
        accessData = AccessingData(rawData)
        # data is utc format
        newTime = rawData['date'].values[-1]
        oldTime = newTime - datetime.timedelta(hours=1)
        # time向上取整
        accessTime = datetime.datetime(oldTime.year, oldTime.month, oldTime.day, oldTime.hour, 0, 0)
        saveInMongodb(accessTime,accessData)

    #每天运行一次，统计上一天的数据
    elif timeInterval == 'day':
        rawData = readMongo('day')
        # 对时间向上取整
        rawData['newdate'] = rawData['date'].apply(lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour,0 ,0)) #以小时为间隔统计
        # utc format
        times = list(pd.unique(rawData['newdate']))
        grouped = rawData.groupby('newdate')
        for accessTime in times:
            accessData = AccessingData(grouped.get_group(accessTime).reset_index(drop=True))
            accessTime = accessTime.astype('M8[s]').astype('O')
            saveInMongodb(accessTime,accessData)

def saveInMongodb(accessTime,accessData):
    statisticData = {
        # utc format
        'accessTime': accessTime,
        'accessNum': accessData.getAccessNumber(),
        'uniqIpNum': accessData.getUniqueIpNum(),
        'uniqUserNum': accessData.getUserNum(),
        'accessSource': [accessData.getAccessSource()],
        'regionInfo': [accessData.getSite()[0]],
        'cityInfo': [accessData.getSite()[1]],
        'accessBrowser': [accessData.getAccessDevice()[0]],
        'accessPlatform': [accessData.getAccessDevice()[1]],
        'hashUserIp': accessData.hashData()[0],
        'hashUserId': accessData.hashData()[1]
    }
    client = pm.MongoClient('mongodb://jizhi:pwd123@127.0.0.1:27017/statistic_result')
    db = client.statistic_result
    col = db.stat
    # 只插入原有数据库中不存在的数据，避免重复
    if not list(col.find({'accessTime': statisticData['accessTime']})):
        col.insert_one(statisticData)
    client.close()
    client = None

if __name__ == '__main__':
    statInfo('day')




