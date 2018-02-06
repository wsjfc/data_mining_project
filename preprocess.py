# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import concurrent.futures
import pymongo as pm
import re
import random

class AccessingData:
    def __init__(self,data):
        self.rawData = data

    def getAttributeName(self):
        attributeName = list(self.rawData)

        return attributeName

    def getAccessNumber(self):
        accessNumber = self.rawData.iloc[:,0].size

        return accessNumber

    def getUniqueIpNum(self):
        uniqueIpNum = len(pd.unique(self.rawData['userip']))

        return uniqueIpNum

    def getUserNum(self):
        userNum = len(pd.unique(self.rawData['userid']))

        return userNum

    def getSite(self):
        userIps = list(self.rawData[self.rawData['method'] == 'GET']['userip'].dropna().values)
        sampleIps = random.sample(userIps,len(userIps)//100)
        #print(sampleIps)
        regionDict,cityDict = dict(),dict()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {executor.submit(self._getLocation, ip): ip for ip in sampleIps}
            for key in future_to_url.keys():
                try:
                    site = key.result()
                    if site['country'] in regionDict.keys():
                        regionDict[site['country']] = regionDict[site['country']] + 1
                    else:
                        regionDict[site['country']] = 1

                    if site['city'] in cityDict.keys():
                        cityDict[site['city']] = cityDict[site['city']] + 1
                    else:
                        cityDict[site['city']] = 1
                except:
                    pass
        try:
            cityDict.pop('')
        except:
            pass

        return regionDict,cityDict

    def _getLocation(self,ip):
        client = pm.MongoClient('mongodb://jizhi:pwd123@127.0.0.1:27017/ip_location')
        db = client.ip_location
        col = db.ip_location
        ip = ip.split(':')[-1]
        intIp = int(ip.split('.')[0]) * pow(256, 3) + int(ip.split('.')[1]) * pow(256, 2) + int(ip.split('.')[2]) * pow(
            256, 1) + int(ip.split('.')[3]) * pow(256, 0)
        for i in col.aggregate([{'$match': {'ipStart': {'$lte': intIp}, 'ipEnd': {'$gte': intIp}}},
                                {'$project': {'_id': 0, 'country': 1, 'city': 1}}]):

            return i

    '''
    def _urlOpen(self,ip):
        ip = ip.split(':')[-1]
        url = 'http://freegeoip.net/json/' + ip
        req = urllib.request.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                    'Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36')
        try :
            response = urllib.request.urlopen(url, timeout=2)
            html = response.read()
            siteDict = json.loads(html, encoding='utf-8')
            print(siteDict)
            return siteDict
        except:
            print('URLERROR')

        #print(html)
    '''

    def getAccessDevice(self):
        useragents = self.rawData[self.rawData['method'] == 'GET']['useragent'].dropna().values
        count = np.zeros(8)
        for useragent in useragents:
            while True:
                if re.findall('Windows', useragent):
                    count[0] += 1
                    break
                elif re.findall('Android|iPhone', useragent):
                    count[3] += 1
                    break
                elif re.findall('linux', useragent):
                    count[1] += 1
                    break
                elif re.findall('Macintosh', useragent):
                    count[2] += 1
                    break
                break

            while True:
                if re.findall('Chrome', useragent):
                    count[4] += 1
                    break
                elif re.findall('MSIE', useragent):
                    count[5] += 1
                    break
                elif re.findall('Firefox', useragent):
                    count[6] += 1
                    break
                else:
                    count[7] += 1
                    break

        accessDevice = {'windows': count[0], 'linux': count[1], 'mac': count[2], 'mobile': count[3]
            , 'chrome': count[4], 'ie': count[5], 'firefox': count[6], 'otherBrowser': count[7]}

        return accessDevice

    def getAccessSource(self):
        baseurls = self.rawData[self.rawData['method'] == 'GET']['baseurl'].dropna().values
        source = dict()
        for url in baseurls:
            try:
                url = url.split('/')[2]
                if url.split('.')[-2] == 'com':
                    url = url.split('.')[-3]
                else:
                    url = url.split('.')[-2]

                if url in source.keys():
                    source[url] = source[url] + 1
                else:
                    source[url] = 1
            except:
                print(url)
        dropKey = []
        for key in source.keys():
            if len(key) <3 or key[0]<'9':
                dropKey.append(key)
        for key in dropKey:
            source.pop(key)

        return source



