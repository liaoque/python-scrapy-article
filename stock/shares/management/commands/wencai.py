import requests
import numpy as np
from datetime import datetime, timedelta

from wencai2 import trend, trendCode, acodes, common, pic_n

if __name__ == '__main__':
    day = datetime.today().strftime('%Y-%m-%d')
    yeasterday = ""
    date_obj = datetime.strptime(day, '%Y-%m-%d')
    today = date_obj - timedelta(days=1)
    today = today.strftime('%Y-%m-%d')
    yeasterday = date_obj - timedelta(days=4)
    yeasteryeasterday = date_obj - timedelta(days=5)
    yeasterday = yeasterday.strftime('%Y-%m-%d')
    yeasteryeasterday = yeasteryeasterday.strftime('%Y-%m-%d')
    # today = "2023-07-01"
    # yeasterday = "2023-06-30"
    # 查最强票
    codes = trend.trendNight(today)
    # 把这些最强票，统计5个最强概念，及其龙头
    concepts_sorted = trend.top(codes)
    # print(concepts_sorted)

    for item in concepts_sorted:
        # 打印概念和龙头
        print(item["concept"], "-----龙头:", item["codes2"][0]["name"], item["codes2"][0]["code"], item["codes2"][0]["concept"])
        # 查该概念的符合的股票集合
        codes2 = acodes.buzhang(today, yeasterday, yeasteryeasterday , item["concept"])

        intersection2 = []
        for codes3 in codes2:
            if codes3["code"] in item["codes"]:
                continue
            if codes3["code"] > "680000":
                continue
            # 匹配概念，跟龙头， 记录跟龙头的匹配度
            intersection = list(set(codes3["concept"]) & set(item["codes2"][0]["concept"]))
            intersection2.append({
                "code": codes3["code"],
                "name": codes3["name"],
                "c": len(intersection),
                "intersection": intersection,
            })
        # 匹配度排序
        intersection2 = sorted(intersection2, key=lambda x: x['c'], reverse=True)
        print(intersection2)
        print("+++++++++++++++++++")
        # 查N的
        # for item2 in intersection2:
        #     # 非3字开头的
        #     if item2["code"][0] != "3" and pic_n.check(today, item2["code"]):
        #         print("匹配--------------",item2["code"])

    # pic_n.check(today, "002931.SZ")
    # print(concepts_sorted)

    # removals = ['标普道琼斯A股', '转融券标的', '沪股通', '融资融券', '雄安新区', '京津冀一体化', '转融券标的', '参股银行', '共同富裕示范区']
    #
    # for item in removals:
    #     concept_set.discard(item)  # 使用discard方法移除元素，如果元素不存在，不会抛出错误
    #
    # codes = trendCode(today, yeasterday)
    # arr_2d = np.array(codes)
    #
    # filtered_codes = []
    #
    # for item in codes:
    #     # 将industry和concept字段转为集合，以便进行集合操作
    #     industry_set = set(item["concept"])
    #     # 检查industry集合是否包含concept集合的任何一个元素
    #     if any(concept in concept_set for concept in industry_set):
    #         # 如果不包含，就加入到filtered_codes列表中
    #         filtered_codes.append(item)
    #
    # # 将过滤后的codes转为numpy数组
    # arr_2d_filtered = np.array(filtered_codes)
    #
    # print('","'.join([code["code"].replace(".SZ", "").replace(".SH", "") for code in arr_2d_filtered]))
