import requests

# 看空看多
# https://vote.eastmoney.com/voteapi/Handlers/ViewVoteResultHandler.ashx?callback=jQuery35105476083748663809_1732710053574&VoteOptionID=1&_=1732710053575
# 持仓
# https://vote.eastmoney.com/voteapi/Handlers/ViewVoteResultHandler.ashx?callback=jQuery35105476083748663809_1732710053576&VoteOptionID=2&_=1732710053577

#机构看多
# https://quote.eastmoney.com/newapi/jgdc

def jgkd():
    url = "https://quote.eastmoney.com/newapi/jgdc"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url,  headers=headers)
    codes2 = response.json()
    return {
        "up": codes2[0],
        "flat": codes2[1],
        "down": codes2[2],
    }

def kanduo():
    url = "https://vote.eastmoney.com/voteapi/Handlers/ViewVoteResultHandler.ashx?callback=&VoteOptionID=1&_=1732710053575"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url,  headers=headers)
    codes2 = response.json()
    return {
        "up": codes2["VoteOptions"][0]["OptionCounter"],
        "flat": codes2["VoteOptions"][1]["OptionCounter"],
        "down": codes2["VoteOptions"][2]["OptionCounter"],
    }


def chicang():
    url = "https://vote.eastmoney.com/voteapi/Handlers/ViewVoteResultHandler.ashx?callback=&VoteOptionID=2&_=1732710053577"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url,  headers=headers)
    codes2 = response.json()
    return {
        "70": codes2["VoteOptions"][0]["OptionCounter"], #持仓大于70
        "30": codes2["VoteOptions"][1]["OptionCounter"], #持仓大于30
        "0": codes2["VoteOptions"][2]["OptionCounter"], #持仓大于0
    }
