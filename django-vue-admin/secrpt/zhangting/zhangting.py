from pymongo import MongoClient
from datetime import datetime
from dateutil import parser as date_parser
from itertools import combinations
import os
import sys

from datetime import date, timedelta


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 设置根目录是secrpt
print(parent_dir)
sys.path.insert(0, parent_dir)

from common.wencai import wencai
from common.database import getConfig



# —— 2. 获取并保存当日数据 —— #
def fetch_and_save(date_str: str):
    """
    1) 按日期（YYYYMMDD）调用接口
    2) 将接口返回的 'datas' 中的每条记录 upsert 到 MongoDB
    """
    s = "%s涨停股票，首次涨停时间，最终涨停时间，连续涨停天数，涨停原因，涨停封单量，涨停封单额，涨停封成比，涨停封流比，涨停开板次数，几天几板，涨停类型，所属概念，所属行业" %(date_str)
    dall = wencai(s,1)
    if len(dall) <= 0 :
        return
    print("==========================================================")
    print(s)
    print("==========================================================")

    # 连接 DB
    config = getConfig("default")
    client = MongoClient(config['uri'])
    coll = client[config['db_name']]["limitup_records"]

    coll.delete_many({'date': date_str})

    #
    saved = 0
    date_str = [ key.replace("首次涨停时间[", "").replace("]", "")  for key, item in dall[0].items() if "首次涨停时间" in key][0]
    suffix = f'[{date_str}]'

    for entry in dall:
        print(entry)
        code = entry['股票代码']
        name = entry['股票简称']

        # 动态拼接带日期后缀的字段名
        first_key = f"首次涨停时间{suffix}"
        last_key = f"最终涨停时间{suffix}"
        vol_key = f"涨停封单量{suffix}"
        ratio_key = f"涨停封单量占成交量比{suffix}"

        dde = 0
        if "最新dde大单净额" in entry:
            dde = entry['最新dde大单净额']

        # 显式把所有我们关注的列都取出来
        record = {
            'date': date_str,
            'code': code,
            'name': name,

            # 基本涨停信息
            # 'price': float(entry['最新价']),
            # 'change_ratio': float(entry['最新涨跌幅']),
            'concepts': entry['所属概念'],
            # 'attributes_count': int(entry['所属概念数量']),

            # 封单 & 市值等
            # 'a_share_market_value': float(entry[f"a股市值(不含限售股){suffix}"]),
            # 'dde_big_order': dde,
            # 'total_share_capital': float(entry[f"总股本{suffix}"]),
            # 'pe_ratio': float(entry[f"市盈率(pe){suffix}"]),

            # 时间信息
            'first_limit_time': date_parser.parse(f"{date_str} {entry[first_key].strip()}"),
            'last_limit_time': date_parser.parse(f"{date_str} {entry[last_key].strip()}"),

            # 连续涨停天数 & 类型
            'consecutive_days': (entry[f"连续涨停天数{suffix}"]),
            'limit_type': entry[f"涨停类型{suffix}"],

            # 封单量/额
            'seal_order_volume': int(float(entry[vol_key])),
            'seal_order_amount': float(entry[f"涨停封单额{suffix}"]),
            'seal_order_ratio': float(entry[ratio_key]),
            'seal_to_flow_ratio': float(entry[f"涨停封单量占流通a股比{suffix}"]),

            # 涨停打开次数 & 概念、行业
            'open_count': (entry[f"涨停开板次数{suffix}"]),
            'plate': entry[f"几天几板{suffix}"],
            'industry': entry['所属同花顺行业'],

            # 明细数据（原 JSON 字符串）
            # 'detail_data': entry[f"涨停明细数据{suffix}"],
        }

        # upsert
        coll.update_one(
            {'date': date_str, 'code': code},
            {'$set': record},
            upsert=True
        )
        saved += 1

    print(f"[{date_str}] 已保存 {saved} 条涨停记录。")


def fetch_and_save2(date_str: str):
    s = "%s跌停股票，首次跌停时间，最终跌停时间，连续跌停天数，跌停原因，跌停封单量，跌停封单额，跌停封成比，跌停封流比，跌停开板次数，跌停类型，所属概念，所属行业" % (
        date_str)
    dall = wencai(s, 1)
    if len(dall) <= 0 :
        return
    print("==========================================================")
    print(s)
    print("==========================================================")
    config = getConfig("default")
    client = MongoClient(config['uri'])
    coll = client[config['db_name']]["limitdown_records"]

    coll.delete_many({'date': date_str})

    saved = 0
    date_str = [key.replace("首次跌停时间[", "").replace("]", "") for key, item in dall[0].items() if "首次跌停时间" in key][0]
    suffix = f'[{date_str}]'

    for entry in dall:
        print(entry)
        code = entry['股票代码']
        name = entry['股票简称']

        # 动态拼接带日期后缀的字段名
        first_key = f"首次跌停时间{suffix}"
        last_key = f"最终跌停时间{suffix}"
        vol_key = f"跌停封单量{suffix}"
        ratio_key = f"跌停封单量占成交量比{suffix}"

        dde = 0
        if "最新dde大单净额" in entry:
            dde = entry['最新dde大单净额']

        # 显式把所有我们关注的列都取出来
        record = {
            'date': date_str,
            'code': code,
            'name': name,

            # 基本跌停信息
            # 'price': float(entry['最新价']),
            # 'change_ratio': float(entry['最新涨跌幅']),
            'concepts': entry['所属概念'],
            # 'attributes_count': int(entry['所属概念数量']),

            # 封单 & 市值等
            # 'a_share_market_value': float(entry[f"a股市值(不含限售股){suffix}"]),
            # 'dde_big_order': dde,
            # 'total_share_capital': float(entry[f"总股本{suffix}"]),
            # 'pe_ratio': float(entry[f"市盈率(pe){suffix}"]),

            # 时间信息
            'first_limit_time': date_parser.parse(f"{date_str} {entry[first_key].strip()}"),
            'last_limit_time': date_parser.parse(f"{date_str} {entry[last_key].strip()}"),

            # 连续跌停天数 & 类型
            'consecutive_days': (entry[f"连续跌停天数{suffix}"]),
            'limit_type': entry[f"跌停类型{suffix}"],

            # 封单量/额
            'seal_order_volume': int(float(entry[vol_key])),
            'seal_order_amount': float(entry[f"跌停封单额{suffix}"]),
            'seal_order_ratio': float(entry[ratio_key]),
            'seal_to_flow_ratio': float(entry[f"跌停封单量占流通a股比{suffix}"]),

            # 跌停打开次数 & 概念、行业
            'open_count': int(entry[f"跌停开板次数{suffix}"]),
            'industry': entry['所属同花顺行业'],

            # 明细数据（原 JSON 字符串）
            # 'detail_data': entry[f"跌停明细数据{suffix}"],
        }

        # upsert
        coll.update_one(
            {'date': date_str, 'code': code},
            {'$set': record},
            upsert=True
        )
        saved += 1

    print(f"[{date_str}] 已保存 {saved} 条跌停记录。")


# —— 4. 一键执行示例 —— #
if __name__ == '__main__':
    # 1) 拉取并存储 2025-06-13 的数据

    today = date.today()
    fetch_and_save(today.strftime("%Y%m%d"))
    i = 1
    while(i < 3):
        yesterday = today - timedelta(days=i)
        fetch_and_save(yesterday.strftime("%Y%m%d"))
        i += 1

    fetch_and_save2(today.strftime("%Y%m%d"))
    i = 1
    while(i < 3):
        yesterday = today - timedelta(days=i)
        fetch_and_save2(yesterday.strftime("%Y%m%d"))
        i += 1


    #
    # # 2) 查找共振（至少两天共振）
    # resonances = find_resonance(min_occurrences=2)
    # if resonances:
    #     print("检测到以下“共振”组合（天数 ≥2）：")
    #     for pair, days in resonances.items():
    #         print(f"  {pair}: 共振 {days} 天")
    # else:
    #     print("当前数据库中暂无满足 ≥2 天共振的股票对。")
