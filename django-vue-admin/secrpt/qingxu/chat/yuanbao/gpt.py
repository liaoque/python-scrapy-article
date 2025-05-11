import requests
import json
import time

def reqGpt(id, msg):
    url = "https://yuanbao.tencent.com/api/chat/" + id
    headers = {
        "Host": "yuanbao.tencent.com",
        "cookie": "hy_user=CIhCqbC6T5voiJRk; hy_token=h1nxijKasHsn4fUxgFQiqu6LYWrMB5fquv5djhn4rffbWXNgUWx4U8Hl0gDeByUX; hy_source=web"
    }
    response = requests.post(url, json={
        "model": "gpt_175B_0404",
        "prompt": msg,
        "plugin": "Adaptive",
        "displayPrompt": msg,
        "displayPromptType": 1,
        "options": {"imageIntention": {"needIntentionModel": True, "backendUpdateFlag": 2, "intentionStatus": True}},
        "multimedia": [], "agentId": "naQivTmsDa", "supportHint": 1, "version": "v2", "chatModelId": "deep_seek_v3"
    }, headers=headers)
    return response.content.decode("utf-8")

def extract_msg(data_str):
    lines = data_str.strip().split('\n')
    mdg = ""
    for line in lines:
        if line.startswith("data:"):
            # 去掉前缀 "data:" 并去除多余的空格
            json_str = line[len("data:"):].strip()
            if json_str.startswith("{") and json_str.endswith("}"):
                try:
                    data = json.loads(json_str)
                    if isinstance(data, dict) and 'msg' in data:
                        mdg += data['msg']
                except json.JSONDecodeError:
                    continue
    return mdg


def gpt(id, msg):
    time.sleep(3)
    codes2 = reqGpt(id, msg)
    codes2 = extract_msg(codes2)
    # 回答异常就直接返回数据错误，丁丁提示
    return codes2