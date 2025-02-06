
import re

def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    # 进一步清洗可以根据需要添加
    return text