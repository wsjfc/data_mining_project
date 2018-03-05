import pymongo as pm
import pandas as pd
import pyprind

def csv2mongodbCol(f):
    df = pd.read_csv(f,header=None)
    df = df.replace('-','-1')
    print(df)
    client = pm.MongoClient('mongodb://jizhi:pwd123@127.0.0.1:27017/ip_location')
    db = client.ip_location
    col = db.ip_location
    bar = pyprind.ProgBar(df.iloc[:,0].size)
    for i in range(df.iloc[:,0].size):
        #print(type(str(df.ix[i,0])))
        dic = {'ipStart':int(df.ix[i,0]),'ipEnd':int(df.ix[i,1]),
                'country':str(df.ix[i,3]),'city':str(df.ix[i,4])}
        #print(dic)
        col.insert_one(dic)
        bar.update()

if __name__ == '__main__':
    f = 'IP2LOCATION-LITE-DB3.CSV'
    csv2mongodbCol(f)