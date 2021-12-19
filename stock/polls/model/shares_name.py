from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from shares.model.shares_name import SharesName as SharesNameModels
# Create your models here.

from plotly.offline import plot
from plotly.graph_objs import Scatter

class SharesName(SharesNameModels):

    @admin.display(empty_value='???')
    def view_code(self, obj):
        return 222

    @admin.display
    def colored_name(self):
        x_data = [0, 1, 2, 3]
        y_data = [x ** 2 for x in x_data]
        data = Scatter(x=x_data, y=y_data, mode='lines', name='test', opacity=0.8, marker_color='red')
        plot_div = plot([data], output_type='div')
        # context = {'plot_div': plot_div}
        # print(self.shares_set)
        return plot_div
        # return self.shares_set.all()

    def __str__(self):
        return self.name

