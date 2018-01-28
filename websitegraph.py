import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import pyprind
from preprocess import AccessingData
from plotly.offline.offline import _plot_html
from plotly.graph_objs import *
import random
import datetime

if __name__ == '__main__':
    plotly.tools.set_credentials_file(username='jfc', api_key='qNFJR2HxHYxnUZXpuTkk')
    #f = 'stats-20180117-110180.csv'
    #rawData = pd.read_csv(f)
    rawData = pd.read_json('stats.json', orient='split')
    rawData = rawData.loc[random.sample(range(0, 50000),5000)].reset_index(drop=True)
    bar = pyprind.ProgBar(rawData.iloc[:,0].size)
    for i in range(rawData.iloc[:, 0].size):
        rawData.ix[i, 'timestamp'] = rawData.ix[i, 'date'].round('h')
        #ts = rawData.ix[i, 'newdate']
        #print(ts.to_datetime())
        #rawData.ix[i, 'newdate'] = rawData.ix[i, 'newdate'].to_datetime()
        bar.update()
        #print(type(rawData.ix[i,'newdate']))
    #rawData['newdate'] = rawData['timestamp'].apply(lambda x: datetime.date(x.year, x.month, x.day))
    '''
    for i in range(rawData.iloc[:, 0].size):
        rawData.ix[i, 'date'] = rawData.ix[i, 'date'].split(' ')[0]
        bar.update()
    '''
    accessData = AccessingData(rawData)
    accessSource = accessData.getAccessSource()
    labels = list(accessSource.keys())
    values = list(accessSource.values())
    trace = go.Pie(labels=labels, values=values)
    data = Data([trace])
    first_plot_url = py.plot(data,filename = 'accessSource', fileopt = 'overwrite', auto_open=False)
    
    regionInfo,cityInfo = accessData.getSite()
    fig = {
        "data": [
            {
                "values": [value for value in regionInfo.values() if value >= sorted(list(regionInfo.values()))[-5]],
                "labels": [key for key in regionInfo.keys() if regionInfo[key] >= sorted(list(regionInfo.values()))[-5]],
                "domain": {"x": [0, .38]},
                "hoverinfo": "label+percent",
                "hole": .35,
                "type": "pie",
                "legendgroup": "groupone",
                "name":'Different regions access per'
            },
            {
                "values": [value for value in cityInfo.values() if value >= sorted(list(cityInfo.values()))[-5]],
                "labels": [key for key in cityInfo.keys() if cityInfo[key] >= sorted(list(cityInfo.values()))[-5]],
                "domain": {"x": [.62, 1]},
                "hoverinfo": "label+percent",
                "hole": .35,
                "type": "pie",
                "legendgroup": "grouptwo",
                "name":"Different cities access per"
            }],
        "layout": {
            "title": "Access num in different regions",
            "legend":dict(x=0.38, y=1.0),
            "annotations": [
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "region",
                    "x": 0.13,
                    "y": 0.5
                },
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "city",
                    "x": 0.85,
                    "y": 0.5
                }
            ]
        }
    }
    second_plot_url = py.plot(fig, filename='region_access_num', fileopt='overwrite',auto_open= False)
    

    #trace = go.Pie(labels=labels, values=values)
    #plot_html, plotdivid, width, height = _plot_html(plot([trace]),False,"",True,'100%',525)
    accessDevice = accessData.getAccessDevice()

    fig = {
        "data": [
            {
                "values": [accessDevice['windows'], accessDevice['linux'], accessDevice['mac'], accessDevice['mobile']],
                "labels": ['windows', 'linux', 'mac', 'mobile'],
                "domain": {"x": [0, .38]},
                "hoverinfo": "label+percent",
                "hole": .35,
                "type": "pie",
                "legendgroup": "groupone",
                "name": 'Different platforms access per'
            },
            {
                "values": [accessDevice['chrome'], accessDevice['ie'], accessDevice['firefox'], accessDevice['otherBrowser']],
                "labels": ['chrome', 'ie', 'firefox', 'otherBrowser'],
                "domain": {"x": [.62, 1]},
                "hoverinfo": "label+percent",
                "hole": .35,
                "type": "pie",
                "legendgroup": "grouptwo",
                "name": "Different browsers access per"
            }],
        "layout": {
            "title": "Access num using different devices or browsers",
            "legend": dict(x=0.4, y=0.7),
            "annotations": [
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "device",
                    "x": 0.14,
                    "y": 0.5
                },
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "browser",
                    "x": 0.87,
                    "y": 0.5
                }
            ]
        }
    }
    third_plot_url = py.plot(fig, filename='devices_or_browsers_access_num', fileopt='overwrite', auto_open=False)

    times = pd.unique(rawData['timestamp'])
    grouped = rawData.groupby('timestamp')
    accessNum, ipNum, userNum = dict(), dict(), dict()
    for time in times:
        accessData = AccessingData(grouped.get_group(time).reset_index(drop=True))
        time = time.astype('M8[s]').astype('O')
        accessNum[time] = accessData.getAccessNumber()
        ipNum[time] = accessData.getUniqueIpNum()
        userNum[time] = accessData.getUserNum()

    trace1 = go.Scatter(x = sorted(list(accessNum.keys())),y = [accessNum[key] for key in sorted(list(accessNum.keys()))],name = 'totalAccessNum')
    trace2 = go.Scatter(x = sorted(list(ipNum.keys())),y = [ipNum[key] for key in sorted(list(ipNum.keys()))],name ='uniqueIpAccessNum')
    trace3 = go.Scatter(x = sorted(list(userNum.keys())),y = [userNum[key] for key in sorted(list(userNum.keys()))],name='registeredUserAccessNum')
    data = [trace1,trace2,trace3]
    fig = dict(data=data)
    fourth_plot_url = py.plot(fig, filename='access_and_ip_num', fileopt='overwrite', auto_open=False)
    print(fourth_plot_url)

