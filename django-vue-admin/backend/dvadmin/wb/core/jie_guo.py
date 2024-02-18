# 返回 -1差，  1 好， 0平
def qingxu(today, yeastday):
    if "jing_jia_sort" not in yeastday:
        return -1

    jin_jia_yeastday = yeastday["jing_jia_sort"]
    jin_jia = today["jing_jia_sort"]
    qing_xu = 0
    # if jin_jia['die_ting'] > jin_jia_yeastday['die_ting']:
    #     qing_xu = 1
    # elif jin_jia['die_ting'] < jin_jia_yeastday['die_ting']:
    #     qing_xu = -1
    # else:
    #     if jin_jia['zhang_ting'] > jin_jia_yeastday['zhang_ting']:
    #         qing_xu = 1
    #     elif jin_jia['zhang_ting'] < jin_jia_yeastday['zhang_ting']:
    #         qing_xu = -1

    die_ting = jin_jia['die_ting'] - jin_jia_yeastday['die_ting']
    zhang_ting = jin_jia['zhang_ting'] - jin_jia_yeastday['zhang_ting']

    zhang_ting = zhang_ting + die_ting
    if zhang_ting > 0:
        qing_xu = 1
    elif zhang_ting < 0:
        qing_xu = -1
    else:
        qing_xu = 1

    if "shang_zhang_sort" in yeastday:
        if yeastday["shang_zhang_sort"]["shang_zhang_count"] > 4000:
            qing_xu = -1

    return qing_xu
