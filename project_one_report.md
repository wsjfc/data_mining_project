# 项目一汇报书

## 概述     

已完成：  
1.csv格式数据转成json格式，并读取;  
2.对原始数据进行清洗;  
3.按照要求统计了多个访问量指标;   
4.暂时采用matplotlib绘制出了要求的图表。   

>独立IP数，独立用户数，总访问数以小时为间隔进行统计，其余访问量指标未按特定时间间隔进行统计

## 结果展示

### 不同时间间隔独立IP数、独立用户数、总访问数：

* 代码：

        def getAccessNumber(self):
            accessNumber = self.rawData.iloc[:,0].size

            return accessNumber

        def getUniqueIpNum(self):
            uniqueIpNum = len(pd.unique(self.rawData['userip']))
    
            return uniqueIpNum

        def getUserNum(self):
            userNum = len(pd.unique(self.rawData['userid']))

            return userNum	  

* 示例表格：  

  |时间<sup>1</sup>|总访问数|独立IP数|独立用户数<sup>2</sup>|
  |-----|-----|-----|-----|
  |2017-5-1 00:00|422|214|2|
  |2017-5-1 06:00|744|376|1|
  |2017-5-1 12:00|705|331|3|
  |2017-5-1 18:00|494|259|1|
  |2017-5-2 00:00|521|256|2|
  |2017-5-2 06:00|681|348|1|
  |2017-5-2 12:00|810|337|9|
  |2017-5-2 18:00|867|378|9|
  |2017-5-3 00:00|781|350|3|
  |2017-5-3 06:00|733|354|1|
  |2017-5-3 12:00|860|325|6|
  |2017-5-3 18:00|781|354|9|
  |2017-5-4 00:00|364|138|9|
  >1:采样间隔为小时，仅抽取部分数据进行展示  
  >2:指注册用户访问数

### 主要访问来源占比

* 代码:

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

* 示例表格：  

  |访问来源|访问量<sup>1</sup>|占比(%)|
  |-----|-----|-----|
  |zhihu|734|35.8|
  |jizhi|584|28.5|
  |weibo|388|18.9|
  |csdn|148|7.2|
  |baidu|67|3.3|
  |google|33|1.6|
  |topspeedsnail|30|1.5|
  |ai100|15|0.7|
  |readthedocs|14|0.7|
  |julydeu|13|0.6|
  >1:仅展示访问量大于10的来源

### 主要使用设备占比

* 代码：

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

* 示例表格   
 
  不同操作系统访问量占比
  |操作系统名称|访问量|占比(%)|
  |-----       |----- |-----|
  |windows     |44293 |94.9 |
  |linux       |9     |0    |
  |mac         |409   |0.9  |
  |mobile device|1973 |4.2  |

  不同浏览器访问量占比
  |浏览器名称  |访问量|占比(%)|
  |-----       |----- |-----  |
  |chrome      |8010  |16.8   |
  |firefox     |1033  |2.2    |
  |ie          |35779 |74.9   |
  |OtherBrowser|2954  |6.2    |

### 不同地理位置访问量占比

* 代码：
      
        def getSite(self):
           userIps = list(self.rawData['userip'].dropna().values)
           sampleIps = random.sample(userIps,len(userIps)//50)
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
              try:
                  cityDict.pop('')
              except:
                  pass

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
              print(siteDict)
              return siteDict
           except:
              print('URLERROR')

* 示例表格:   

  不同区域访问数<sup>1</sup>：
  |区域     |访问量   |占比(%)  |
  |-----    |-----    |-----    |
  |CHINA    |63       |75       |
  |CHINA TAIWAN|6     |7.1      |
  |UNITED STATES|9    |10.7     |
  |GERMANY  |2        |2.4      |
  |THAILAND |2        |2.4      |
  |BRAZIL   |2        |2.4      |
  >1:采用随机抽样的方法统计

  不同城市访问数<sup>1</sup>:
  |城市     |访问量   |占比(%)  |
  |-----    |-----    |-----    |
  |GuangDong|10       |22.7     |
  |shangdong|6        |13.6     |
  |zhejiang |13       |29.5     |
  |jiangsu  |5        |11.4     |
  |Beijing  |10       |22.7     |
  >1:采用随机抽样的方法统计
