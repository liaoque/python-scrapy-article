import requests
import numpy as np
from datetime import datetime, timedelta

from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from collections import OrderedDict


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        file_path = "data.json"

        data = pic_n.getData(datetime.today().strftime('%Y-%m-%d'), "000001.SZ", -1)
        days = data
        json_data = common.read_json_file(file_path)
        for i in range(len(days)):
            today = datetime.utcfromtimestamp(days[i] / 1000)
            today = today.strftime('%Y-%m-%d')
            # today = "2023-08-01"

            codes2 = trend.trendFirst(today)

            codes3 = trend.trendNight(today)
            codes2 = codes3 + codes2
            codes2 = list({d['code']: d for d in codes2}.values())

            concepts_sorted = trend.top(codes2)

            json_data[today] = [{"concept": item["concept"], "codes": item["codes"]} for item in concepts_sorted]
            # print(sorted(json_data.items()))
            json_data = OrderedDict(sorted(json_data.items()))
            json_data = dict(json_data)

        common.write_json_file(file_path, json_data)
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
