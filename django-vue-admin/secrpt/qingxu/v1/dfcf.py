import requests
from qingxu import config
import datetime


# 看空看多
# https://vote.eastmoney.com/voteapi/Handlers/ViewVoteResultHandler.ashx?callback=jQuery35105476083748663809_1732710053574&VoteOptionID=1&_=1732710053575
# 持仓
# https://vote.eastmoney.com/voteapi/Handlers/ViewVoteResultHandler.ashx?callback=jQuery35105476083748663809_1732710053576&VoteOptionID=2&_=1732710053577

# 机构看多
# https://quote.eastmoney.com/newapi/jgdc

def jgkd():
    url = "https://quote.eastmoney.com/newapi/jgdc"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
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
    response = requests.get(url, headers=headers)
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
    response = requests.get(url, headers=headers)
    codes2 = response.json()
    return {
        "up": codes2["VoteOptions"][0]["OptionCounter"],  # 持仓大于70
        "flat": codes2["VoteOptions"][1]["OptionCounter"],  # 持仓大于30
        "down": codes2["VoteOptions"][2]["OptionCounter"],  # 持仓大于0
    }


def queryId(cursor, tid, type, created_at):
    cursor.execute(
        'SELECT id FROM m_dfcf WHERE tid=%s AND type=%s AND created_at = %s ORDER BY id DESC LIMIT 1',
        (tid, type, created_at)
    )

    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    return values['id']


def saveData(cursor, id, item):
    if id == 0:
        cursor.execute(
            'INSERT INTO m_dfcf (tid, kd_up, kd_flat, kd_down, jg_up, jg_flat, jg_down, cc_up, cc_flat, cc_down, type, created_at) ' +
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (id,
             item['kd_up'], item['kd_flat'], item['kd_down'],
             item['jg_up'], item['jg_flat'], item['jg_down'],
             item['cc_up'], item['cc_flat'], item['cc_down'],
             1, item['created_at'])
        )
    else:
        cursor.execute(
            'UPDATE m_dfcf SET ' +
            'kd_up = %s, kd_flat = %s, kd_down = %s, ' +
            'jg_up = %s, jg_flat = %s, jg_down = %s, ' +
            'cc_up = %s, cc_flat = %s, cc_down = %s ' +
            'WHERE id = %s',
            (item['kd_up'], item['kd_flat'], item['kd_down'],
             item['jg_up'], item['jg_flat'], item['jg_down'],
             item['cc_up'], item['cc_flat'], item['cc_down'],
             id))


def run(cursor):
    if datetime.date.today().weekday() > 4:
        return

    jd = jgkd()  # 机构持仓
    kd = kanduo()  # 看多
    cc = chicang()  # 看
    created_at = datetime.date.today().strftime("%Y-%m-%d")
    id = queryId(cursor, "1", 1, created_at)
    saveData(cursor, id, {
        "kd_up": jd["up"],
        "kd_flat": jd["flat"],
        "kd_down": jd["down"],
        "jg_up": kd["up"],
        "jg_flat": kd["flat"],
        "jg_down": kd["down"],
        "cc_up": cc["up"],
        "cc_flat": cc["flat"],
        "cc_down": cc["down"],
        "created_at": created_at,
    })
    pass


def queryCommitPoint(cursor, created_at):
    cursor.execute(
        'SELECT * FROM m_dfcf WHERE created_at = %s ORDER BY id DESC LIMIT 1',
        (created_at,)
    )
    values = cursor.fetchall()
    if len(values) == 0:
        return {
            "kd": 0,
            "jg": 0,
            "cc": 0,
        }
    values = values[0]
    return {
        "kd": (values["kd_up"] - values["kd_down"]) / (values["kd_up"] + values["kd_flat"] + values["kd_down"]),
        "jg": (values["jg_up"] - values["jg_down"]) / (values["jg_up"] + values["jg_flat"] + values["jg_down"]),
        "cc": (values["cc_up"] - values["cc_down"]) / (values["cc_up"] + values["cc_flat"] + values["cc_down"]),
    }
