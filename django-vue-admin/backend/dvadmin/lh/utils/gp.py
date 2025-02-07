import requests
import datetime


def getCode(code):
    if len(code) > 6:
        return str(code[0:-3])
    return str(code)


def getTodayLimit(today):
    url = "http://81.68.241.227:39001/polls/date/last/%s" % (today)
    r = requests.get(url)
    return r.json()


def getToday(today):
    url = "http://81.68.241.227:39001/polls/date/%s" % (today)
    r = requests.get(url)
    return r.json()


def saveSort(d, data):
    current_time = datetime.datetime.now().hour
    if current_time < 9 and current_time > 10:
        return

    url = 'http://81.68.241.227:39001/polls/date/stor/save'
    data = {
        "d": d,
        "type": 5,
        "data": data
    }
    response = requests.post(url, json=data)
    print("polls/date/stor/save")
    print(data)
    print(response.json())
    return response.json()
