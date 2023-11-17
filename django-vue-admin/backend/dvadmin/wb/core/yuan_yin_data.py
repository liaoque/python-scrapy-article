from dvadmin.wb.core import init_data, streak_rise, bu_zhang, suo_shu_gai_nian, pi_pei_gai_nian, gn, jie_guo, \
    biao_shai_xuan, zhu_xian


def getYuanYin(data):
    # 标记涨停和跌停， 炸板， 创百日新高， 一字板， 首板， N10, N20
    lianzhang_code_page = {
        # 取连涨股票
        "lianzhanggupiao": streak_rise.lian_zhang_gu_piao(data),
        # 取跌停股票
        "dietinggupiao": streak_rise.die_ting_gu_piao(data),
        # 取炸板股票
        "zhabangupiao": streak_rise.zha_ban_gu_piao(data),
        # 取创百日新高股票
        "chuangbairixingao": streak_rise.bai_ri_xin_gao_gu_piao(data),
        # 取一字板股票
        "yizibangupiao": streak_rise.yi_zi_ban_gu_piao(data),
        # 取首板股票
        "shoubangupiao": streak_rise.shou_ban_gu_piao(data),
    }

    lianzhang_page = {
        # 生成连涨概念 计算概念出现得次数
        "lianzhanggainian": streak_rise.lian_zhang_gai_nian(lianzhang_code_page["lianzhanggupiao"]),

        # 生成跌停概念
        "dietinggainian": streak_rise.die_ting_gai_nian(lianzhang_code_page["dietinggupiao"]),

        # 生成炸板概念
        "zhabangainian": streak_rise.zha_ban_gai_nian(lianzhang_code_page["zhabangupiao"]),

        # 生成创百日新高概念
        "chuangbairixingaogainnian": streak_rise.chuang_bai_ri_xin_gao_gai_nian(
            lianzhang_code_page["chuangbairixingao"]),

        # 生成一字板概念
        "yizibangainian": streak_rise.yi_zi_ban_gai_nian(lianzhang_code_page["yizibangupiao"]),

        # 生成首板概念
        "shoubangainian": streak_rise.shou_ban_gai_nian(lianzhang_code_page["shoubangupiao"]),
    }

    # 取涨停原因， 匹配涨停概念， 并标记最多的原因得次数
    lianzhang_code_page["lianzhanggupiao"] = streak_rise.zhang_ting_shi_pei_gu_piao(
        lianzhang_code_page["lianzhanggupiao"],
        lianzhang_page["lianzhanggainian"])

    # 取跌停原因
    lianzhang_code_page["dietinggupiao"] = streak_rise.die_ting_shi_pei_gu_piao(
        lianzhang_code_page["dietinggupiao"],
        lianzhang_page["dietinggainian"])

    # 取炸板原因
    lianzhang_code_page["zhabangupiao"] = streak_rise.zha_ban_shi_pei_gu_piao(lianzhang_code_page["zhabangupiao"],
                                                                              lianzhang_page["zhabangainian"])

    # 取创百日新高原因
    lianzhang_code_page["chuangbairixingao"] = streak_rise.chuang_bai_ri_xin_gao_shi_pei_gai_nian(
        lianzhang_code_page["chuangbairixingao"],
        lianzhang_page["chuangbairixingaogainnian"])

    # 取一字板原因
    lianzhang_code_page["yizibangupiao"] = streak_rise.yi_zi_ban_shi_pei_gu_piao(
        lianzhang_code_page["yizibangupiao"],
        lianzhang_page["yizibangainian"])

    # 取首板原因
    lianzhang_code_page["shoubangupiao"] = streak_rise.shou_ban_shi_pei_gu_piao(
        lianzhang_code_page["shoubangupiao"],
        lianzhang_page["shoubangainian"])

    yuan_yin = {
        # 排列涨停原因，对概念计算竞价未匹配
        "lian_zhang_sort": streak_rise.zhang_ting_yuan_yin(lianzhang_code_page["lianzhanggupiao"],
                                                           lianzhang_page["lianzhanggainian"]),

        # 排列跌停原因
        "die_ting_sort": streak_rise.die_ting_yuan_yin(lianzhang_code_page["dietinggupiao"],
                                                       lianzhang_page["dietinggainian"]),

        # 排列炸板原因
        "zha_ban_sort": streak_rise.zha_ban_yuan_yin(lianzhang_code_page["zhabangupiao"],
                                                     lianzhang_page["zhabangainian"]),

        # 排列创百日新高原因
        "chuang_bai_ri_xin_gao_sort": streak_rise.chuang_bai_ri_xin_gao_yuan_yin(
            lianzhang_code_page["chuangbairixingao"],
            lianzhang_page["chuangbairixingaogainnian"]),

        # 排列一字板原因
        "yi_zi_ban_sort": streak_rise.yi_zi_ban_yuan_yin(lianzhang_code_page["yizibangupiao"],
                                                         lianzhang_page["yizibangainian"]),

        # 排列首板原因
        "shou_ban_sort": streak_rise.shou_ban_yuan_yin(lianzhang_code_page["shoubangupiao"],
                                                       lianzhang_page["shoubangainian"]),

        # 排列竞涨停竞跌停， 可以当作情绪看待
        "jing_jia_sort": streak_rise.jing_jia_info(lianzhang_code_page["yizibangupiao"],
                                                   lianzhang_code_page["dietinggupiao"]),

        # 排列5日涨跌幅，取每个概念涨跌幅最高得
        "day_5_sort": streak_rise.max_zhang_fu5_gu_piao(data),
        "zhu_xian": zhu_xian.zhuxian(data)
    }

    return yuan_yin
