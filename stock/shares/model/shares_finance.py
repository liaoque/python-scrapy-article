from django.db import models
from .shares_name import SharesName
from datetime import datetime


# Create your models here.

# https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYZBAjaxNew?type=0&code=SH600519
# SECURITY_CODE code
# REPORT_DATE date_as
# REPORT_DATE_NAME title

# XSJLL npmos
# XSMLL gpm
# ZZCZZTS 总资产周转天数
# CHZZTS 存货周转天数
# YSZKZZTS 应收账款周转天数
# TOAZZL 总资产周转率
# CHZZL 存货周转率
# YSZKZZL 应收账款周转率

# NONBUSINESS_INCOME 营业外收入
# NONBUSINESS_EXPENSE 营业外支出
# INVEST_INCOME 投资收益
# NOTE_ACCOUNTS_PAYABLE 应付票据及应付账款
# NOTE_ACCOUNTS_RECE 应收票据及应收账款
# PREPAYMENT 预付款项

class SharesFinance(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text='名字')
    date_as = models.DateField(help_text='财报日期')
    gpm = models.FloatField(default=0, help_text="毛利率 Gross Profit Margin")
    npmos = models.FloatField(default=0, help_text="净利率 Net Profit Margin on Sales")
    turnover_days = models.FloatField(default=0, help_text="总资产周转天数")
    goods_turnover_days = models.FloatField(default=0, help_text="存货周转天数")
    account_turnover_days = models.FloatField(default=0, help_text="应收账款周转天数")
    turnover_rate = models.FloatField(default=0, help_text="总资产周转率")
    goods_turnover_rate = models.FloatField(default=0, help_text="存货周转率")
    account_turnover_rate = models.FloatField(default=0, help_text="应收账款周转率")
    non_operating_incom = models.FloatField(default=0, help_text="营业外收入")
    non_operating_expenses = models.FloatField(default=0, help_text="营业外支出")
    income_from_investment = models.FloatField(default=0, help_text="投资收益")
    notes_payable = models.FloatField(default=0, help_text="应付票据及应付账款")
    notes_receivable = models.FloatField(default=0, help_text="应收票据及应收账款")
    parentnetprofit = models.FloatField(default=0, help_text="归属净利润(元)")
    kcfjcxsyjlr = models.FloatField(default=0, help_text="扣非净利润(元)")
    prepayment = models.FloatField(default=0, help_text="预付款项")
    companyType = models.FloatField(default=0, help_text="东方财富必须字段")

    class Meta:
        db_table = "mc_shares_finance"

    def __str__(self):
        return self.code_id + ":" + self.title + ":" + datetime.strftime(self.date_as, '%Y-%m-%d') + \
               " 净利润:" + str(self.gpm) + " 毛利润:" + str(self.npmos) + " 总资产周转率:" + str(self.turnover_rate) + \
               " 存货周转率:" + str(self.goods_turnover_rate) + " 应收账款周转率:" + str(self.account_turnover_rate) + \
               " 营业外收入:" + str(self.non_operating_expenses) + " 营业外支出:" + str(self.income_from_investment) + \
               " 应付票据及应付账款:" + str(self.notes_payable) + " 应收票据及应收账款:" + str(self.notes_receivable) + \
               " 预付款项:" + str(self.prepayment)
