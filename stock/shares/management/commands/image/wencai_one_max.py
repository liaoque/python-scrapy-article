# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, timedelta
import configparser

plt.rcParams['font.family'] = 'Arial Unicode MS'


def read_ini_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        config = configparser.ConfigParser()
        config.read_file(file)
    return config


def read_json_file(file_path):
    if not os.path.exists(file_path):  # 检测文件是否存在
        with open(file_path, 'w', encoding='utf-8') as new_file:
            json.dump({}, new_file)  # 创建一个新的空JSON文件，初始内容为一个空字典

    with open(file_path, 'r+', encoding='utf-8') as file:
        data = json.load(file)
    return data


# # 示例文件路径
file_path = 'config.ini'
#
# # 读取 INI 文件
ini_config = read_ini_file(file_path)
section_name = 'k-line'  # INI 文件中的节名
#
start = ini_config.get(section_name, "start")
end = ini_config.get(section_name, "end")

hot = ini_config.get(section_name, "hot").split(',')

if hot[0] == "":
    hot = []

if len(end) == 0:
    end = datetime.today().strftime('%Y-%m-%d')

if len(start) == 0:
    start = (datetime.today() - timedelta(days=5)).strftime('%Y-%m-%d')

json_data = read_json_file("data.json")

concepts_sorted2 = {}
x = []
tomorrow_concept = []
for key, value in json_data.items():
    if key >= start and key <= end:
        concepts_sorted2[key] = value
        for iem in value:
            if (len(hot) == 0 or  iem["concept"] in hot):
                tomorrow_concept.append(iem["concept"])
        x.append(key)

tomorrow_concept = list(set(tomorrow_concept))

for concept in tomorrow_concept:
    d = []
    i = 0
    for key, value in concepts_sorted2.items():
        d.append(0)
        for key2 in value:
            if key2["concept"] == concept:
                d[i] = len(key2["codes"])
        i = i + 1
    plt.plot(x, d, label=concept)

# 显示图例
plt.legend()

# 显示图表
plt.show()
