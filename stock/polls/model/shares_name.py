from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from .shares import Shares as SharesModels
from shares.model.shares_name import SharesName as SharesNameModels
# Create your models here.
import numpy as np
import talib

from plotly.offline import plot
from plotly.graph_objs import Scatter

class SharesName(SharesNameModels):

    class Meta:
        proxy = True

    @admin.display
    def shares(self):
        itemList = self.shares_set.all()
        #
        kd = self.talib_KDJ(itemList)
        return kd
        itemListLen = 20
        x_data = np.array([v for v in range(0, itemListLen)])
        kk = kd['k'][~np.isnan(kd['k'])][-20:]
        kj = kd['j'][~np.isnan(kd['j'])][-20:]
        kd = kd['d'][~np.isnan(kd['d'])][-20:]



        data1 = Scatter(x=x_data, y=kk, mode='lines', name='k', opacity=0.8, marker_color='red')
        data2 = Scatter(x=x_data, y=kd, mode='lines', name='d', opacity=0.8, marker_color='blue')
        data3 = Scatter(x=x_data, y=kj, mode='lines', name='j', opacity=0.8, marker_color='orange')
        plot_div = plot([data1, data2, data3], output_type='div')
        # context = {'plot_div': plot_div}
        return plot_div

    def __str__(self):
        return self.name


    def talib_KDJ(self, data, fastk_period=9, slowk_period=3, slowd_period=3):
        indicators = {}
        # 计算kd指标
        high_prices = np.array([v.p_max / 100 for v in data])
        low_prices = np.array([v.p_min / 100 for v in data])
        close_prices = np.array([v.p_end / 100 for v in data])
        slowk_period = 2 * slowk_period - 1
        slowd_period = 2 * slowd_period - 1
        indicators['k'], indicators['d'] = talib.STOCH(high_prices, low_prices, close_prices,
                                                       fastk_period=fastk_period,
                                                       slowk_period=slowk_period,
                                                       slowk_matype=1,
                                                       slowd_period=slowd_period,
                                                       slowd_matype=1)
        # indicators['j'] = 3 * indicators['k'] - 2 * indicators['d']
        # indicators['j'] = 3 * indicators['d'] - 2 * indicators['k']
        indicators['j'] = list(map(lambda x, y: 3 * x - 2 * y, indicators['k'], indicators['d']))

        return indicators
