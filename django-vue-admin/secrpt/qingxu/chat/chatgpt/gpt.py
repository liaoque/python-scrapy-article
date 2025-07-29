import requests
import json
import time


def reqGpt(id, msg):
    url = "https://cc01.plusai.io/backend-api/conversation"
    headers = {
        "x-timestamp": "1753000624",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM5NDI1MTYsInN1YiI6IjMyZTdmOTVhZGMyYzQxNmM4ZTNiYzlmYTM2NWQ2MjdkIiwiaWF0IjoxNzUzODA3NTE2LCJ0b2tlbl90eXBlIjoiYWNjZXNzX3Rva2VuIiwic3Vic2NyaXB0aW9uX2lkIjoiNjVhOTA4NDI1NjQ2YTNjNGRlNjg5ODcyIiwiYWNjb3VudF9pZCI6IjY4MzdjN2MyZmRmNDVjNzA3ZTdjZTY3NyJ9.-PrPYeqw_L4cJ1-bTHyyvAIKf9xc60fuDWGMhDDaWAg",
        "cookie": "timestamp=1722905044021; oai-locale=en-US; oai-nav-state=1; oai-did=11f14f78-5f1b-4a21-accf-458b98c52533; oai-thread-sidebar=%22%257B%2522isOpen%2522%253Afalse%257D%22; __Secure-auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM4ODAxNzAsInN1YiI6IjMyZTdmOTVhZGMyYzQxNmM4ZTNiYzlmYTM2NWQ2MjdkIiwiaWF0IjoxNzUyNjcwNTcwLCJ0b2tlbl90eXBlIjoiYXV0aF90b2tlbiJ9.eEFGIp_WHnF9Ns7c741wn3K3zuPNleytp9_kvG4wCsY; __Secure-access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM5NDI1MTYsInN1YiI6IjMyZTdmOTVhZGMyYzQxNmM4ZTNiYzlmYTM2NWQ2MjdkIiwiaWF0IjoxNzUzODA3NTE2LCJ0b2tlbl90eXBlIjoiYWNjZXNzX3Rva2VuIiwic3Vic2NyaXB0aW9uX2lkIjoiNjVhOTA4NDI1NjQ2YTNjNGRlNjg5ODcyIiwiYWNjb3VudF9pZCI6IjY4MzdjN2MyZmRmNDVjNzA3ZTdjZTY3NyJ9.-PrPYeqw_L4cJ1-bTHyyvAIKf9xc60fuDWGMhDDaWAg; _account=f9f24477-3b6b-4a27-a298-c8663fd4edc5"

    }
    response = requests.post(url, json={
        "action": "variant",
        "messages": [
            {
                "id": "aaa22765-9e30-4f3b-baba-585d7bfaeba1",
                "author": {"role": "user", "name": None, "metadata": {}},
                "create_time": 1752997866.204491,
                "update_time": None,
                "content": {
                    "content_type": "text", "parts": [
                        msg
                    ]
                },
                "status": "finished_successfully",
                "end_turn": None,
                "weight": 1,
                "metadata": {
                    "serialization_metadata": {"custom_symbol_offsets": []},
                    "request_id": "96212012ba9ab3a6-SJC",
                    "message_source": None,
                    "timestamp_": "absolute"
                }, "recipient": "all", "channel": None
            }],
            "conversation_id": "687c9fcd-3c00-8005-94ed-4c67dea4a4db",
            "parent_message_id": "4e4dd461-704d-4605-bf88-fbb6d8aba55b",
            "model": "gpt-4-1-mini", "timezone_offset_min": -480,
            "timezone": "Asia/Shanghai", "variant_purpose": "none",
            "history_and_training_disabled": False,
            "conversation_mode": {"kind": "primary_assistant", "plugin_ids": None},
            "force_paragen": False, "force_paragen_model_slug": "",
            "force_rate_limit": False, "reset_rate_limits": False,
            "websocket_request_id": "ff10239b-8f62-49b7-811b-d2e7c3799f17",
            "supported_encodings": [], "conversation_origin": None,
            "client_contextual_info": {
                "is_dark_mode": False,
                "time_since_loaded": 88,
               "page_height": 656, "page_width": 655,
               "pixel_ratio": 2, "screen_height": 900,
               "screen_width": 1440
            },
            "paragen_stream_type_override": None,
            "paragen_cot_summary_display_override": "allow"
    }, headers=headers)
    return response.content.decode("utf-8")


import json


def extract_msg(data_str):
    """
    从 OpenAI 流式响应（data: 前缀）中提取并拼接所有用户可见的文本内容。

    支持两种格式：
      1. JSON 对象流（{"choices":[{"delta":{"content":...}}]})
      2. JSON 字符串数组（["您","提供",...]）

    参数:
        data_str (str): 包含多行以 "data:" 开头的聊天响应原始字符串。

    返回:
        str: 拼接后的完整消息内容。
    """
    msg = ""
    for line in data_str.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line[len("data:"):].strip()
        if not payload:
            continue
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            # 忽略非 JSON 或不完整行
            continue

        # 1. 处理带 choices 的对象格式
        if isinstance(parsed, dict) and "choices" in parsed:
            for choice in parsed["choices"]:
                delta = choice.get("delta", {})
                if isinstance(delta, dict) and "content" in delta:
                    content = delta["content"]
                    if isinstance(content, str):
                        msg += content

        # 2. 处理字符串数组格式
        elif isinstance(parsed, list):
            # 扁平化字符串列表，拼接所有字符串元素
            def flatten_and_collect(item):
                if isinstance(item, str):
                    return item
                elif isinstance(item, list):
                    return "".join(flatten_and_collect(sub) for sub in item)
                return ""

            for elem in parsed:
                msg += flatten_and_collect(elem)

    return msg


def gpt(id, msg):
    time.sleep(3)
    codes2 = reqGpt(id, msg)
    if "当前会话已过期" in codes2:
        return "当前会话已过期"
    codes2 = extract_msg(codes2)
    # 回答异常就直接返回数据错误，丁丁提示
    return codes2


if __name__ == "__main__":
    print(gpt(0,
              "周末没啥重大消息，下周一美股还休市一天，A股下周自己走了。目前看，下周5月收官周，技术面不太乐观，各大指数陆续都有向下破位的走势，技术面，显示，下周调整的概率大。 "))
