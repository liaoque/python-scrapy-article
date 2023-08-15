# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, timedelta
import pic_n
import trend
import configparser

plt.subplots(figsize=(20, 10))  # 设置图形大小
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


# https://4.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=1.000001&ut=&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf60&klt=101&fqt=1&end=20500101&lmt=500&_=1691856348281
# 数据

zd = [
    # ["-4%", "-3%"],
    # ["-3%", "-2%"],
    # ["-2%", "-1%"],
    # ["-1%", "0%"],
    # ["0%", "1%"],
    # ["1%", "2%"],
    # ["2%", "3%"],
    ["3%", "4%"],
]

for item in zd:
    start = item[0]
    end = item[1]
    x = []
    xlen = []
    for index in range(0, 30):
        startIndex = 30 - index
        today = dates[len(dates) - startIndex]
        x.append("%s" % (today.replace("2023-", "23").replace("2022-", "22")))
        le = trend.trendTop(today, start, end, "")
        xlen.append(le)
    label = "%s-%s"%(start, end)
    plt.plot(x, xlen, label=label)

# start = "-3%"
# end = "-2%"
# x = []
# xlen = []
# xlen2 = []
# for index in range(0, 100):
#     startIndex = 100 - index
#     today = dates[len(dates) - startIndex]
#     le = trend.trendTop(today, start, end, "")
#
#     # xlen.append(le)
#     le2 = trend.trendTop(today, "2%", "3%", "")
#     if le/le2 > 0.5:
#         continue
#     x.append("%s" % (today.replace("2023-", "23").replace("2022-", "22")))
#     xlen2.append(le/le2)
# # label = "%s-%s"%(start, end)
# # plt.plot(x, xlen, label=label)
# label = "%s-%s"%("2%", "3%")
# plt.plot(x, xlen2, label=label)


# 显示图例
plt.legend()

# 显示图表
plt.show()











