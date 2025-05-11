import requests
import json
import time

prefixMsg = """
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


def reqGpt(id, msg):
    url = "https://chat.qwen.ai/api/v1/chats/new"
    headers = {
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImU1MDI4MTA3LWY4ZjgtNGNiNC1iZWRiLTEyNzIzMThmM2E0NCIsImV4cCI6MTc0OTUyNTQwMH0.D6r8THlne4mHvjALJ5vtaT19WpgI3aff6vxP8d_ooNU",
        "cookie": "ssxmod_itna=QqUxBiD=i=itGQIPYQiQ=G=D2Dm67CaqDzxC5iO8Du2xjKidNDUQX0=FEGcjQm0XDqhrqDDqtDlaO2YDSxD6HDK4GTwzp00234dUARPpNYnA4Ueo3+jrrcKzlDE03YsjDES3Aau/BDIDnneDQKDoxGkDiyoD09YoQ4DxrPD5xDTDWeDGDD3YUYwD0+ITzgIDzb+T0AIDYco5R2oDY56DAwIs9Yv64i3gtdDEE4vDiPGV4DWQ4i1fAoputxD0ZW0qfRADWchfQZoqKQDIPloCAoDFrL3xq0k59dbW9zMDCKwvmMhq3TvSR7XK2qbi1Gnr+0YUwYfGx8i8KDKGnDUirbqKmDojYx00DzGi8Dt4EOtbRY4Tz0wzW552lj5/n5VKhx0xx0w=awsYG5ZRPouYKbtb0tS24lYx974kiKbGtdSY3+DD; "
    }
    response = requests.post(url, json={
        "stream": True,
        "incremental_output": True,
        "chat_type": "t2t",
        "model": "qwen3-30b-a3b",
        "messages": [
            {
                "role": "user",
                "content": prefixMsg,
                "chat_type": "t2t",
                "extra": {},
                "feature_config": {"thinking_enabled": False, "output_schema": "phase"}
            },
            {
                "role": "assistant",
                "content": "",
                "chat_type": "t2t",
                "feature_config": {"thinking_enabled": False, "output_schema": "phase"},
                "content_list": [
                    {"phase": "answer",
                     "content": "您好，我是金融市场情绪分析专家。我将根据您提供的A股市场相关文本内容，为您判断情绪是过热、积极、中性、消极还是过冷。请提供您需要分析的文本内容。",
                     "chat_type": "t2t"}
                ]
            },
            {
                "role": "user",
                "content": msg,
                "chat_type": "t2t",
                "extra": {},
                "feature_config": {"thinking_enabled": False, "output_schema": "phase"}
            }
        ],
        "session_id": "2c54ed4a-e890-42d4-b976-f49b8bfebd88",
        "chat_id": "9a230f0e-5e2d-4e98-9204-bbdfe667047b",
        "id": "3dbce5ce-cf1c-40e3-bf79-1011ad6bf357",
        "sub_chat_type": "t2t",
        "chat_mode": "normal"
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
                    if (
                            isinstance(data, dict)
                            and 'choices' in data
                            and len(data['choices']) == 1
                            and 'delta' in data['choices'][0]
                            and 'content' in data['choices'][0]['delta']
                    ):
                        mdg += data['choices'][0]['delta']['content']
                except json.JSONDecodeError:
                    continue
    return mdg


def gpt(id, msg):
    time.sleep(3)
    codes2 = reqGpt(id, msg)
    codes2 = extract_msg(codes2)
    # 回答异常就直接返回数据错误，丁丁提示
    return codes2
