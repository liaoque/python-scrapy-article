import requests
import re
# import jieba
# import nltk
import time
# from nltk.corpus import stopwords
import sqlite3
import os
import sys
import json
import MySQLdb  # 修改为 MySQLdb
from MySQLdb.cursors import DictCursor  #

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)

import qingxu.chat.anget as chat
from common.database import getConfig

# nltk.download('stopwords')
# stop_words = set(stopwords.words('chinese'))  # 需要下载中文停用词表


def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)  # 去除多余空格
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    # 进一步清洗可以根据需要添加
    return text

#
# def tokenize(text):
#     return ' '.join(jieba.cut(text))



def commitMsg(msg):
    msg = clean_text(msg)
    # msg = tokenize(msg)
    return msg

def extract_msg(data_str):
    lines = data_str.strip().split('\n')
    for line in lines:
        if line.startswith("data:"):
            # 去掉前缀 "data:" 并去除多余的空格
            json_str = line[len("data:"):].strip()
            if json_str.startswith("{") and json_str.endswith("}"):
                try:
                    data = json.loads(json_str)
                    if isinstance(data, dict) and 'msg' in data:
                        return data['msg']
                except json.JSONDecodeError:
                    continue
    return ""


def reqCreateChat():
    url = "https://yuanbao.tencent.com/api/user/agent/conversation/create"
    headers = {
        "Host": "yuanbao.tencent.com",
        "cookie": "hy_user=34489ef062c24625982e512b51d0dad2; hy_token=lR06RvjUp+tcvcp7EFNyWoLTZ+Y0av1uHqneBhyaZYeW22WU13XdJKlkXcEx7Nyg/DycQatJDIPQmgsc0hiPXQ==; hy_source=web"
    }
    response = requests.post(url, json={
        "agentId": "naQivTmsDa",
    }, headers=headers)
    data = response.json()
    return data['id']



def queryRrport(cursor):
    cursor.execute('SELECT * FROM m_qingxu_report where  isrun = 0 limit 50')
    values = cursor.fetchall()
    return values

def queryContent(cursor, table_name, table_id):
    query = f'SELECT content FROM {table_name} WHERE id = %s LIMIT 1'
    cursor.execute(query, (table_id,))
    # values = cursor.fetchall()
    # query = f'SELECT content FROM {table_name} WHERE id = ? LIMIT 1'
    # cursor.execute(query, (table_id,))
    values = cursor.fetchall()
    return values[0] if values else None  # Access the actual content

def savePoint(cursor, id, point):
    query = 'UPDATE m_qingxu_report SET point = %s, isrun = 1 WHERE id = %s'
    cursor.execute(query, (point, id))

def run(cursor, conn):
    id = reqCreateChat()
    msg = """
    """

    chat.reqGpt(id, msg)
    while (True):
        reports = queryRrport(cursor)
        if len(reports) == 0:
            break

        for item in reports:
            table_name = item['table_name']
            table_id = item['table_id']
            qc = queryContent(cursor, table_name, table_id)
            codes2 = chat.gpt(id, qc['content'])
            print(qc['content'])
            # if "data" in codes2 and "content" in codes2["data"]:
            #     point = content2 = codes2["data"]["content"]
            point = 0
            content2 = codes2
            if "过热" in content2 or "强烈积极" in content2 :
                point = "2"
            elif "积极" in content2:
                point = "1"
            elif "中性" in content2:
                point = "0"
            elif "消极" in content2:
                point = "-1"
            elif "过冷" in content2 or "强烈消极" in content2:
                point = "-2"
            elif content2 not in [0, 1, -1, 2, -2, "0", "1", "-1", "2", "-2"]:
                return
            savePoint(cursor, item['id'], point)
            conn.commit()
    pass


def compute():
    mc = getConfig('mysql')
    conn = MySQLdb.connect(
        host=mc['host'],
        user=mc['user'],
        passwd=mc['passwd'],
        db=mc['db'],
        charset='utf8mb4',
        cursorclass=DictCursor  # 使用字典游标
    )
    cursor = conn.cursor()

    # conn = sqlite3.connect(parent_dir + '/sqlitefile/v1/qingxu.db')
    # conn.row_factory = sqlite3.Row
    # 创建一个Cursor:
    # cursor = conn.cursor()
    # cursor.execute('PRAGMA journal_mode=WAL;')
    run(cursor, conn)


    cursor.close()
    conn.close()

if __name__ == "__main__":
    compute()
    # gpt("习近平同俄罗斯总统普京会谈①双方就中俄关系和国际问题深入交换意见，一致同意深化战略协作，推动中俄关系稳定、健康、高水平发展。②习近平强调中俄双方要坚持合作大方向，排除外部干扰，让合作“稳”的基础更坚实、“进”的动能更充足。普京表示坚定奉行一个中国原则，在台湾问题上始终支持中方立场。")
