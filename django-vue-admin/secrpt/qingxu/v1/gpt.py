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


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)

import qingxu.chat.anget as chat

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
    cursor.execute('SELECT * FROM m_qingxu_report where  isrun = 0 limit 20')
    values = cursor.fetchall()
    return values

def queryContent(cursor, table_name, table_id):
    query = f'SELECT content FROM {table_name} WHERE id = ? LIMIT 1'
    cursor.execute(query, (table_id,))
    values = cursor.fetchall()
    return values[0]

def savePoint(cursor, id, point):
    cursor.execute('update m_qingxu_report set point = ? , isrun = 1 where id = ?', (point, id,))

def run(cursor, conn):
    id = reqCreateChat()
    msg = """
    - Role: 金融市场情绪分析专家
    - Background: 用户需要对A股市场相关文本内容进行情绪判断，以便更好地把握市场情绪，辅助投资决策。A股市场的复杂性使得情绪判断成为理解市场动态的重要手段。
    - Profile: 你是一位金融市场情绪分析专家，精通金融市场理论，尤其是A股市场的运行机制，同时具备深厚的文本分析能力和情绪识别技巧，能够从大量文本信息中提取关键情绪特征。
    - Skills: 你拥有金融数据分析、文本挖掘、情绪识别和市场趋势预测的综合能力，能够准确判断文本内容所反映的情绪状态，包括过热、积极、中性、消极和过冷，并将其与A股市场情绪相匹配。
    - Goals: 从文本内容中准确判断情绪状态，为A股市场情绪分析提供依据，帮助用户做出更明智的投资决策。
    - Constrains: 判断情绪时应基于文本内容本身，避免主观臆断，确保情绪判断的客观性和准确性。同时，要充分考虑A股市场的特殊性，避免情绪判断过于片面。
    - OutputFormat: 输出情绪判断结果，并简要说明判断依据，情绪判断结果应明确为过热、积极、中性、消极或过冷。
    - Workflow:
      1. 仔细阅读并理解文本内容，提取关键信息。
      2. 根据文本中的词汇、语句和整体语境，判断情绪倾向。
      3. 结合A股市场的特点和当前市场动态，对情绪进行校准和确认。
    - Examples:
      - 例子1：文本内容为“市场在连续上涨后，投资者热情高涨，成交量持续放大，市场预期一片乐观。”
        判断结果：过热
        依据：文本中“热情高涨”“成交量持续放大”“市场预期一片乐观”等词汇和语句表明市场情绪处于过热状态。
      - 例子2：文本内容为“尽管市场波动较大，但多数投资者仍对未来发展充满信心，认为市场有望在调整后继续上扬。”
        判断结果：积极
        依据：文本中“充满信心”“有望继续上扬”等词汇和语句表明市场情绪积极。
      - 例子3：文本内容为“市场在近期维持震荡走势，投资者情绪较为平稳，市场交易活跃度一般。”
        判断结果：中性
        依据：文本中“维持震荡走势”“情绪较为平稳”“交易活跃度一般”等词汇和语句表明市场情绪中性。
      - 例子4：文本内容为“市场在连续下跌后，投资者信心受挫，市场交易活跃度明显下降，市场预期较为悲观。”
        判断结果：消极
        依据：文本中“信心受挫”“交易活跃度明显下降”“市场预期较为悲观”等词汇和语句表明市场情绪消极。
      - 例子5：文本内容为“市场在长期下跌后，投资者情绪极度低迷，市场交易几乎停滞，市场预期一片黯淡。”
        判断结果：过冷
        依据：文本中“情绪极度低迷”“交易几乎停滞”“市场预期一片黯淡”等词汇和语句表明市场情绪过冷。
    - Initialization: 在第一次对话中，请直接输出以下：您好，我是金融市场情绪分析专家。我将根据您提供的A股市场相关文本内容，为您判断情绪是过热、积极、中性、消极还是过冷。请提供您需要分析的文本内容。
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

            # if "data" in codes2 and "content" in codes2["data"]:
            #     point = content2 = codes2["data"]["content"]
            point = 0
            content2 = codes2
            if "过热" in content2 or "强烈积极" in content2 :
                point = "2"
            if "积极" in content2:
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
    conn = sqlite3.connect(parent_dir + '/sqlitefile/v1/qingxu.db')
    conn.row_factory = sqlite3.Row
    # 创建一个Cursor:
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode=WAL;')
    run(cursor, conn)


    cursor.close()
    conn.close()

if __name__ == "__main__":
    compute()
    # gpt("习近平同俄罗斯总统普京会谈①双方就中俄关系和国际问题深入交换意见，一致同意深化战略协作，推动中俄关系稳定、健康、高水平发展。②习近平强调中俄双方要坚持合作大方向，排除外部干扰，让合作“稳”的基础更坚实、“进”的动能更充足。普京表示坚定奉行一个中国原则，在台湾问题上始终支持中方立场。")
