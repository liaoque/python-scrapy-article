from django.db import models


# Create your models here.

from .model.shares_name import SharesName
from .model.shares import Shares
from .model.shares_kdj import SharesKdj
from .model.shares_ban import SharesBan
from .model.shares_kdj_compute import SharesKdjCompute
from .model.shares_kdj_compute_detail import SharesKdjComputeDetail
from .model.shares_join_industry import SharesJoinIndustry
from .model.shares_industry import SharesIndustry
from .model.shares_industry_kdj import SharesIndustryKdj
from .model.shares_macd import SharesMacd
from .model.futrues_hot import FutruesHot
from .model.futrues_join_shares import FutruesJoinShares
from .model.shares_half_year import SharesHalfYear
from .model.shares_season import SharesSeason
from .model.shares_month import SharesMonth
from .model.shares_industry_month import SharesIndustryMonth
from .model.shares_industry_season import SharesIndustrySeason
from .model.shares_date import SharesDate

