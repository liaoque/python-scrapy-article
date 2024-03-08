from dvadmin.wb.core import zhu_xian

def biao_shai_xuan(d, data1):
    gn = [gn for (gn, item) in d["chuang_ye_ban_gn"].items() if
          item["shu_liang"]["color"] == 13421823 or item["chuang_bai_ri_xin_gao"]["color"] == 13421823]

    for gn2 in d["bu_zhang_data"]["gn"]:
        if gn2 in d["chuang_ye_ban_gn"] and d["chuang_ye_ban_gn"][gn2]["jin_jing_feng"]["color"] == 35:
            continue
        gn.append(gn2)


    # print(gn)
    # gn.extend(filter(  d["bu_zhang_data"]["gn"],  lambda gn:gn in d["chuang_ye_ban_gn"]. ))

    # 主线取前三
    i = 0
    gn3 = []
    while i < 3:
        if d["zhu_xian"][i]['gn'] not in gn :
            i += 1
            continue
        gn3.append(d["zhu_xian"][i]['gn'])
        i += 1

    # gn = [gn for (gn, item) in d["chuang_ye_ban_gn"].items() if
    #              item["jin_jing_feng_count"]["color"] == 13421823 or item["chuang_bai_ri_xin_gao"]["color"] == 13421823]
    # gn.extend(d["bu_zhang_data"]["gn"])

    #  如果主线源选不到，直接走原来逻辑
    if len(gn3) == 0:
        zhuxian2 = zhu_xian.zhuxian2(data1)
        gn3.append(zhuxian2[0]['gn'])

    # T1 数据
    chuang_data = filter(lambda x: len(set(x[1]["suoshugainian"]) & set(gn3)) > 0 and x[0][0:2] == '30', data1.items())
    chuang_data = sorted(chuang_data, key=lambda x: x[1]["zhangdie4thday"], reverse=True)
    # chuang_data = list(chuang_data)
    # chuang_data = {key: value for key, value in chuang_data}
    for key,item in chuang_data:
        item["suoshugainian"] = list(set(item["suoshugainian"]) & set(gn3))
        item["color8"] = 0
        item["color12"] = 0
        item["color13"] = 0
        if item["n"] > 0:
            item["color12"] = 37
            # 前日最大涨幅 >0 昨日连板天数 = 38
            if item["N_maxzhangfu"] > 0:
                item["color8"] = 38
            # 昨日最大涨幅 >0 昨日连板天数 = 38
            if item["N_zuidazhangfu"] > 0:
                item["color8"] = 38
            # '前日涨停 = "涨停" 且 昨日连板天数 = 0 昨日连板天数 = 38
            if item["N_beforeyesterdaytop"] > 0 and item["lianbantianshuyesterday"] == 0:
                item["color8"] = 38

    # T2 数据
    zhu_data = filter(
        lambda x: len(set(x[1]["suoshugainian"]) & set(gn3)) > 0 and x[0][0:2] != '30' and x[0][0:2] != '68',
        data1.items())
    zhu_data = sorted(zhu_data, key=lambda x: x[1]["zhangdie4thday"], reverse=True)
    # zhu_data = {key: value for key, value in zhu_data}
    for key,item  in zhu_data:
        item["suoshugainian"] = list(set(item["suoshugainian"]) & set(gn3))
        item["color8"] = 0
        item["color12"] = 0
        item["color13"] = 0
        if item["n"] > 0:
            item["color12"] = 37
            # 连板次数 >0 昨日连板天数 = 38
            if item["N_lianbancishu"] > 0:
                item["color8"] = 38
            # 昨日曾涨停 >0 昨日连板天数 = 38
            if item["N_zuocengzhangting"] > 0:
                item["color8"] = 38
            # '前日涨停 = "涨停"  昨日连板天数 = 38
            if item["N_beforeyesterdaytop"] > 0 and item["lianbantianshuyesterday"] == 0:
                item["color8"] = 38

    return {
        "chuang_data": chuang_data,
        "zhu_data": zhu_data,
        "biao_shai_xuan": gn3,
        "gn": gn,
    }
