import requests
import numpy as np
from datetime import datetime, timedelta

from wencai2 import trend, trendCode, acodes, common, pic_n
from django.core.mail import send_mail

if __name__ == '__main__':
    today = datetime.today().strftime('%Y-%m-%d')
    # today = "2023-07-17"
    codes2 = trend.trendFirst(today)
    concepts_sorted = trend.top(codes2)
    tomorrow_concept = [item["concept"] for item in concepts_sorted]
    # print(tomorrow_concept)

    str = "night：%s\n" % ("\",\"".join(tomorrow_concept))
    send_mail(
        'night %s' % today,
        str,
        'lovemeand1314@163.com',
        ['844596330@qq.com'],
        fail_silently=False,
    )