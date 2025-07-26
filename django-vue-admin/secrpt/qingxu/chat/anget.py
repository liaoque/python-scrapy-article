import requests
import json
import time
import qingxu.chat.yuanbao.gpt as yuanbao
import qingxu.chat.qianwen.gpt as qianwen
import qingxu.chat.chatgpt.gpt as chatgpt
from datetime import datetime

current_gpt = "qianwen"
hour = datetime.now().hour
if 0 <= hour <= 7:
    current_gpt = "chatgpt"

def reqGpt(id, msg):
    global current_gpt

    if id == "":
        # current_gpt = "qianwen"
        return msg

    if current_gpt == "yuanbao":
        msg = yuanbao.reqGpt(id, msg)
        if "今日提问次数已达上限，请明日再试" in msg:
            current_gpt = "qianwen"
    #         msg = qianwen.reqGpt(id, msg)
    # else:
    #     msg = qianwen.reqGpt(id, msg)

    return msg

# def extract_msg(data_str):
#     global current_gpt
#     if current_gpt == "yuanbao":
#         msg = yuanbao.extract_msg(data_str)
#     else:
#         msg = qianwen.extract_msg(data_str)
#     return msg


def gpt(id, msg):
    global current_gpt
    if current_gpt == "chatgpt":
        msg = chatgpt.gpt(id, msg)
        if "今日提问次数已达上限，请明日再试" in msg:
            current_gpt = "qianwen"
            return gpt(id, msg)
    elif current_gpt == "yuanbao":
        msg = yuanbao.gpt(id, msg)
        if "今日提问次数已达上限，请明日再试" in msg:
            current_gpt = "qianwen"
            return gpt(id, msg)
    else:
        msg = qianwen.gpt(id, msg)
    # 回答异常就直接返回数据错误，丁丁提示
    return msg