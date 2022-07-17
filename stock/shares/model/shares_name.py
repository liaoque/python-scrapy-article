from django.db import models


# Create your models here.


class SharesName(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)
    temper_tonghuashun = models.IntegerField(default=0, help_text="同花顺股民看涨看跌比例")
    temper_dongfangcaifu = models.IntegerField(default=0, help_text="东方财富股民看涨看跌比例")
    area_id = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    pb = models.IntegerField(default=0, help_text="市净率")
    # 市盈率 看notice5
    pe = models.IntegerField(default=0, help_text="市盈率(静态)")
    pe_d = models.IntegerField(default=0, help_text="市盈率(动)")
    pe_ttm = models.IntegerField(default=0, help_text="市盈率(ttm)")
    gpm = models.IntegerField(default=0, help_text="毛利率 Gross Profit Margin")
    npmos = models.IntegerField(default=0, help_text="净利率 Net Profit Margin on Sales")
    roe = models.IntegerField(default=0, help_text="加权净资产收益率")
    gpm_ex = models.IntegerField(default=0, help_text="营业同比增长率")
    npmos_ex = models.IntegerField(default=0, help_text="净利润同比增长率")

    code_type = models.IntegerField(default=0, help_text="1股票，2行业板块")
    member_up = models.IntegerField(default=2, help_text="股东人数，1 下降，2 上升")
    macd_up = models.IntegerField(default=1, help_text="macd，1 下降，2 上升")
    finance_up = models.IntegerField(default=1, help_text="财务，1 下降，2 上升")

    five_day = models.IntegerField(default=0, help_text="5天最低")
    twenty_day = models.IntegerField(default=0, help_text="20天最低")
    sixty_day = models.IntegerField(default=0, help_text="60天最低")
    one_hundred_day = models.IntegerField(default=0, help_text="120天最低")
    four_year_day = models.IntegerField(default=0, help_text="4年最低")

    # 基本面向好的公司
    @staticmethod
    def getCodeList():
        # 找公司 行业成长性，或者收入成长 比较靠谱的公司
        sql = """
            SELECT n.code ,n.gpm,t.gpm as tgpm FROM (SELECT * FROM `mc_shares_name` where code_type =  1 and (gpm_ex > 4000 or npmos_ex > 4000))  n
    left join mc_shares_join_industry as i on n.code = i.code_id
    left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2 and gpm_ex > 1500) t on t.code = i.industry_code_id
    where ( n.gpm_ex > t.gpm_ex or  n.npmos_ex > t.npmos_ex)  and n.name not like %s  and n.npmos > 0 and n.member_up =1 
            and t.gpm != 0 and n.name not like %s 
            """
        codeList = SharesName.objects.raw(sql, params=('%ST%', '%退%',))
        # codeList = [item for item in codeList]
        #  公司毛利率不能低于行业毛利率的 30%
        return list(filter(lambda n: (n.gpm >= n.tgpm or (n.gpm / n.tgpm > 0.3)), codeList))

    @staticmethod
    def getCodeListByFhCode(implement_date_as):
        sql = """
                SELECT 1 as id, t.code , t.code as code_id FROM `mc_shares_name` t  
                LEFT JOIN mc_shares_join_industry i on i.code_id = t.code
                LEFT JOIN mc_shares_name n on n.code = i.industry_code_id
                where t.npmos_ex > 5000 
                and n.gpm_ex > 1000
                and code_id in (%s)
                """ % ('"%s"' % ("\",\"".join([item.code_id for item in implement_date_as])))
        result = SharesName.objects.raw(sql)
        return result

    class Meta:
        db_table = "mc_shares_name"
        # abstract = True

    def __str__(self):
        return self.name

    class SkillType():
        kdj = 1

        class AccountType():
            intersection_pre = 1
            intersection_today = 2
            turn_tomorrow = 3

