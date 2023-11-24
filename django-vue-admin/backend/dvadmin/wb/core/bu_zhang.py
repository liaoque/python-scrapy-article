from dvadmin.wb.core import concept
from dvadmin.wb.config import code_config

"""

Sub 补涨()
    Dim rng As Range
    Dim sb, zsb, h, i, imax As Integer
    Dim fd, fd2 As Double
    Dim arr
    Dim gn, outgn, maxgn, fdgn, str, yzgp As String
    Dim firstAddress
    '1、在"昨原因"表里面的昨首板和首板里相同概念的涨停封单额对比，只要昨首板涨停封单额大于首板涨停封单额的在首板概念上标绿。
    Set rng = Sheet21.Range("a:a").Find("首板")
    sb = 0 '首板行号
    If Not rng Is Nothing Then sb = rng.Row + 1

    Set rng = Sheet21.Range("a:a").Find("昨首板")
    zsb = 0 '昨首板行号
    If Not rng Is Nothing Then zsb = rng.Row + 1
    imax = 0
    fd = 0
    fd2 = 0
    maxgn = ""
    fdgn = ""

    Dim sortedKeys() As Variant
    Dim secondName As String

    secondName = ""

    Dim dict2 As Object
    Set dict2 = CreateObject("Scripting.Dictionary")

    If sb > 0 And zsb > 0 Then
        For i = 1 To 256 Step 3
            If Sheet21.Cells(sb, i) = "" Then Exit For
            '开始对比
            Set rng = Sheet21.Rows(zsb).Find(Sheet21.Cells(sb, i), , , 1)
            If Not rng Is Nothing Then
                If rng.Offset(0, 1) > Sheet21.Cells(sb, i + 1) Then
                    Sheet21.Cells(sb, i).Interior.ColorIndex = 35
                End If

            End If
            '4.找出""昨原因"表首板里非绿的最大股票个数的概念（如果最大股票个数的概念有多个取涨停封单额最大的概念）和最大涨停封单额的概念，填入结果表的补涨里。
            If Sheet21.Cells(sb, i).Interior.ColorIndex <> 35 Then
                dict2.Add Sheet21.Cells(sb, i), Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1
                If imax < Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1 Then
                    imax = Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1
                    maxgn = Sheet21.Cells(sb, i)
                    fd = Sheet21.Cells(sb, i + 1)
                ElseIf imax = Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1 Then
                    If fd < Sheet21.Cells(sb, i + 1) Then
                        maxgn = Sheet21.Cells(sb, i)
                        fd = Sheet21.Cells(sb, i + 1)
                    End If
                    If fd = Sheet21.Cells(sb, i + 1) Then
                        maxgn = maxgn & ";" & Sheet21.Cells(sb, i)
                    End If
                End If
                If fd2 < Sheet21.Cells(sb, i + 1) Then
                    fd2 = Sheet21.Cells(sb, i + 1)
                    fdgn = Sheet21.Cells(sb, i)
                ElseIf fd2 = Sheet21.Cells(sb, i + 1) Then
                    fdgn = fdgn & ";" & Sheet21.Cells(sb, i)
                End If
            End If
        Next

         ' 遇到新股与次新股和国企改革 就找第二梯队的概念
        If maxgn = "新股与次新股" Or maxgn = "国企改革" Then

            sortedKeys = SortDictionaryByValue(dict2)
            secondName = sortedKeys(0)

            If secondName = "新股与次新股" Or secondName = "国企改革" Then
                secondName = sortedKeys(1)

            End If
            maxgn = maxgn & ";" & secondName
        End If

        Set dict2 = Nothing '关闭字典
    End If

    '2、在"昨原因"表找到主板，创业板，科创板中5日涨跌幅最大的股票的所属概念和首板里非绿的概念比对，找出相同的概念，

    gn = ""
    outgn = ";"
    yzgp = "" '阈值股票名
    Set rng = Sheet21.Range("a:a").Find("主板")
    If Not rng Is Nothing Then
        gn = rng.Offset(2, 2)
        fd = rng.Offset(2, 3)
        yzgp = rng.Offset(2, 1)
    End If
    Set rng = Sheet21.Range("a:a").Find("创业板")
    If Not rng Is Nothing Then
        If fd < rng.Offset(2, 3) Then
            gn = rng.Offset(2, 2)
            fd = rng.Offset(2, 3)
            yzgp = rng.Offset(2, 1)
        End If
    End If
    Set rng = Sheet21.Range("a:a").Find("科创板")
    If Not rng Is Nothing Then
        firstAddress = rng.Address
        Do
            If rng.Interior.ColorIndex = 36 Then
                If fd < rng.Offset(2, 3) Then
                    gn = rng.Offset(2, 2)
                    fd = rng.Offset(2, 3)
                    yzgp = rng.Offset(2, 1)
                End If
                Exit Do
            End If
            Set rng = Sheet21.Range("a:a").FindNext(rng)
        Loop While Not rng Is Nothing And rng.Address <> firstAddress
    End If

    '取出阈值股票的5日涨幅
    Sheet4.Range("H11:H12") = ""
    Set rng = Sheet2.Range("b:b").Find(yzgp)
    If Not rng Is Nothing Then
        Sheet4.Range("H11") = yzgp
        Sheet4.Range("H12") = rng.Offset(0, 9)
    End If

    '3、在"table1"中找到5日涨跌幅最大的股票，这个例子是尚太科技，用这个股票的所属概念比对昨原因表里的首板的非绿的概念找出相同的概念。
    Set rng = Sheet2.Range("N:N").Find(Evaluate("max(Table1!N:N)"))
    If Not rng Is Nothing Then
        gn = gn & rng.Offset(0, -9)
        '处理风口
        If Left(rng.Offset(0, -13), 5) = "SH.68" Then
            Sheet4.Range("H35") = "科创板"
        ElseIf Left(rng.Offset(0, -13), 5) = "SZ.30" Then
            Sheet4.Range("H35") = "创业板"
        Else
            Sheet4.Range("H35") = "主板"
        End If
    End If
    Debug.Print gn
    If sb > 0 Then
        For i = 1 To 256 Step 3
            If Sheet21.Cells(sb, i) = "" Then Exit For
            '开始对比
            If Sheet21.Cells(sb, i).Interior.ColorIndex <> 35 Then
                If InStr(gn, ";" & Sheet21.Cells(sb, i) & ";") > 0 Then
                    outgn = outgn & Sheet21.Cells(sb, i) & ";"
                End If
            End If
        Next
    End If


    'Sheet4.Range("h9") = outgn & maxgn & ";" & fdgn & ";"
    str = ";"
    arr = Split(outgn & maxgn & ";" & fdgn & ";", ";")
    For i = LBound(arr) To UBound(arr)
        If arr(i) <> "" Then
            If InStr(str, ";" & arr(i) & ";") = 0 Then str = str & arr(i) & ";"
        End If
    Next

    '如果当天一字板 表是空的，就昨原因里首板的所有概念里非绿的概念加入 结果表的补涨框
    If Sheet19.Range("a2") = "" Then
        If Not rng Is Nothing Then sb = rng.Row + 1
        For i = 1 To 256 Step 3
            If Sheet21.Cells(sb, i) = "" Then Exit For
            '开始对比
            If Sheet21.Cells(sb, i).Interior.ColorIndex <> 35 Then
                    str = str & Sheet21.Cells(sb, i) & ";"
            End If
        Next
    End If


    Sheet4.Range("h9") = str
    昨标高
End Sub
"""


def bu_zhang(data, chuang_ye_ban_gn, today, yesterday):
    imax = 0  # 最多概念
    maxgn = []  # 最大概念
    fdgn = []  # 封单概念
    sortgn = []
    xia_xian = code_config.CodeConfig().getCodeConfig()
    fd = xia_xian["fd"]
    for gn, item in yesterday["shou_ban_sort"].items():
        # 趋势未变弱
        # 根据封单的股票数，取强势的首版概念
        # 根据封单额度，取强势的首版概念
        if "color" not in item or item["color"] != 35:
            sortgn.append({"gn": gn, "c": item["count"]})
            # if imax < item["count"]:
            #     imax = item["count"]
            #     maxgn = []
            #     maxgn.append(gn)
            #     fd = item["gai_nian_feng_dan_jin_e"]
            # elif imax == item["count"]:
            #     if fd < item["gai_nian_feng_dan_jin_e"]:
            #         maxgn = []
            #         maxgn.append(gn)
            #         fd = item["gai_nian_feng_dan_jin_e"]
            #     elif fd == item["gai_nian_feng_dan_jin_e"]:
            #         maxgn.append(gn)
            #
            # if fd2 < item["gai_nian_feng_dan_jin_e"]:
            #     fdgn = []
            #     fdgn.append(gn)
            #     fd2 = item["gai_nian_feng_dan_jin_e"]
        # elif fd2 == item["gai_nian_feng_dan_jin_e"]:
        #     fdgn.append(gn)

        # if "新股与次新股" in maxgn or "国企改革" in maxgn:
        #     sortgn = [item for item in sortgn if item["gn"] in ["新股与次新股", "国企改革"]]
        #     sortgn = sorted(sortgn, key=lambda x: x["c"], reverse=True)
        #     ngn = sortgn[1]["gn"]
        #     if "新股与次新股" == ngn or "国企改革" == ngn:
        #         ngn = sortgn[2]["gn"]
        #         maxgn.append(ngn)

    # 5日内的最强势概念和股票
    gn = []
    outgn = []
    yzcode = {}
    yzgp = ""  # 阈值股票名
    zhangfu5 = 0
    if yesterday["day_5_sort"]["zhu_ban"]["zhangfu5"] != -1000:
        gn = (yesterday["day_5_sort"]["zhu_ban"]["suoshugainian"])
        zhangfu5 = yesterday["day_5_sort"]["zhu_ban"]["zhangfu5"]
        yzgp = yesterday["day_5_sort"]["zhu_ban"]["code"][0:-3]

    if yesterday["day_5_sort"]["chuang_ye_ban"]["zhangfu5"] != -1000:
        if zhangfu5 < yesterday["day_5_sort"]["chuang_ye_ban"]["zhangfu5"]:
            zhangfu5 = yesterday["day_5_sort"]["chuang_ye_ban"]["zhangfu5"]
            gn = (yesterday["day_5_sort"]["chuang_ye_ban"]["suoshugainian"])
            yzgp = yesterday["day_5_sort"]["chuang_ye_ban"]["code"][0:-3]

    if yesterday["day_5_sort"]["ke_chuang_ban"]["zhangfu5"] != -1000:
        if zhangfu5 < yesterday["day_5_sort"]["ke_chuang_ban"]["zhangfu5"]:
            zhangfu5 = yesterday["day_5_sort"]["ke_chuang_ban"]["zhangfu5"]
            gn = (yesterday["day_5_sort"]["ke_chuang_ban"]["suoshugainian"])
            yzgp = yesterday["day_5_sort"]["ke_chuang_ban"]["code"][0:-3]

    # 连涨股票
    # zhu_chuang_zhang_ting = filter( lambda x: x[1]["zhu_chuang_zhang_ting"] == 1, data.items())
    # zhu_chuang_zhang_ting = sorted(zhu_chuang_zhang_ting, key=lambda x: x[1]["lianbantianshutoday"], reverse=True)
    # zhu_lianban = zhu_chuang_zhang_ting[0]

    lian_xu_duo_ri_yi_zi_ban = [data[gp]["lianbantianshutoday"] for gp in xia_xian["lian_xu_duo_ri_yi_zi_ban"]]
    # 连板股票 h10 - h11
    data2 = sorted(data.items(), key=lambda x: (x[1]["zhangdie4thday"], x[1]["lianbantianshutoday"]), reverse=True)
    lian_ban_code = getLianBanGuPiao(data2, lian_xu_duo_ri_yi_zi_ban, fd)

    if lian_ban_code["lianbantianshu"] > 4:
        lian_ban_code["lianbantianshu_coloer"] = 35

    if lian_ban_code["code"] in data:
        if fd == 1:
            if data[lian_ban_code["code"]]["zhangdiefuqianfuquantoday"] < -0.04: lian_ban_code["zhangdiefu_coloer"] = 35
        else:
            if data[lian_ban_code["code"]]["jingjiazhangfutoday"] < -0.04: lian_ban_code["zhangdiefu_coloer"] = 35

    # 120日涨跌幅 H12
    data2 = sorted(data.items(), key=lambda x: (x[1]["zhangdie4thday"]), reverse=True)
    lian_ban_code120 = {
        "code": data2[0][1]["code"],
        "zhangfu120": data2[0][1]["zhangfu120"],
        "zhangfu120_color": 0,
    }
    if data2[0][1]["zhangdie4thday"] < 0.2:
        lian_ban_code120["zhangfu120_color"] = 35

    # 賽里斯
    data2 = filter(lambda x: x[1]["zhangfu5"] > 0 and x[1]["ziyouliutongshizhiyesterday"] > 100 * 10000 * 10000,
                   data2)
    data2 = list(data2)

    zhong_jun = {
        "code": data2[0][0],
    }

    # '3、在"table1"中找到5日涨跌幅最大的股票，这个例子是尚太科技，用这个股票的所属概念比对昨原因表里的首板的非绿的概念找出相同的概念。
    max_code = max(data.items(), key=lambda x: x[1]["zhangfu5"])
    # if max_code[0][0:2] == "68":
    #     feng_kou = "科创板"
    # elif max_code[0][0:2] == "30":
    #     feng_kou = "创业板"
    # else:
    #     feng_kou = "主板"

    max_code = data[max_code[0]]

    # 取出阈值股票的5日涨幅
    # yzcode = data[yzgp]
    yzcode = {"name": "", "zhangdie4thday": 0}

    gn.extend(max_code["suoshugainian"])

    # 昨首版非綠的概念
    for (code, item2) in yesterday["shou_ban_sort"].items():
        if "color" in item2 and item2["color"] == 35:
            continue
        if item2["suoshugainian"] in gn:
            outgn.append(item2["suoshugainian"])

    # '如果当天一字板 表是空的，就昨原因里首板的所有概念里非绿的概念加入 结果表的补涨框    if len(today["yi_zi_ban_sort"].keys()) == 0:
    if len(today["yi_zi_ban_sort"].keys()) == 0:
        outgn.extend(yesterday["yi_zi_ban_sort"].keys())

    outgn.extend(maxgn)
    outgn.extend(fdgn)

    outgn = list(set(outgn))

    # outgn = filter(lambda x:x[1] in chuang_ye_ban_gn, outgn)

    gn = []
    # Offset(0, 4).Interior.ColorIndex <> 35
    # gn.Offset(0, 5).Interior.ColorIndex <> 35
    # gn.Offset(0, 6).Interior.ColorIndex <> 35
    for (item) in outgn:
        if item not in chuang_ye_ban_gn.keys():
            gn.append(item)
        else:
            if fd == 1:
                if chuang_ye_ban_gn[item]["jin_jing_feng"]["color"] != 35 and \
                        chuang_ye_ban_gn[item]["pan_zhong"]["color"] != 35 and \
                        chuang_ye_ban_gn[item]["die_ting"]["color"] != 35:
                    gn.append(item)
            else:
                if chuang_ye_ban_gn[item]["jin_jing_feng"]["color"] != 35 and \
                        chuang_ye_ban_gn[item]["die_ting"]["color"] != 35:
                    gn.append(item)

    bu_zhang = {
        "lian_ban_code": lian_ban_code,
        "lian_ban_code120": lian_ban_code120,
        "zhong_jun": zhong_jun,
        "feng_kou": "feng_kou",
        "yz": yzcode,
        "yz_rate": yzcode["zhangdie4thday"],
        "gn": outgn,
        "zuo_biao_gao": zuo_biao_gao(yesterday)
    }
    return bu_zhang


"""
找连板股票
"""


def getLianBanGuPiao(data2, lian_xu_duo_ri_yi_zi_ban, fd):
    lian_ban_code = {
        "code": "",
        "lianbantianshu": 0,
        "lianbantianshu_coloer": 35,
        "zhangdiefu_coloer": 0,
    }
    if fd == 1:
        data2 = sorted(data2, key=lambda x: (x[1]['lianbantianshutoday']),
                       reverse=True)
        for index, item in data2:
            if item["lianbantianshutoday"] in lian_xu_duo_ri_yi_zi_ban:
                continue
            lian_ban_code["code"] = item["code"]
            lian_ban_code["lianbantianshu"] = item["lianbantianshutoday"]
            break
    else:
        for index, item in data2:
            if item["lianxuzhangtingtianshuyesterday"] in lian_xu_duo_ri_yi_zi_ban:
                continue
            lian_ban_code["code"] = item["code"]
            lian_ban_code["lianbantianshu"] = item['lianxuzhangtingtianshuyesterday']
            break
    return lian_ban_code


"""
Sub 昨标高()
    Dim rng As Range
    Sheet4.Range("h25:h30") = ""
    Sheet4.Range("h25:h30").Interior.Pattern = xlNone
    
    Set rng = Sheet21.Range("a:a").Find("主板")
    If Not rng Is Nothing Then
        Sheet4.Range("h25") = rng.Offset(2, 1)
        Sheet4.Range("h26") = rng.Offset(2, 3)
    End If
    Set rng = Sheet21.Range("a:a").Find("创业板")
    If Not rng Is Nothing Then
        Sheet4.Range("h27") = rng.Offset(2, 1)
        Sheet4.Range("h28") = rng.Offset(2, 3)
    End If
    Set rng = Sheet21.Range("a:a").Find("科创板")
    If Not rng Is Nothing Then
        Sheet4.Range("h29") = rng.Offset(2, 1)
        Sheet4.Range("h30") = rng.Offset(2, 3)
    End If
    If Sheet4.Range("h26") > Sheet4.Range("h85") Then Sheet4.Range("h26").Interior.ColorIndex = 35
    If Sheet4.Range("h28") > Sheet4.Range("h87") Then Sheet4.Range("h28").Interior.ColorIndex = 35
End Sub
"""


def zuo_biao_gao(yesterday):
    return {}
    xian = code_config.CodeConfig().getCodeConfig()
    color10 = 0
    if yesterday["day_5_sort"]["zhu_ban"]["zhangfu5"] > xian["10cm"]:
        color10 = 35
    color20 = 0
    if yesterday["day_5_sort"]["chuang_ye_ban"]["zhangfu5"] > xian["20cm"]:
        color20 = 35

    return {
        "zhu_ban": yesterday["day_5_sort"]["zhu_ban"],
        "chuang_ye_ban": yesterday["day_5_sort"]["chuang_ye_ban"],
        "ke_chuang_ban": yesterday["day_5_sort"]["ke_chuang_ban"],

        "color10": color10,

        "color20": color20,
    }


def merge_shou_ban(yesterday, before_yesterday):
    for gn, item in yesterday["shou_ban_sort"].items():
        yesterday["shou_ban_sort"][gn]["color"] = 0

        if len(before_yesterday["yi_zi_ban_sort"].keys()) == 0 and len(
                yesterday["yi_zi_ban_sort"].keys()) == 0:
            break

        if gn not in before_yesterday["shou_ban_sort"]:
            continue

        if before_yesterday["shou_ban_sort"][gn]["gai_nian_feng_dan_jin_e"] > item[
            "gai_nian_feng_dan_jin_e"]:
            yesterday["shou_ban_sort"][gn]["color"] = 35

    return yesterday
