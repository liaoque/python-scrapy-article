from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from shares.model.shares_kdj_compute_detail import SharesKdjComputeDetail as SharesKdjComputeDetailModels
# Create your models here.
import numpy as np

from plotly.offline import plot
from plotly.graph_objs import Scatter

class SharesKdjComputeDetail(SharesKdjComputeDetailModels):

    class Meta:
        proxy = True
