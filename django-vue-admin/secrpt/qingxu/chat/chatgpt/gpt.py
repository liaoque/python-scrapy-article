import requests
import json
import time


def reqGpt(id, msg):
    url = "https://cc01.plusai.io/backend-api/conversation"
    headers = {
        "x-timestamp": "1753000624",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTY0Mzg5NTAsInN1YiI6IjMyZTdmOTVhZGMyYzQxNmM4ZTNiYzlmYTM2NWQ2MjdkIiwiaWF0IjoxNzU2MzAzOTUwLCJ0b2tlbl90eXBlIjoiYWNjZXNzX3Rva2VuIiwic3Vic2NyaXB0aW9uX2lkIjoiNjVhOTA4NDI1NjQ2YTNjNGRlNjg5ODcyIiwiYWNjb3VudF9pZCI6IjY4YTk0YTAxNjk2NjNlMjg0YzZjZmNlMCJ9.N5gptslYGkESI24Kdk6ngRFmH_ULluihPUC5xqUP_aY",
        "cookie": "oai-locale=en-US; oai-nav-state=1; oai-did=11f14f78-5f1b-4a21-accf-458b98c52533; oai-thread-sidebar=%22%257B%2522isOpen%2522%253Afalse%257D%22; __Secure-auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTY0MzcxNTksInN1YiI6IjMyZTdmOTVhZGMyYzQxNmM4ZTNiYzlmYTM2NWQ2MjdkIiwiaWF0IjoxNzU1MjI3NTU5LCJ0b2tlbl90eXBlIjoiYXV0aF90b2tlbiJ9.FrwsWTppEXc5GwO4a9OTefa5Jih0y3ZQELEIQv_xF6U; __Secure-access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTY0Mzg5NTAsInN1YiI6IjMyZTdmOTVhZGMyYzQxNmM4ZTNiYzlmYTM2NWQ2MjdkIiwiaWF0IjoxNzU2MzAzOTUwLCJ0b2tlbl90eXBlIjoiYWNjZXNzX3Rva2VuIiwic3Vic2NyaXB0aW9uX2lkIjoiNjVhOTA4NDI1NjQ2YTNjNGRlNjg5ODcyIiwiYWNjb3VudF9pZCI6IjY4YTk0YTAxNjk2NjNlMjg0YzZjZmNlMCJ9.N5gptslYGkESI24Kdk6ngRFmH_ULluihPUC5xqUP_aY; _account=f9f24477-3b6b-4a27-a298-c8663fd4edc5"
    }
    response = requests.post(url, json={
        "action": "variant",
        "messages": [
            {
                "id": "aaa23fde-c5a5-49c5-93a8-12d4f738bd4d",
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
            "conversation_id": "68b0a204-3c10-832a-9494-f628eddc7b84",
            "parent_message_id": "d83c2063-abd5-4581-911b-8ccd14ad68e2",
            "model": "gpt-4-1-mini", "timezone_offset_min": -480,
            "timezone": "Asia/Shanghai", "variant_purpose": "none",
            "history_and_training_disabled": False,
            "conversation_mode": {"kind": "primary_assistant", "plugin_ids": None},
            "force_paragen": False, "force_paragen_model_slug": "",
            "force_rate_limit": False, "reset_rate_limits": False,
            "websocket_request_id": "ff53aa25-8a05-4899-a54d-0bbd783dab45",
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
