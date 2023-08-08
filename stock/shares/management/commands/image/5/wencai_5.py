# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, timedelta
import pic_n
import trend
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

hot = ini_config.get(section_name, "hot")
first = ini_config.get(section_name, "first")

dates = pic_n.getData()
if len(end) == 0 and len(start) == 0:
    start = dates[len(dates) -5]

blockStr = None
if len(hot) > 0:
    blockStr = hot


x = []
block1Line = []
concepts = []
for item in dates:
    if start > item:
        continue
    elif start == item:
        if first == 1:
            codes2 = trend.trendFirst(item, block=blockStr)
        else:
            codes2 = trend.trendNight(item, block=blockStr)
    elif item in dates :
        if first == 1:
            codes2 = trend.trendFirst(item, block=blockStr)
        else:
            codes2 = trend.trendNight(item, block=blockStr)
    elif item > end :
        break
    concepts_sorted = trend.top(codes2)
    if len(concepts_sorted) == 0:
        x.append("%s \n %s"%(item, ""))
        block1Line.append([
            {"concept": "", "full":0 },
            {"concept": "", "full":0 }
        ])
        continue

    block1 = sorted(concepts_sorted, key=lambda x: x['count'], reverse=True)
    block2 = sorted(concepts_sorted, key=lambda x: x['full'], reverse=True)
    if block1[0]["concept"] == block2[0]["concept"]:
        if len(block2) == 1:
            block2[0] = {"concept": "", "full":0 }
        else:
            block2[0] = block2[1]
    if blockStr == "" or blockStr is None :
        blockStr = "%s, %s"%(block1[0]["concept"], block2[0]["concept"])
        concepts.append(block1[0]["concept"])
        if block2[0]["concept"] != "":
            concepts.append(block2[0]["concept"])
    block1Line.append([
        block1[0],
        block2[0],
    ])
    
    x.append("%s \n %s"%(item, block1[0]["codes2"][0]["name"]))


concepts = list(set(concepts))
for concept in concepts:
    xBlock = []
    for block1Item in block1Line:
        full = 0
        for item2 in block1Item:
            if item2["concept"] == concept:
                full = item2["full"]
                break
        xBlock.append(full)
    plt.plot(x, xBlock, label=concept)



# 显示图例
plt.legend()

# 显示图表
plt.show()











