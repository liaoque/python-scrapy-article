import requests


def getCode(code):
    if len(code) > 6:
        return str(code[0:-3])
    return str(code)


def getToday(today):
    url = "http://81.68.241.227:39001/polls/date/%s" % (today)
    r = requests.get(url)
    return r.json()
