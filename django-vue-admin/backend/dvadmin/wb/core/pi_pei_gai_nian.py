from dvadmin.wb.config import code_config

"""
Sub 匹配概念()
    Debug.Print Now & "匹配概念"
    Dim gp, rng, rng3, rng4, rng5, rng6, rng7 As Range
    Dim temp, qx As String
    Dim js, i, h As Integer
    Dim yz, imax1, imax2, imin1, imin2, ijjlb1, ijjlb2, ijzlb1, ijzlb2 As Double
    qx = Sheet4.Range("H6")
    Range("T1_匹配[所属行业]") = ""
    Range("T2_匹配[所属行业]") = ""

    If Sheet19.Range("a2") <> "" Then
        h = Sheet19.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("T1_匹配[  代码]").Find(Sheet19.Range("a" & i), , , 1)
            If rng Is Nothing Then Set rng = Range("T2_匹配[  代码]").Find(Sheet19.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 2) = Round(Sheet19.Range("e" & i) / 100000000, 2)
            End If
        Next
    End If
    For Each gp In Range("T1_匹配[所属概念]")
        temp = ""
        js = 0
        For i = 2 To Sheet4.Range("aM1").Value
            If InStr(gp, ";" & Sheet4.Range("am" & i) & ";") > 0 Then
                'If Sheet4.Range("am" & i).Interior.Color = 13421823 Then gp.Offset(0, -2).Interior.Color = 13421823
                temp = temp & Sheet4.Range("am" & i) & ";"
                'js = js + 1
            End If
        Next
        If temp <> "" Then temp = Left(temp, Len(temp) - 1)
        'gp.Offset(0, -1).Value = js
        gp.Value = temp
    Next

    For Each gp In Range("T2_匹配[所属概念]")
        temp = ""
        js = 0
        For i = 2 To Sheet4.Range("aR1").Value
            If InStr(gp, ";" & Sheet4.Range("ar" & i) & ";") > 0 Then
                temp = temp & Sheet4.Range("ar" & i) & ";"
            End If
        Next
        If temp <> "" Then temp = Left(temp, Len(temp) - 1)
        'gp.Offset(0, -1).Value = js
        gp.Value = temp
    Next

'-2  代码
'-1    名称
'0 竞价未匹配
'1 所属概念
'2 涨跌幅
'3 5日涨跌幅
'4 竞价量比
'5 今昨量比
'6 昨日连板天数
'7 25日涨停次数
'8 异动次数
'9 监管
'10 停牌

    '=====================标高变绿============
    If Sheet4.Range("h26").Interior.ColorIndex = 35 Then
        Set rng = Union(Range("T1_匹配[    名称]"), Range("T2_匹配[    名称]")).Find(Sheet4.Range("h25"), , , 1)
        If Not rng Is Nothing Then rng.Interior.ColorIndex = 35
    End If
    If Sheet4.Range("h28").Interior.ColorIndex = 35 Then
        Set rng = Union(Range("T1_匹配[    名称]"), Range("T2_匹配[    名称]")).Find(Sheet4.Range("h27"), , , 1)
        If Not rng Is Nothing Then rng.Interior.ColorIndex = 35
    End If

    '变绿
    yz = Sheet4.Range("H12") '阈值
    For Each gp In Union(Range("T1_匹配[所属行业]"), Range("T2_匹配[所属行业]"))
        '比较阈值
        If gp.Offset(0, 3) >= yz And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
        '1：情绪好和差时 ，异动次数大于等于3或者监管类型有数据或者停牌非0或今昨量比大于700或者竞价量比大于等于100或自由流通市值大于80，其中任何一种情况发生，就名称绿
        If gp.Offset(0, 8) >= 3 Or gp.Offset(0, 9) <> "" Or gp.Offset(0, 5) > 700 Or gp.Offset(0, 4) >= 1 Or gp.Offset(0, 11) > 200 Then gp.Offset(0, -1).Interior.ColorIndex = 35

        If qx = "差" Then
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 2) < 0 Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Offset(0, 2).Interior.ColorIndex = 35
            End If
            If gp <> "" Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Interior.ColorIndex = 35
            End If
            If gp.Offset(0, 6) > 2 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            If gp.Column = 12 And gp.Offset(0, 3) > 0.2 Then gp.Offset(0, -1).Interior.ColorIndex = 35
        Else
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then gp.Offset(0, 4).Interior.Color = 13551615
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then gp.Offset(0, 5).Interior.Color = 13551615

        End If

    Next

    '变红
    imax1 = 0
    imax2 = 0
    imin1 = 0
    imin2 = 0
    ijjlb1 = 0
    ijjlb2 = 0
    ijzlb1 = 0
    ijzlb2 = 0
    For Each gp In Range("T1_匹配[所属行业]")
        If qx = "好" Then
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then gp.Offset(0, 4).Interior.Color = 13551615
            If imin1 = 0 Then
                If gp < 0 And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    imin1 = 1
                    gp.Offset(0, -1).Interior.Color = 13551615
                End If
            End If
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then gp.Offset(0, 5).Interior.Color = 13551615
        Else '情绪差时
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then

                If gp.Offset(0, -1).Interior.ColorIndex <> 35 Then
                gp.Offset(0, 4).Interior.Color = 13551615
                        If gp.Offset(0, 4) >= ijjlb1 Then
                            ijjlb1 = gp.Offset(0, 4)
                            'gp.Offset(0, 4).Interior.ColorIndex = 3
                            'gp.Offset(0, -1).Interior.Color = 13551615
                        End If
                        If gp.Offset(0, 3) >= imax1 Then
                            imax1 = gp.Offset(0, 3)
                            gp.Offset(0, -1).Interior.Color = 13551615
                        End If
                End If
            End If
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then

                gp.Offset(0, 5).Interior.Color = 13551615
                        If gp.Offset(0, 5) >= ijzlb1 Then
                            ijzlb1 = gp.Offset(0, 5)
                            'gp.Offset(0, 5).Interior.ColorIndex = 3
                        End If
                'End If
            End If
        End If

    Next
    For Each gp In Range("T2_匹配[所属行业]")
        If qx = "好" Then
            竞价量比
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then gp.Offset(0, 4).Interior.Color = 13551615
            If imin1 = 0 Then
                If gp < 0 And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    imin2 = 1
                    gp.Offset(0, -1).Interior.Color = 13551615
                End If
            End If
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then gp.Offset(0, 5).Interior.Color = 13551615
        Else '情绪差时
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then

                If gp.Offset(0, -1).Interior.ColorIndex <> 35 Then
                gp.Offset(0, 4).Interior.Color = 13551615
                        If gp.Offset(0, 4) >= ijjlb2 Then
                            ijjlb2 = gp.Offset(0, 4)
                            'gp.Offset(0, 4).Interior.ColorIndex = 3
                            'gp.Offset(0, -1).Interior.Color = 13551615
                        End If
                        If gp.Offset(0, 3) >= imax2 Then
                            imax2 = gp.Offset(0, 3)
                            gp.Offset(0, -1).Interior.Color = 13551615
                        End If
                End If
            End If
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then

                'If gp.Offset(0, -1).Interior.ColorIndex <> 35 Then
                gp.Offset(0, 5).Interior.Color = 13551615
                        If gp.Offset(0, 5) >= ijzlb2 Then
                            ijzlb2 = gp.Offset(0, 5)
                            'gp.Offset(0, 5).Interior.ColorIndex = 3
                        End If
                'End If
            End If
        End If

    Next

    If qx = "好" Then

        If imin1 = 0 Then
            For Each gp In Range("T1_匹配[所属行业]")
                If gp = "" And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    gp.Offset(0, -1).Interior.Color = 13551615
                    Exit For
                End If
            Next
        End If
        If imin2 = 0 Then
            For Each gp In Range("T2_匹配[所属行业]")
                If gp = "" And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    gp.Offset(0, -1).Interior.Color = 13551615
                    Exit For
                End If
            Next
        End If
    Else '情绪差时
        For Each gp In Range("T1_匹配[竞价量比]")
            If gp = ijjlb1 Then
                gp.Interior.ColorIndex = 3
                'gp.Offset(0, -5).Interior.Color = 13551615
            End If

            If gp.Offset(0, 1) = ijzlb1 Then
                gp.Offset(0, 1).Interior.ColorIndex = 3
                If gp.Offset(0, -5).Interior.ColorIndex <> 35 Then
                    If gp >= 0.08 And gp < 1 Then gp.Offset(0, -5).Interior.Color = 13551615
                End If
            End If
        Next
        For Each gp In Range("T2_匹配[竞价量比]")
            If gp = ijjlb2 Then
                gp.Interior.ColorIndex = 3
                'gp.Offset(0, -5).Interior.Color = 13551615
            End If

            If gp.Offset(0, 1) = ijzlb2 Then
                gp.Offset(0, 1).Interior.ColorIndex = 3
                If gp.Offset(0, -5).Interior.ColorIndex <> 35 Then
                    If gp >= 0.08 And gp < 1 Then gp.Offset(0, -5).Interior.Color = 13551615
                End If
            End If
        Next
    End If


    '变黄
    For Each gp In Range("T1_匹配[    名称]")
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
            gp.Interior.ColorIndex = 36
            Exit For
        End If
    Next
    For Each gp In Range("T2_匹配[    名称]")
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
            gp.Interior.ColorIndex = 36
            Exit For
        End If
    Next

    Range("T1_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    For Each gp In Range("T1_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.3 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11) = "创百日新高" Then
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                 gp.Offset(0, -1).Interior.ColorIndex = 46
                Exit For
            End If
        End If
    Next

    For Each gp In Range("T2_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.3 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11) = "创百日新高" Then
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                 gp.Offset(0, -1).Interior.ColorIndex = 46
                Exit For
            End If
        End If
    Next
     For Each gp In Range("T1_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
             'gp.Offset(0, 2).Interior.ColorIndex = 29
            If rng5 = "" Then Set rng5 = gp.Offset(0, 2)
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                Set rng6 = gp.Offset(0, 2)
                Exit For
            End If
        End If
    Next

    If Not rng6 = "" Then
        rng6.Interior.ColorIndex = 29
    ElseIf Not rng5 = "" Then
        rng5.Interior.ColorIndex = 29
    End If


     For Each gp In Range("T2_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11).Interior.ColorIndex = 28 Then
            'gp.Offset(0, 2).Interior.ColorIndex = 29

            If rng3 = "" Then Set rng3 = gp.Offset(0, 2)
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) And rng4 = "" Then
                Set rng4 = gp.Offset(0, 2)
                Exit For
            End If

        End If
    Next

    If Not rng4 = "" Then
        rng4.Interior.ColorIndex = 29
    ElseIf Not rng3 = "" Then
        rng3.Interior.ColorIndex = 29
    End If

    Range("T1_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "120日涨跌幅", 2, , , , , , 1

End Sub
"""


def setColor3Purple(chuang_data):
    chuang_data = sorted(chuang_data, key=lambda x: x[1]["zhangdie4thday"], reverse=True)
    # chuang_data = dict(tmp)

    rng5 = None
    for (key, item) in chuang_data:
        if item["color1"] != 35 and  item["color10"] == 37:
            if rng5 is None:
                rng5 = item
            if item["color8"] != 38 and item["zuo_ri_lian_ban_tian_shu"] > 0:
                item["color3"] = 29
                return chuang_data
    if rng5 is not None:
        rng5["color3"] = 29
    return chuang_data


def setColorOrange(chuang_data):
    chuang_data = sorted(chuang_data, key=lambda x: x[1]["zhangfu120"], reverse=True)
    # chuang_data = dict(tmp)
    for (key, item) in chuang_data:
        if item["color1"] != 35 and  item["chuang_bai_ri_xin_gao"] > 0 and item[
            "color10"] == 37:
            item["color0"] = 46
            break
    return chuang_data


def setColor1Yellow(chuang_data):
    # 破20日均线
    chuang_data = sorted(chuang_data.items(), key=lambda x: x[1]["zhangfu120"], reverse=True)
    # chuang_data = dict(tmp)
    for (key, item) in chuang_data:
        if item["zhangdiefuqianfuquantoday"] > 0 and item[
            "po20"] < 0:
            item["color1"] = 36
            break
    return chuang_data


def setColor1Pink(chuang_data):
    for (key, item) in chuang_data.items():
        if item["color1"] != 35 and item["jingjiaweipipeijinetoday"] == 0 and item[
            "jingjiajinechengjiaoliangbi"] >= 0.08:
            item["color1"] = 13551615
            break
    return chuang_data


def setColor6Red(chuang_data_s, chuang_data):
    code = chuang_data_s["max_jingjiajinechengjiaoliangbi"]["code"]
    if code == "":
        return chuang_data
    chuang_data[code]["color6"] = 3
    return chuang_data


def setColor7Red(chuang_data_s, chuang_data):
    code = chuang_data_s["max_jingjiajinejingjialiangbi"]["code"]
    if code != "":
        chuang_data[code]["color7"] = 3

        if chuang_data[code]["color1"] != 35:
            if chuang_data[code]["jingjiajinechengjiaoliangbi"] >= 0.08 and \
                    chuang_data[code]["jingjiajinechengjiaoliangbi"] < 1:
                chuang_data[code]["color1"] = 13551615
    return chuang_data


def pi_pei_gai_nian(d):
    chuang_data = d["chuang_data"]
    zhu_data = d["zhu_data"]

    # execl:1004
    qx = d["qing_xu"]
    # yzcode = d["bu_zhang_data"]["yz"]
    bu_zhang_data = d["bu_zhang_data"]
    # 昨标高
    # if d["bu_zhang_data"]["zuo_biao_gao"]["color10"] == 35:
    #     code = d["bu_zhang_data"]["zuo_biao_gao"]["zhu_ban"]["code"]
    #     if code in zhu_data:
    #         zhu_data[code]["color1"] = 35
    #     if code in chuang_data:
    #         chuang_data[code]["color1"] = 35
    #
    # if d["bu_zhang_data"]["zuo_biao_gao"]["color20"] == 35:
    #     code = d["bu_zhang_data"]["zuo_biao_gao"]["zhu_ban"]["code"]
    #     if code in chuang_data:
    #         chuang_data[code]["color1"] = 35
    #     if code in zhu_data:
    #         zhu_data[code]["color1"] = 35

    # execl 1013
    chuang_data = definedcolor1(chuang_data, bu_zhang_data, qx)
    zhu_data = definedcolor1(zhu_data, bu_zhang_data, qx, 0)

    # execl 1055
    chuang_data_s = definedcolor2(chuang_data, qx)
    chuang_data = chuang_data_s["data"]

    # execl 1105
    zhu_data_s = definedcolor2(zhu_data, qx)
    zhu_data = zhu_data_s["data"]

    chuang_data = {code: item for (code, item) in chuang_data}
    zhu_data = {code: item for (code, item) in zhu_data}
    if qx == 1:
        # 对应
        #   If gp = "" And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
        if chuang_data_s["imin"] == 0:
            chuang_data = setColor1Pink(chuang_data)

        if zhu_data_s["imin"] == 0:
            zhu_data = setColor1Pink(zhu_data)
    else:
        #  If gp = ijjlb1 Then
        chuang_data = setColor6Red(chuang_data_s, chuang_data)
        # If gp.Offset(0, 1) = ijzlb1 Then
        chuang_data = setColor7Red(chuang_data_s, chuang_data)

        zhu_data = setColor6Red(zhu_data_s, zhu_data)
        zhu_data = setColor7Red(zhu_data_s, zhu_data)

    chuang_data = setColor1Yellow(chuang_data)
    zhu_data = setColor1Yellow(zhu_data)

    chuang_data = setColorOrange(chuang_data)
    zhu_data = setColorOrange(zhu_data)

    chuang_data = setColor3Purple(chuang_data)
    zhu_data = setColor3Purple(zhu_data)
    #
    # for (key, item) in chuang_data:
    #     if item["color1"] != 35 and item["color4"] != 13551615 and item["color4"] != 3:
    #         chuang_data[key]["color1"] = 36
    #         break
    #
    # for (key, item) in zhu_data.items():
    #     if item["color1"] != 35 and item["color4"] != 13551615 and item["color4"] != 3:
    #         zhu_data[key]["color1"] = 36
    #         break

    result = {
        "chuang_data": [item for code, item in chuang_data],
        "zhu_data": [item for code, item in zhu_data],
    }

    return result


def definedcolor1(chuang_data, bu_zhang_data, qx, is_chuang_ye=1):
    for (key, item) in chuang_data:
        item["color0"] = 0  # 代码
        item["color1"] = 0  # 名称
        item["color2"] = 0  # 竞价未匹配
        item["color3"] = 0  # 所属概念
        item["color4"] = 0  # 涨跌幅
        item["color5"] = 0  # 4日涨跌幅
        item["color6"] = 0  # 竞价量比
        item["color7"] = 0  # 今昨量比
        # item["color8"] = 0  # 昨日连板天数
        item["color9"] = 0  # 120日涨跌幅
        item["color10"] = 0  # 异动次数
        item["color11"] = 0  # 监管
        # item["color12"] = 0  # 创百日新高
        # item["color13"] = 0  # 代表N

        # # 符合n 且 昨日曾涨停 == 1
        # if "n" in item and item["n"] == 1:
        #     item["color10"] = 37
        #     if "N_zuidazhangfu" in item and item["N_zuidazhangfu"] > 0:
        #         item["color6"] = 38
        #     if "N_zuocengzhangting" in item and item["N_zuocengzhangting"] == 1:
        #         item["color6"] = 38

        # if item["zhangdie4thday"] > yzcode["zhangdie4thday"] and \
        #         item["jingjiajinechengjiaoliangbi"] >= 0.08:
        #     item["color1"] = 35
        xia_xian = code_config.CodeConfig().getCodeConfig()

        # 异动次数大于等于3 且异动是开的情况下 且 创百日新高 == 1
        if item["yidongcishu"] >= 3 and xia_xian["yd"] == 1 and item["chuang_bai_ri_xin_gao"] == 0:
            item["color1"] = 35

        #  监管类型有数据或者停牌非0或今昨量比大于700或者竞价量比大于等于100或 自由流通市值大于100且不符合塞力斯概念 H13
        if item["jianguanleixingyesterday"] != "" or \
                item["jingjiajinejingjialiangbi"] > 700 or \
                item["jingjiajinechengjiaoliangbi"] >= 1 or \
                (item["ziyouliutongshizhiyesterday"] / 10000 / 10000 > 100 and item["code"] !=
                 bu_zhang_data["zhong_jun"]["code"]):
            item["color1"] = 35

        if qx == -1:
            if item["jingjiajinechengjiaoliangbi"] >= 0.08 and item["zhangdiefuqianfuquantoday"] < 0 and item["code"] != \
                    bu_zhang_data["lian_ban_code"]["code"]:
                item["color1"] = 35
                item["color4"] = 35

            # if item["jingjiaweipipeijinetoday"] == 0:
            #     item["color1"] = 35
            #     item["color2"] = 35

            if item["lianxuzhangtingtianshuyesterday"] > 2:
                if is_chuang_ye == 1:
                    item["color1"] = 35
                elif item["lianxuzhangtingtianshuyesterday"] < bu_zhang_data["lian_ban_code"]["lianbantianshu"]:
                    #  连板天数 < 最大连板天数
                    item["color1"] = 35

            # 创业板情绪差原来是4日涨跌幅大于20%就绿改成4日涨跌幅大于100%
            if is_chuang_ye == 1 and item["zhangdie4thday"] >= 1 :
                item["color1"] = 35
        else:
            if item["jingjiajinechengjiaoliangbi"] >= 0.08 and item["jingjiajinechengjiaoliangbi"] < 1:
                item["color6"] = 13551615
            if item["jingjiajinejingjialiangbi"] >= 100 and item["jingjiajinejingjialiangbi"] < 700:
                item["color7"] = 13551615
    return chuang_data


# JingJiaJinEChengJiaoLiangBi      float64 ` column:"竞价量比;type=float"`
# JingJiaJinEJingJiaLiangBi        float64 ` column:"今昨量比;type=float"`
def definedcolor2(chuang_data, qx):
    imin = 0
    # 最大竞价量比 ijjlb
    max_jingjiajinechengjiaoliangbi = {'code': '', "data": 0}
    # 四日最大涨跌幅 imax
    max_zhangdie4thday = {'code': '', "data": 0}
    # 最大今昨量比 ijzlb
    max_jingjiajinejingjialiangbi = {'code': '', "data": 0}
    for (code, item) in chuang_data:
        if qx == 1:
            #  竞价量比 > 0.08 and 竞价量比 < 1 粉色
            if item["jingjiajinechengjiaoliangbi"] >= 0.08 and item["jingjiajinechengjiaoliangbi"] < 1:
                item["color6"] = 13551615
            if imin == 0:
                # 竞价未匹配 < 0 and 名字不是绿色 and 竞价量比 > 0.08
                if item["jingjiaweipipeijinetoday"] < 0 and item["color1"] != 35 and item[
                    "jingjiajinechengjiaoliangbi"] >= 0.08:
                    imin = 1
                    item["color1"] = 13551615
            # 今昨量比 > 100 and 今昨量比 <= 700 粉色
            if item["jingjiajinejingjialiangbi"] >= 100 and item["jingjiajinejingjialiangbi"] <= 700:
                item["color7"] = 13551615
        else:
            # 竞价量比 > 0.08 and 竞价量比 < 1
            # 颜色不是绿色 粉色
            if item["jingjiajinechengjiaoliangbi"] >= 0.08 and item["jingjiajinechengjiaoliangbi"] < 1:
                if item["color1"] != 35:
                    item["color6"] = 13551615

                    # 竞价量比
                    if item["jingjiajinechengjiaoliangbi"] > max_jingjiajinechengjiaoliangbi["data"]:
                        max_jingjiajinechengjiaoliangbi["data"] = item["jingjiajinechengjiaoliangbi"]
                        max_jingjiajinechengjiaoliangbi["code"] = code

                    # 四日最大涨跌幅
                    if item["zhangdie4thday"] > max_zhangdie4thday["data"]:
                        max_zhangdie4thday["data"] = item["zhangdie4thday"]
                        max_zhangdie4thday["code"] = code
                        item["color1"] = 13551615

            # 今昨量比 > 100 and 今昨量比 <= 700 粉色
            if item["jingjiajinejingjialiangbi"] >= 100 and item["jingjiajinejingjialiangbi"] <= 700:
                item["color7"] = 13551615
                if item["jingjiajinejingjialiangbi"] > max_jingjiajinejingjialiangbi["data"]:
                    max_jingjiajinejingjialiangbi["data"] = item["jingjiajinejingjialiangbi"]
                    max_jingjiajinejingjialiangbi["code"] = code
        # chuang_data[key] = item
    return {
        "imin": imin,
        "max_jingjiajinechengjiaoliangbi": max_jingjiajinechengjiaoliangbi,
        "max_zhangdie4thday": max_zhangdie4thday,
        "max_jingjiajinejingjialiangbi": max_jingjiajinejingjialiangbi,
        "data": chuang_data,
    }
