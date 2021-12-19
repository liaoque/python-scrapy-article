from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from shares.model.shares_name import SharesName as SharesNameModels
from shares.model.shares import Shares as SharesModels2
# Create your models here.
import numpy as np
import talib

from plotly.offline import plot
from plotly.graph_objs import Scatter

class SharesName(SharesNameModels):

    @admin.display
    def shares(self):
        itemList = SharesModels2.objects.filter(code_id=self.code).all()
        # itemList = self.code.shares_set.all()
        kd = self.talib_KDJ(itemList)
        itemListLen = len(itemList)
        x_data = np.array([v for v in range(0, itemListLen)])
        kk = kd['k']
        kd = kd['d']
        kj = kd['j']

        data1 = Scatter(x=x_data, y=kk, mode='lines', name='test', opacity=0.8, marker_color='red')
        data2 = Scatter(x=x_data, y=kd, mode='lines', name='test', opacity=0.8, marker_color='red')
        data3 = Scatter(x=x_data, y=kj, mode='lines', name='test', opacity=0.8, marker_color='red')
        plot_div = plot([data1, data2, data3], output_type='div')
        # context = {'plot_div': plot_div}
        # print(self.shares_set)


        return plot_div
        # return self.shares_set.all()

    def __str__(self):
        return self.name


    def talib_KDJ(self, data, fastk_period=9, slowk_period=3, slowd_period=3):
        indicators = {}
        # 计算kd指标
        high_prices = np.array([v.p_max / 100 for v in data])
        low_prices = np.array([v.p_min / 100 for v in data])
        close_prices = np.array([v.p_end / 100 for v in data])
        indicators['k'], indicators['d'] = talib.STOCH(high_prices, low_prices, close_prices,
                                                       fastk_period=fastk_period,
                                                       slowk_period=slowk_period,
                                                       slowd_period=slowd_period)
        indicators['j'] = 3 * indicators['k'] - 2 * indicators['d']
        return indicators
