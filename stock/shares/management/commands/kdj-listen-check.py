import numpy as np
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
from shares.model.shares import Shares
from shares.model.shares_date_listen import SharesDateListen
from shares.model.shares_macd import SharesMacd
from shares.model.shares_buys import SharesBuys
from shares.model.shares_date import SharesDate
import numpy as np
import talib
import math


# 校验的
# 1. 先记录 j < 0 作为参考点
# 2. 记录 diff 的上涨走势 且 J < 40  作为买点
# 3. 判断 j 下调走势作为卖点，或者3天强制卖出

class Command(BaseCommand):
    help = '记录每天-10以下的kdj股票'

    codeList = []
    dateList = []
    five_start = ''
    twenty_start = ''
    sixty_start = ''
    one_hundred_start = ''
    four_year_start = ''

    date_as = None

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        print("开始计算-----")

        self.dateList = self.getAllDates()

        # 获取基本的监控股票
        self.codeList = self.getCodeList()

        for item in self.dateList[-60:]:
            print(item.date_as.strftime("%Y-%m-%d"))
            if item.date_as.strftime("%Y-%m-%d") <= '2022-03-31':
                continue

            self.getkdj10(item.date_as)

            # dateList = self.getAllDateListens()
            # for item in dateList:
            #     item.date_as = date_as
            allCodeIds = SharesDateListen.objects.filter(buy_date_as=None)
            print("寻找买入点-----")
            for codeItem in allCodeIds:
                # codeItem.date_as = item.date_as
                codeItemResult, buy_pre = self.findBuyPoint(codeItem, item.date_as)
                if codeItemResult != None:
                    sharesItem = Shares.objects.filter(date_as=codeItemResult.date_as, code_id=codeItem.code_id)[0]
                    print("找到买入点--%s--%s---%s", codeItem.code_id, codeItemResult.date_as, sharesItem.p_end)
                    codeItem.buy_date_as = codeItemResult.date_as
                    codeItem.buy_pre = buy_pre
                    codeItem.buy_start = sharesItem.p_end
                    codeItem.save()
                pass

            allCodeIds = SharesDateListen.objects.filter(buy_start__gt=0)
            print("寻找卖出点-----")
            for codeItem in allCodeIds:
                codeItemResult = self.findSellPoint(codeItem, item)
                if codeItemResult == None:
                    continue
                sharesItem = Shares.objects.filter(date_as=codeItemResult.date_as, code_id=codeItem.code_id)[0]
                print("找到卖出点--%s--%s---%s", codeItem.code_id, codeItemResult.date_as, sharesItem.p_end)
                buys = SharesBuys(
                    code_id=codeItem.code_id,
                    buy_date_as=codeItem.buy_date_as,
                    buy_start=codeItem.buy_start,
                    buy_pre=codeItem.buy_pre,
                    sell_date_as=codeItemResult.date_as,
                    sell_end=sharesItem.p_end,
                )
                buys.save()
                codeItem.delete()
                if codeItem.buy_start >= sharesItem.p_end:
                    # 亏损的情况下继续监控
                    listen = SharesDateListen(
                        code_id=codeItem.code_id,
                        p_start=sharesItem.p_end,
                        date_as=codeItemResult.date_as,
                        type=1,
                    )
                    listen.save()
            # break

    def findSellPoint(self, codeItem, item):
        date_as = item.date_as
        if item.date_as <= codeItem.buy_date_as:
            return None

        # 对比今天和昨天
        result = SharesKdj.objects.filter(code_id=codeItem.code_id, date_as__lte=date_as).order_by('-date_as')
        if len(result) < 2:
            return None
        sharesCollect = Shares.objects.filter(code_id=codeItem.code_id, date_as__lte=date_as).order_by('-date_as')
        item = None
        key = 0
        result = result[:2]
        sharesCollect = sharesCollect[:2]
        for value in result:
            if key + 1 >= len(result):
                break
            # 倒锤头
            hammerMax = max(sharesCollect[key].p_end, sharesCollect[key].p_start)
            hammerMin = min(sharesCollect[key].p_end, sharesCollect[key].p_start)
            hammerBody = math.fabs(sharesCollect[key].p_end - sharesCollect[key].p_start)
            hammerHeader = math.fabs(sharesCollect[key].p_max - hammerMax)
            hammerFooter = math.fabs(sharesCollect[key].p_min - hammerMin)
            if hammerHeader < hammerBody and hammerBody * 2.5 < hammerFooter:
                print("倒锤头%s--%s--%d---%d---%d", sharesCollect[key].date_as, codeItem.code_id,
                      hammerHeader, hammerBody, hammerFooter)
                item = value
                break
            if hammerFooter < hammerBody and hammerBody * 2.5 < hammerHeader:
                print("锤头%s--%s--%d---%d---%d", sharesCollect[key].date_as, codeItem.code_id,
                      hammerHeader, hammerBody, hammerFooter)
                item = value
                break

            # kdj下跌
            if value.j < result[key + 1].j:
                item = result[key]
                break
            key += 1
        return item

    def findBuyPoint(self, codeItem, date_as):
        #     需要避险
        # ban = SharesBan.objects.filter(code_id=codeItem.code_id)
        # if len(ban):
        #     return None, 0

        result = Shares.objects.filter(code_id=codeItem.code_id, date_as__lt=date_as).order_by('-date_as')
        if len(result) < 30:
            return None, 0

        # 最后一天股价
        lastItem = result[0]
        codeNameItem = SharesName.objects.filter(code=codeItem.code_id)[0]
        # 有没有到支撑位
        if not self.checkPrice(lastItem, codeNameItem):
            return None, 0

        # 先计算一个最低的拐点的股价， 然后对比今天的股价
        todayPend, today = self.getTodayPend(codeItem.code_id, date_as)
        # if datetime.strptime(today, '%Y-%m-%d').date() > lastItem.date_as:
        #     return None, 0

        # 判断上升标准
        # 计算ema
        # 按 date_as 从小到大 排序
        shares = result[::-1]
        close = [item.p_end / 100 for item in shares]
        emaList = talib.EMA(np.array(close), timeperiod=5)
        # emaList[-1] + .01 表示上升的 ema 最小值

        # """
        # 假如N=1，则EMA(X，1)=［2*X1+(1-1)*Y’］/(1+1)=X1
        # 假如N=2，则EMA(X，2)=［2*X2+(2-1)*Y’］/(2+1)=(2/3)*X2+(1/3)X1
        # 假如N=3，则EMA(X，3)=［2*X3+(3-1)*Y’］/(3+1)=［2*X3+2*((2/3)*X2+(1/3)*X1)］/4=(1/2)*X3+(1/3)*X2+(1/6)*X1=3/6*X3+2/6*X2+1/6*X1
        # """

        # Y =［2*X3+(3-1)*Y’］/(3+1)
        # Y * (3+1) = 2*X3+(3-1)*Y’
        # Y * (3+1) - (3-1)*Y’ = 2*X3
        # (Y * (3+1) - (3-1)*Y’) /2 = X3
        n = len(close) % 5
        if n == 0:
            n = 5
        preEma = ((emaList[-1] + .01) * (n + 1) - (n - 1) * emaList[-1]) / 2
        print(shares[0], shares[-1], emaList[-1], todayPend, preEma)
        # 今天股价> 预测股价，则判断上升，且今天必须大于监控时间
        if todayPend >= preEma:
            item = Shares.objects.filter(code_id=codeItem.code_id, date_as=date_as)[0]
            pre_ema = preEma
            return item, pre_ema
        return None, 0

    def checkPrice(self, item, codeNameItem):
        dateList = SharesDate.objects.filter(date_as__lte=item.date_as).order_by('-date_as')
        five_start = dateList[:5][4].date_as
        twenty_start = dateList[:20][19].date_as
        sixty_start = dateList[:60][59].date_as
        one_hundred_start = dateList[:120][119].date_as
        four_year_start = dateList[:1200][1119].date_as
        print(five_start, item.date_as)
        codeNameItem.five_day = Shares.objects.filter(date_as__gte=five_start,
                                                      date_as__lte=item.date_as,
                                                      code_id=item.code).aggregate(Min('p_end'))["p_end__min"]
        codeNameItem.twenty_day = Shares.objects.filter(date_as__gte=twenty_start,
                                                        date_as__lte=item.date_as,
                                                        code_id=item.code).aggregate(Min('p_end'))["p_end__min"]
        codeNameItem.sixty_day = Shares.objects.filter(date_as__gte=sixty_start,
                                                       date_as__lte=item.date_as,
                                                       code_id=item.code).aggregate(Min('p_end'))["p_end__min"]
        codeNameItem.one_hundred_day = Shares.objects.filter(date_as__gte=one_hundred_start,
                                                             date_as__lte=item.date_as,
                                                             code_id=item.code).aggregate(Min('p_end'))["p_end__min"]
        codeNameItem.four_year_day = Shares.objects.filter(date_as__gte=four_year_start,
                                                           date_as__lte=item.date_as,
                                                           code_id=item.code).aggregate(Min('p_end'))["p_end__min"]
        # if codeNameItem.five_day == 0:
        #     return False
        return abs(item.p_end - codeNameItem.five_day) / codeNameItem.five_day < 0.01 or abs(
            item.p_end - codeNameItem.five_day) / codeNameItem.five_day < 0.01 or abs(
            item.p_end - codeNameItem.twenty_day) / codeNameItem.twenty_day < 0.01 or abs(
            item.p_end - codeNameItem.sixty_day) / codeNameItem.sixty_day < 0.01 or abs(
            item.p_end - codeNameItem.one_hundred_day) / codeNameItem.one_hundred_day < 0.01 or abs(
            item.p_end - codeNameItem.four_year_day) / codeNameItem.four_year_day < 0.01

    def getTodayPend(self, code_id, date_as):
        #  第二天的股价
        item = Shares.objects.filter(code_id=code_id, date_as__gt=date_as).order_by('date_as')
        if len(item) == 0:
            return False, False
        return item[0].p_end / 100, item[0].date_as
        # sharesNameItem = SharesName.objects.filter(status=1, code_type=1, code=code_id)[0]
        # if sharesNameItem.area_id == 1:
        #     s_code = "1." + str(code_id)
        # else:
        #     s_code = "0." + str(code_id)
        # url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=' + \
        #       s_code + '&cb=&klt=101&fqt=0&lmt=' + str(1) + \
        #       '&end=20500101&iscca=1&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58'
        # r = requests.get(url)
        # klines = r.json()["data"]["klines"][0]
        # # print(float(klines.split(',')[2]), klines.split(',')[0])
        # return float(klines.split(',')[2]), klines.split(',')[0]
        pass

    def getkdj10(self, date):
        date = SharesDate.objects.filter(date_as__lt=date).order_by('-date_as')[0].date_as
        sql = '''
            select 1 as id, a.code_id,c.p_end,a.date_as,a.j  from mc_shares_kdj  a
            left join ( select code_id,p_end from mc_shares where date_as = %s ) c  on a.code_id = c.code_id
            where a.date_as = %s  
               and a.code_id not in ( select code_id from mc_shares_date_listen )
               and a.j < 55
               and (a.code_id < 300000 or a.code_id > 600000)
               and a.code_id < 680000
               and a.code_id not in (SELECT code FROM `mc_shares_name` where name like %s )
            ;
            '''

        result = SharesKdj.objects.raw(sql, params=(date, date, '%ST%',))
        result = list(filter(lambda n: n.code_id in self.codeList, result))
        # print(result)
        print("%s-挑选出-10的股票：%s个" % (date, len(result)))
        print(",".join(["\"" + item.code_id + "\"" for item in result]))
        for item in result:
            if len(SharesDateListen.objects.filter(code_id=item.code_id)):
                continue
            listen = SharesDateListen(
                code_id=item.code_id,
                p_start=item.p_end,
                date_as=item.date_as,
                type=1,
            )
            listen.save()

    def getAllDateListens(self):
        sql = '''
            select 1 as id, date_as from mc_shares_date_listen group by date_as ;
            '''
        return SharesDateListen.objects.raw(sql)

    def getAllDates(self):
        sql = '''
            select 1 as id, date_as from mc_shares_date where date_as >= '2021-12-01' ;
            '''
        return SharesDateListen.objects.raw(sql)

    # 基本面向好的公司
    def getCodeList(self):

        # 找公司 行业成长性，或者收入成长 比较靠谱的公司
        sql = """
        SELECT n.code ,n.gpm,t.gpm as tgpm FROM (SELECT * FROM `mc_shares_name` where code_type =  1 and (gpm_ex > 1000 or npmos_ex > 1000))  n
left join mc_shares_join_industry as i on n.code = i.code_id
left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2 and gpm_ex > 1000) t on t.code = i.industry_code_id
where ( n.gpm_ex > t.gpm_ex or  n.npmos_ex > t.npmos_ex)  and n.name not like %s  and n.npmos > 0 and n.member_up =1 
        """
        codeList = SharesName.objects.raw(sql, params=('%ST%',))
        # codeList = [item for item in codeList]
        #  公司毛利率不能低于行业毛利率的 30%
        codeList = list(filter(lambda n: (n.gpm >= n.tgpm or (n.gpm / n.tgpm > 0.3)), codeList))
        # print(codeList)

        # if len(industry) <= 0:
        #     return []
        # industry = [item.code for item in industry]
        # codeList = SharesJoinIndustry.objects.filter(industry_code_id__in=industry)
        # codeList = SharesJoinBlock.objects.filter(block_code_id__in=[
        #     "BK0683",
        #     "BK0520",
        #     "BK0823",
        # ], code_id=[item.code_id for item in industryList])
        self.codeList = [item.code for item in codeList]
        return self.codeList
