# 返回 -1差，  1 好， 0平
def qingxu(today, yeastday):
    if len(yeastday) == 0:
        return -1

    jin_jia_yeastday = yeastday["yuanyin"]["jing_jia_sort"]
    jin_jia = today["yuanyin"]["jing_jia_sort"]
    qing_xu = 0
    if jin_jia_yeastday['die_ting'] > 0:
        if jin_jia['die_ting'] > jin_jia_yeastday['die_ting']:
            qing_xu = 1
        elif jin_jia['die_ting'] < jin_jia_yeastday['die_ting']:
            qing_xu = -1
        return qing_xu

    if jin_jia_yeastday['zhang_ting'] > 0:
        if jin_jia['zhang_ting'] > jin_jia_yeastday['zhang_ting']:
            qing_xu = 1
        elif jin_jia['zhang_ting'] < jin_jia_yeastday['zhang_ting']:
            qing_xu = -1
    return qing_xu
