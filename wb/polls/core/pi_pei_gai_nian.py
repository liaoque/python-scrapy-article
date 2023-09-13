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


def pi_pei_gai_nian(d):
    chuang_data = d["chuang_data"]
    zhu_data = d["zhu_data"]

    # execl:1004
    qx = d["qing_xu"]
    yzcode = d["bu_zhang_data"]["yz"]
    if d["bu_zhang_data"]["zuo_biao_gao"]["power10"] == 35:
        code = d["bu_zhang_data"]["zuo_biao_gao"]["zhu_ban"]["code"]
        if code in zhu_data:
            zhu_data[code]["power-1"] = 35
        if code in chuang_data:
            chuang_data[code]["power-1"] = 35

    if d["bu_zhang_data"]["zuo_biao_gao"]["power20"] == 35:
        code = d["bu_zhang_data"]["zuo_biao_gao"]["zhu_ban"]["code"]
        if code in chuang_data:
            chuang_data[code]["power-1"] = 35
        if code in zhu_data:
            zhu_data[code]["power-1"] = 35

    # execl 1013
    chuang_data = definedPower1(chuang_data, yzcode, qx)
    zhu_data = definedPower1(zhu_data, yzcode, qx, 0)

    # execl 1055
    chuang_data_s = definedPower2(chuang_data, qx)
    chuang_data = chuang_data_s["data"]

    # execl 1105
    zhu_data_s = definedPower2(zhu_data, qx)
    zhu_data = zhu_data_s["data"]

    if qx == 1:
        if chuang_data_s["imin"] == 0:
            for (key, item) in chuang_data.items():
                if item["power-1"] != 35 and item["jingjiaweipipeijinetoday"] == 0 and item[
                    "jingjiajinechengjiaoliangbi"] >= 0.08:
                    item["power-1"] = 13551615
                    break

        if zhu_data_s["imin"] == 0:
            for (key, item) in zhu_data.items():
                if item["power-1"] != 35 and item["jingjiaweipipeijinetoday"] == 0 and item[
                    "jingjiajinechengjiaoliangbi"] > 0.08:
                    item["power-1"] = 13551615
                    break
    else:
        if chuang_data_s["ijjlb"]["code"] != "":
            code = chuang_data_s["ijjlb"]["code"]
            chuang_data[code]["power4"] = 3

        if chuang_data_s["ijzlb"]["code"] != "":
            code = chuang_data_s["ijzlb"]["code"]
            chuang_data[code]["power5"] = 3


            if chuang_data[code]["power-1"] != 35:
                if chuang_data[code]["jingjiajinechengjiaoliangbi"] >= 0.08 and \
                        chuang_data[code]["jingjiajinechengjiaoliangbi"] < 1:
                    chuang_data[code]["power-1"] = 13551615

        if zhu_data_s["ijjlb"]["code"] != "":
            code = zhu_data_s["ijjlb"]["code"]
            zhu_data[code]["power4"] = 3

        if zhu_data_s["ijzlb"]["code"] != "":
            code = zhu_data_s["ijzlb"]["code"]
            zhu_data[code]["power5"] = 3
            if zhu_data[code]["power-1"] != 35:
                if zhu_data[code]["jingjiajinechengjiaoliangbi"] >= 0.08 and \
                        zhu_data[code]["jingjiajinechengjiaoliangbi"] < 1:
                    zhu_data[code]["power-1"] = 13551615

    for (key, item) in chuang_data.items():
        if item["power-1"] != 35 and item["power4"] != 13551615 and item["power4"] != 3:
            chuang_data[key]["power-1"] = 36
            break

    for (key, item) in zhu_data.items():
        if item["power-1"] != 35 and item["power4"] != 13551615 and item["power4"] != 3:
            zhu_data[key]["power-1"] = 36
            break

    sorted(chuang_data.items(), key=lambda x: x[1]["zhangfu120"], reverse=True)
    sorted(zhu_data.items(), key=lambda x: x[1]["zhangfu120"], reverse=True)

    result = {
        "bu_zhang": getbu_zhang(chuang_data, zhu_data),
        "n": getN(chuang_data, zhu_data)
    }

    return result


def getN(chuang_data, zhu_data):
    return {
        "chuang": nbu_zhang(chuang_data),
        "zhu": nbu_zhang(zhu_data),
    }


def nbu_zhang(chuang_data):
    rng5 = rng6 = ""
    for (key, item) in chuang_data.items():
        if item["power-1"] != 35 and item["jingjiaweipipeijinetoday"] <= 0 and item["zhangfu120"] > 0.3 and item[
            "zhangfu120"] < 0.8 and item["power10"] == 37:
            if rng5 == "":
                rng5 = key
            if item["power6"] == 38 and item["lianxuzhangtingtianshuyesterday"] > 0:
                rng6 = key
                break

    if rng6 != "":
        print(rng6)
        return chuang_data[rng6]
    elif rng5 != "":
        print(rng5)
        return chuang_data[rng5]
    return None


def getbu_zhang(chuang_data, zhu_data):
    return {
        "chuang": rulebu_zhang(chuang_data),
        "zhu": rulebu_zhang(zhu_data),
    }


def rulebu_zhang(chuang_data):
    bu_zhang = None
    for (key, item) in chuang_data.items():

        if item["power-1"] != 35 and item["jingjiaweipipeijinetoday"] <= 0 and item["zhangfu120"] > 0.3 and item[
            "zhangfu120"] < 0.8 and item["chuangbairixingao"] == 1:
            if item["power6"] == 38 and item["lianxuzhangtingtianshuyesterday"] > 0:
                chuang_data[key]["power-1"] = 46
                bu_zhang = item
                break
    return bu_zhang


def definedPower1(chuang_data, yzcode, qx, is_chuang_ye=1):
    for (key, item) in chuang_data.items():
        if key == "001368":
            print(key)
        item["power-1"] = 0
        item["power2"] = 0
        item["power0"] = 0
        item["power4"] = 0
        item["power5"] = 0
        item["power6"] = 0
        item["power7"] = 0
        item["power8"] = 0
        item["power9"] = 0
        item["power10"] = 0
        if item["zhangdie4thday"] > yzcode["zhangdie4thday"] and \
                item["jingjiajinechengjiaoliangbi"] >= 0.08 :
            item["power-1"] = 35

        #  异动次数大于等于3或者监管类型有数据或者停牌非0或今昨量比大于700或者竞价量比大于等于100或自由流通市值大于80
        if item["yidongcishu"] >= 3 or item["jianguanleixingyesterday"] != "" or \
                item["jingjiajinejingjialiangbi"] > 700 or \
                item["jingjiajinechengjiaoliangbi"] >= 1 or \
                (item["ziyouliutongshizhiyesterday"] / 100000000 > 200 and is_chuang_ye != 1):
            item["power-1"] = 35

        if qx == -1:
            if item["jingjiajinechengjiaoliangbi"] >= 0.08  and item["zhangdiefuqianfuquantoday"] < 0:
                item["power-1"] = 35
                item["power2"] = 35

            if item["ziyouliutongshizhiyesterday"] == 0:
                item["power-1"] = 35
                item["power0"] = 35

            if item["lianxuzhangtingtianshuyesterday"] >= 2:
                item["power-1"] = 35

            if is_chuang_ye == 1 and item["zhangdie4thday"] >= 0.2 * 100:
                item["power-1"] = 35
        else:
            if item["jingjiajinechengjiaoliangbi"] >= 0.08  and item["jingjiajinechengjiaoliangbi"] < 1:
                item["power4"] = 13551615
            if item["jingjiajinejingjialiangbi"] >= 100 and item["jingjiajinejingjialiangbi"] < 700:
                item["power5"] = 13551615
        chuang_data[key] = item
    return chuang_data

# JingJiaJinEChengJiaoLiangBi      float64 ` column:"竞价量比;type=float"`
# JingJiaJinEJingJiaLiangBi        float64 ` column:"今昨量比;type=float"`
def definedPower2(chuang_data, qx):
    imin = 0
    ijjlb = {'code': '', "data": 0}
    imax = {'code': '', "data": 0}
    ijzlb = {'code': '', "data": 0}
    for (key, item) in chuang_data.items():
        if key == "001368":
            print(key)
        if qx == 1:
            if item["jingjiajinechengjiaoliangbi"] >= 0.08  and item["jingjiajinechengjiaoliangbi"] < 1  :
                item["power4"] = 13551615
            if imin == 0:
                if item["jingjiaweipipeijinetoday"] < 0 and item["power-1"] != 35 and item[
                    "jingjiajinechengjiaoliangbi"] >= 0.08 :
                    imin = 1
                    item["power-1"] = 13551615

            if item["jingjiajinejingjialiangbi"] >= 100 and item["jingjiajinejingjialiangbi"] <= 700:
                item["power5"] = 13551615
        else:
            if item["jingjiajinechengjiaoliangbi"] >= 0.08 and item["jingjiajinechengjiaoliangbi"] < 1  :
                if item["power-1"] != 35:
                    item["power4"] = 13551615

                    if item["jingjiajinechengjiaoliangbi"] > ijjlb["data"]:
                        ijjlb["data"] = item["jingjiajinechengjiaoliangbi"]
                        ijjlb["code"] = key

                    if item["zhangdie4thday"] > imax["data"]:
                        imax["data"] = item["zhangdie4thday"]
                        imax["code"] = key
                        item["power-1"] = 13551615

            if item["jingjiajinejingjialiangbi"] >= 100 and item["jingjiajinejingjialiangbi"] <= 700:
                item["power5"] = 13551615
                if item["jingjiajinejingjialiangbi"] > ijzlb["data"]:
                    ijzlb["data"] = item["jingjiajinejingjialiangbi"]
                    ijzlb["code"] = key
        chuang_data[key] = item
    return {
        "imin": imin,
        "ijjlb": ijjlb,
        "imax": imax,
        "ijzlb": ijzlb,
        "data": chuang_data,
    }
