import requests
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand, CommandError
from collections import OrderedDict
from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def da(self):
        file_path = "data.json"
        json_data = common.read_json_file(file_path)
        data = pic_n.getData(datetime.today().strftime('%Y-%m-%d'), "000001.SZ", -100)
        days = [item[0] for item in data]
        for i in range(len(days)):
            today = datetime.utcfromtimestamp(days[i] / 1000)
            today = today.strftime('%Y-%m-%d')
            codes = trend.trendNight(today)
            if len(codes) == 0:
                continue
            concepts_sorted = trend.top(codes)
            json_data[today] = [{"concept": item["concept"], "codes": item["codes"]} for item in concepts_sorted]

        json_data = OrderedDict(sorted(json_data.items()))
        json_data = dict(json_data)
        common.write_json_file(file_path, json_data)

    def handle(self, *args, **options):
        # self.da()
        # return
        file_path = "data.json"
        today = datetime.today().strftime('%Y-%m-%d')
        codes2 = trend.trendFirst(today)

        data = pic_n.getData(datetime.today().strftime('%Y-%m-%d'), "000001.SZ", -10)
        days = [item[0] for item in data]

        dates = []
        ta_values = []
        taa_values = []
        taf_values = []
        json_data = common.read_json_file(file_path)
        for i in range(len(days) - 6):
            print(i + 3, days[i + 3])
            today = datetime.utcfromtimestamp(days[i + 3] / 1000)
            year = today.strftime('%Y')
            today = today.strftime('%Y-%m-%d')
            yeasterday = datetime.utcfromtimestamp(days[i + 2] / 1000)
            yeasterday = yeasterday.strftime('%Y-%m-%d')
            yeasteryeasterday = datetime.utcfromtimestamp(days[i + 1] / 1000)
            yeasteryeasterday = yeasteryeasterday.strftime('%Y-%m-%d')
            tomorrow = datetime.utcfromtimestamp(days[i + 4] / 1000)
            tomorrow = tomorrow.strftime('%Y-%m-%d')
            tomorrow2 = datetime.utcfromtimestamp(days[i + 5] / 1000)
            tomorrow2 = tomorrow2.strftime('%Y-%m-%d')

            # 当天晚上风口
            codes = trend.trendNight(today)
            if len(codes) == 0:
                continue
            concepts_sorted = trend.top(codes)

            json_data[today] = [{"concept": item["concept"], "codes": item["codes"]} for item in concepts_sorted]

            # 第二天的风口
            codes2 = trend.trendFirst(tomorrow)
            if len(codes2) == 0:
                continue
            concepts_sorted2 = trend.top(codes)
            tomorrow_concept = [item["concept"] for item in concepts_sorted2]

            # ta 涨 +1 跌 -1
            # taf 涨 + 涨幅 跌 - 跌幅
            # taa 涨 + 涨金额 跌 - 跌金额
            taa = taf = ta = 0
            intersection2 = []
            for item in concepts_sorted:
                if item["concept"] in tomorrow_concept:
                    codes2 = acodes.buzhang(today, yeasterday, yeasteryeasterday, item["concept"])
                    intersection2 = []
                    for codes3 in codes2:
                        # 过滤当天龙头
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
                    # print(len(intersection2))
                    intersection2 = sorted(intersection2, key=lambda x: x['c'], reverse=True)

                    for codes3 in intersection2[:1]:
                        data = pic_n.getData(tomorrow2, codes3["code"], -10)
                        print(codes3["code"])
                        # print(data[9])
                        print(data[8])
                        if len(data) < 10:
                            continue
                        if data[9][5] - data[8][5] > 0:
                            ta = ta + 1
                            taa = taa + data[9][5] - data[8][5]
                            taf = taf + data[8][7]
                        else:
                            ta = ta - 1
                            taa = taa + data[9][5] - data[8][2]
                            taf = taf + data[8][7]

                            # print(data[9][5] - data[8][2], data[9][5] , data[8][2], codes3["code"])
                    # if ta < 0:

            if taf < -10:
                print(tomorrow, taf, intersection2)
            dates.append(tomorrow)
            ta_values.append(ta)
            taa_values.append(taa)
            taf_values.append(taf)

        common.write_json_file(file_path, json_data)

        # print(dates)
        plt.figure(figsize=(10, 6))
        plt.plot(dates, ta_values, label='TA')
        plt.plot(dates, taa_values, label='TAA')
        plt.plot(dates, taf_values, label='TAF')

        plt.xlabel('Date')
        plt.ylabel('Values')
        plt.title('Line Plot Example')
        plt.legend()
        plt.grid(True)
        plt.show()

        # print("ta today -------", today, ta, taa,taf )
        # print(intersection2)

        # print(concepts_sorted)
        # print(concepts_sorted2)

        # print(days[i])
        # break
        # today = today.strftime('%Y-%m-%d')
        # yeasterday = yeasterday.strftime('%Y-%m-%d')
        # yeasteryeasterday = yeasteryeasterday.strftime('%Y-%m-%d')
        # # today = "2023-07-01"
        # # yeasterday = "2023-06-30"
        # # 查最强票
        # codes = trend.trendNight(today)
        # # 把这些最强票，统计5个最强概念，及其龙头
        # concepts_sorted = trend.top(codes)
        # # print(concepts_sorted)
        #
        # for item in concepts_sorted:
        #     # 打印概念和龙头
        #     print(item["concept"], "-----龙头:", item["codes2"][0]["name"], item["codes2"][0]["code"], item["codes2"][0]["concept"])
        #     # 查该概念的符合的股票集合
        #     codes2 = acodes.buzhang(today, yeasterday, yeasteryeasterday , item["concept"])
        #
        #     intersection2 = []
        #     for codes3 in codes2:
        #         if codes3["code"] in item["codes"]:
        #             continue
        #         if codes3["code"] > "680000":
        #             continue
        #         # 匹配概念，跟龙头， 记录跟龙头的匹配度
        #         intersection = list(set(codes3["concept"]) & set(item["codes2"][0]["concept"]))
        #         intersection2.append({
        #             "code": codes3["code"],
        #             "name": codes3["name"],
        #             "c": len(intersection),
        #             "intersection": intersection,
        #         })
        #     # 匹配度排序
        #     intersection2 = sorted(intersection2, key=lambda x: x['c'], reverse=True)
        #     print(intersection2)
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
