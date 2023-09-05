# 返回 -1差，  1 好， 0平
def qingxu(today, yeastday):
    if "yuan_yin" not in yeastday or "jing_jia_sort" not in yeastday["yuan_yin"]:
        return -1

    jin_jia_yeastday = yeastday["yuan_yin"]["jing_jia_sort"]
    jin_jia = today["yuan_yin"]["jing_jia_sort"]
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
