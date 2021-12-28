from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from shares.model.shares_kdj_compute import SharesKdjCompute as SharesKdjComputeModels
# Create your models here.
import numpy as np
# import talib

from plotly.offline import plot
from plotly.graph_objs import Scatter

class SharesKdjCompute(SharesKdjComputeModels):

    class Meta:
        proxy = True




