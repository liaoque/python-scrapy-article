import requests
import json
import time


def reqGpt(id, msg):
    url = "https://yuanbao.tencent.com/api/chat/" + id
    headers = {
        "Host": "yuanbao.tencent.com",
        "cookie": "_qimei_uuid42=196190010341002b502ddff0c2b4fe4a8e5bcdf72c; _qimei_h38=bb868febad5b0914f5ff516703000002119512; _qimei_fingerprint=51bdb5cfd51ad5fc4c453115d6a569d1; hy_source=web; _qimei_i_1=23c172d0c75256d397c2ac610f8121e0feefa0a7170d5587b5892f582593206c616335943980e7ddd487efe1; hy_user=a25aef197e1047929c25955e62755bea; hy_token=8tE8bq6InCxff5mUqQZfc9aGHP6NPD80Cr/k258SiLJ9CYW8HiMzU5pREYyvnbvj1/hU+Oq0a/ipME9s/tsXN7TzG8Qw+nP9tSxY12ByjMoHeBd0Tvv4igvl27GV/SCyijDTsZ4dxwHdLRIyxN+TdzHtsDmmtK4NzJ/7iTB+HHuqxUyqY2tnIf4zh6oqlbG1VRoHY/rZCAzZaGYsqZB8OTe3kRymBnqnDSVaM3sJ0LqWKdjd6U1m6bL3EAy4Rvz9cDkTgu2caWu1vC5xZCjwXoOkOd8LicX11iDC8zXA7bdDTCpIcR0IpzW7WdBGgJTzLOjfTtDzB+R5hcPEDDudn4hHrTauZn4aNkKD6LukrCBYYHNY1PPX1MYy+J0Xyk90pkCGr7xfyucQwGxWOPwOB4hyNguLiCY85pK4u2DbifYXyUvHraVzRoZhCdeliOH4ts4mYPPgxDD29lqQ/E2VXDzfGRcmDPWtAhwmUhZQ7R96jCoqt1gU+TsJeRkQkIToHNqP2JSxypghMT6r9HGS2qqQKmvU3KmM4cCLp1zIX112l8AY2960803ACfwrvA0kGA5WFmWIqLE6x6kMIW7xPVhSfqdKj2dce9aL1d1wjiRzqHz7IMQTLPD2FPFt90AbDFX57nuGiovIn4T3zpfHOQGUd90p8CseYQFmb8QKjpU="
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