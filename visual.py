# -*- coding: UTF-8 -*-

from preprocess import AccessingData
import pandas as pd
import matplotlib.pyplot as plt
import pyprind

if __name__ == '__main__':
    f = 'stats-20180117-110180.csv'
    rawData = pd.read_csv(f)
    rawData = rawData.loc[range(0, 50000, 10)].reset_index(drop=True)
    bar = pyprind.ProgBar(rawData.iloc[:,0].size)
    for i in range(rawData.iloc[:, 0].size):
        rawData.ix[i, 'date'] = rawData.ix[i, 'date'].split(' ')[0]
        bar.update()

    dates = list(pd.unique(rawData['date']))
    grouped = rawData.groupby('date')
    accessNum,ipNum,userNum = dict(),dict(),dict()
    for date in dates:
        accessData = AccessingData(grouped.get_group(date).reset_index(drop=True))
        accessNum[date] = accessData.getAccessNumber()
        ipNum[date] = accessData.getUniqueIpNum()
        userNum[date] = accessData.getUserNum()

    fig,(ax1,ax2) = plt.subplots(2,1)
    ax1.plot(accessNum.keys(),accessNum.values(),label='accessNum')
    ax1.plot(ipNum.keys(),ipNum.values(),label='ipNum')
    ax1.set(xlabel = 'date',ylabel = 'total num',
           title = 'The total mount of access and ip')
    ax1.legend(loc='upper left')

    ax2.plot(userNum.keys(),userNum.values(),label='userNum')
    ax2.set(xlabel = 'date',ylabel = 'total num',
           title = 'The total access mount of registered user')
    ax2.legend(loc='upper left')
    plt.show()


    accessData = AccessingData(rawData)
    countryInfo,cityInfo = accessData.getSite()
    plt.figure()
    plt.subplot(211)
    countryAccessNum = [value for value in countryInfo.values() if value >= sorted(list(countryInfo.values()))[-5]]
    countryAccessLabel = [key for key in countryInfo.keys() if countryInfo[key] >= sorted(list(countryInfo.values()))[-5]]
    plt.pie(countryAccessNum,labels=countryAccessLabel,shadow=True,autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('different country access num')

    plt.subplot(212)
    cityAccessNum = [value for value in cityInfo.values() if value >= sorted(list(cityInfo.values()))[-5]]
    cityAccessLabel = [key for key in cityInfo.keys() if cityInfo[key] >= sorted(list(cityInfo.values()))[-5]]
    plt.pie(cityAccessNum,labels=cityAccessLabel,shadow=True,autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('different city access num')
    plt.show()

    accessDevice = accessData.getAccessDevice()
    plt.figure()
    plt.subplot(211)
    plt.pie([accessDevice['windows'],accessDevice['linux'],accessDevice['mac'],accessDevice['mobile']],
            labels= ['windows','linux','mac','mobile'],shadow=True,autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('different platforms')
    
    plt.subplot(212)
    plt.pie([accessDevice['chrome'], accessDevice['ie'], accessDevice['firefox'], accessDevice['otherBrowser']],
            labels=['chrome', 'ie', 'firefox', 'otherBrowser'], shadow=True,autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('different browsers')
    plt.show()

    accessSource = accessData.getAccessSource()
    plt.figure()
    plt.pie(accessSource.values(),labels=accessSource.keys(),shadow=True,autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('accessSource')
    plt.show()