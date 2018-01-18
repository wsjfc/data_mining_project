# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import concurrent.futures
import urllib
import re
import random
import json

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
        userIps = list(self.rawData['userip'].dropna().values)
        sampleIps = random.sample(userIps,len(userIps)//20)
        countryDict,cityDict = dict(),dict()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_url = {executor.submit(self._urlOpen, url): url for url in sampleIps}
            for key in future_to_url.keys():
                try:
                    site = key.result()
                    if site['country_name'] in countryDict.keys():
                        countryDict[site['country_name']] = countryDict[site['country_name']] + 1
                    else:
                        countryDict[site['country_name']] = 1

                    if site['region_name'] in cityDict.keys():
                        cityDict[site['region_name']] = cityDict[site['region_name']] + 1
                    else:
                        cityDict[site['region_name']] = 1
                except:
                    pass
        cityDict.pop('')

        return countryDict,cityDict

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
            return siteDict
        except:
            print('URLERROR')

        #print(html)

    def getAccessDevice(self):
        useragents = self.rawData['useragent'].dropna().values
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
                if url.split('.')[-1] == 'cn' and url.split('.')[-2] == 'com':
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
            if len(key) <2 or key[0]<'9':
                dropKey.append(key)
        for key in dropKey:
            source.pop(key)

        return source



