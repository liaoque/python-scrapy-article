from polls.core import concept, gn

"""
Sub 增加前后分号()
    'If Left(Sheet1.Range("E2"), 1) = ";" Then Exit Sub
    Debug.Print Now & "增加前后分号"
    Dim rng As Range
    For Each rng In Sheet1.Range("表[所属概念]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
    Next
    Sheet2.Range("s1") = "趋势" '先把趋势清空
    fd = 0 '默认封单为关
    If Sheet4.Range("h3") = "封单开" Then fd = 1 '如果封单是开，那么设置fd=1
    Range("表1[趋势]") = ""
    For Each rng In Sheet2.Range("表1[所属概念]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
        
        'rng.Offset(0, 14) = "" '先把趋势清空
        If fd = 0 Then '如果封单关
            If rng.Offset(0, 1) >= 0.05 Then rng.Offset(0, 14) = 1
            If rng.Offset(0, 1) < -0.095 Then rng.Offset(0, 14) = -1
        Else '否则（封单开）
            If rng.Offset(0, 2) > 0.095 Then rng.Offset(0, 14) = 1
            If rng.Offset(0, 2) < -0.095 Then rng.Offset(0, 14) = -1
            If rng.Offset(0, 4) <> 0 Then '防止收盘价为0，被除数不能为0
                If (rng.Offset(0, 4) - rng.Offset(0, 5)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = 1 '(收盘价-最低价)/收盘价 > 0.095
                If rng.Offset(0, 14) = "" And (rng.Offset(0, 3) - rng.Offset(0, 4)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = -1 '最高价-收盘价)/收盘价 > 0.095
            End If
        End If

'        If rng.Offset(0, 2) >= zf Then rng.Offset(0, 14) = 1
'        If rng.Offset(0, 14) = "" And rng.Offset(0, 6) <> 0 Then '昨日收盘价<>0
'            If (rng.Offset(0, 4) - rng.Offset(0, 5)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = 1
'            'If (rng.Offset(0, 4) - rng.Offset(0, 6)) / rng.Offset(0, 6) > 0.095 Then rng.Offset(0, 14) = 1 '(收盘价-昨日收盘价)/昨日收盘价
'        End If
'
'        If rng.Offset(0, 14) = "" And rng.Offset(0, 4) <> 0 Then
'            If (rng.Offset(0, 3) - rng.Offset(0, 4)) / rng.Offset(0, 4) > 0.095 Then
'                rng.Offset(0, 14) = -1
'            Else
'
'                If rng.Offset(0, 14) = "" And rng.Offset(0, 2) < -0.095 Then rng.Offset(0, 14) = -1
'            End If
'        End If
'        rng.Offset(0, 14) = qs
    Next
    'Range("表[所属概念]") = ";" & Range("表[所属概念]") & ";"
    Range("表[所属概念]").Replace ";;", ";", 2
    Range("表1[所属概念]").Replace ";;", ";", 2
    
    '去掉不要的概念
    'nogn = "富时罗素概念;富时罗素概念股;标普道琼斯A股;沪股通;深股通;融资融券;转融券标的;送转填权;股权转让;并购重组;超跌;MSCI概念;一季报增长;业绩增长;年报增长;超跌;央企国企改革;地方国企改革;国企改革;三季报增长;半年报预增;同花顺漂亮100"
    nogn = Sheet4.Range("h39")
    arr = Split(nogn, ";")
    For i = LBound(arr) To UBound(arr)
        If arr(i) <> "" Then
            Range("表[所属概念]").Replace ";" & arr(i) & ";", ";", 2
            Range("表1[所属概念]").Replace ";" & arr(i) & ";", ";", 2
        End If
    Next
    Range("表[所属概念]").Replace "概念;", ";", 2
    Range("表1[所属概念]").Replace "概念;", ";", 2
    
    '从今曾涨停取炸板
    Sheet2.Range("t1") = "炸板"
    If Sheet13.Range("a2") <> "" Then
        h = Sheet13.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("表1[  代码]").Find(Sheet13.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 19) = "炸板"
            End If
        Next
    End If
    '取创百日新低
    Sheet2.Range("u1") = "创百日新高"
    If Sheet14.Range("a2") <> "" Then
        h = Sheet14.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("表1[  代码]").Find(Sheet14.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 20) = "创百日新高"
            End If
        Next
    End If
    '取一字板
    Sheet2.Range("v1") = "一字板"
    If Sheet19.Range("a2") <> "" Then
        h = Sheet19.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("表1[  代码]").Find(Sheet19.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 21) = Sheet19.Range("e" & i)
            End If
        Next
    End If
    
        '取首板（连板天数为1）的股票涨停封单额
    Sheet2.Range("x1") = "首板"
    If Sheet15.Range("a2") <> "" Then
        h = Sheet15.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("表1[  代码]").Find(Sheet15.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                If Sheet15.Range("g" & i) = 1 Then rng.Offset(0, 23) = Sheet15.Range("i" & i)
            End If
        Next
    End If
    
'    '主创涨停
'    Sheet2.Range("w1") = "涨停封单额"
'    If Sheet15.Range("a2") <> "" Then
'        h = Sheet15.Range("a1").End(xlDown).Row
'        For i = 2 To h
'            Set rng = Range("表1[  代码]").Find(Sheet15.Range("a" & i), , , 1)
'            If Not rng Is Nothing Then
'                rng.Offset(0, 22) = Sheet15.Range("i" & i)
'            End If
'        Next
'    End If
    Range("表[涨跌幅]").NumberFormatLocal = "0.00% "
    Range("表1[涨跌幅]").NumberFormatLocal = "0.00% "
    Range("表[竞价涨幅]").NumberFormatLocal = "0.00% "
    Range("表1[竞价涨幅]").NumberFormatLocal = "0.00% "
End Sub
"""


def step1(data, fd=0):
    data2 = {}
    for (code, items) in data.items():

        if items["zhangdiefuqianfuquantoday"] == "":
            items["zhangdiefuqianfuquantoday"] = "0"
        items["zhangdiefuqianfuquantoday"] = float(items["zhangdiefuqianfuquantoday"])
        items["lowestpricetoday"] = float(items["lowestpricetoday"])
        items["higestpricetoday"] = float(items["higestpricetoday"])
        items["qushi"] = 0
        if fd == 0:
            # 竞价涨幅
            if items["jingjiazhangfutoday"] / 100 >= 0.05:
                items["qushi"] = 1
            elif items["jingjiazhangfutoday"] / 100 < -0.095:
                items["qushi"] = -1
        else:
            # 涨跌幅
            if items["zhangdiefuqianfuquantoday"] / 100 >= 0.095:
                items["qushi"] = 1
            elif items["zhangdiefuqianfuquantoday"] / 100 < -0.095:
                items["qushi"] = -1

            if items['shoupanjiatoday'] != 0:
                # (收盘价-最低价)/收盘价 > 0.095
                if (items['shoupanjiatoday'] - items["lowestpricetoday"]) / items['shoupanjiatoday'] > 0.095:
                    items["qushi"] = 1
                # 最高价-收盘价)/收盘价 > 0.095
                if items["qushi"] == 0 and (items["higestpricetoday"] - items['shoupanjiatoday']) / items[
                    'shoupanjiatoday'] > 0.095:
                    items["qushi"] = -1

        data[code]["zhaban"] = 0
        data[code]["chuangbairixingao"] = 0
        data[code]["jingjiaweipipeijinetoday"] = 0
        data[code]["zhangtingfengdanetoday"] = 0
        data[code]["yidongcishu"] = 0
        data[code]["jianguanleixingyesterday"] = ""
        data[code]["n10"] = 0
        data[code]["zuocengzhangting"] = 0

        data[code]["n20"] = 0
        data2[code] = items

    return data2


# 炸板
def step2(table1, data):
    if table1 is None or "JinCengZhangTing" not in table1:
        return data

    data2 = table1["JinCengZhangTing"]

    for items in data2:
        code = items["code"][0:-3]

        data[code]["zhaban"] = 1

    return data


# 创百日新高
def step3(table1, data):
    if table1 is None or "ChuangBaiRiXinGao" not in table1:
        return data

    data2 = table1["ChuangBaiRiXinGao"]

    for items in data2:
        code = items["code"]

        data[code]["chuangbairixingao"] = 1

    return data


# 取一字板
def step4(table1, data):
    if table1 is None or "YiZiBan" not in table1:
        return data

    data2 = table1["YiZiBan"]

    for items in data2:
        code = items["code"]
        data[code]["jingjiaweipipeijinetoday"] = items["jingjiaweipipeijinetoday"]

    return data


# 取首板（连板天数为1）的股票涨停封单额
def step5(table1, data):
    if table1 is None or "ZhuChuangZhangTing" not in table1:
        return data

    data2 = table1["ZhuChuangZhangTing"]

    for items in data2:
        code = items["code"]
        if items["lianbantianshutoday"] == 1:
            data[code]["zhangtingfengdanetoday"] = items["zhangtingfengdanetoday"]

    return data


# 取异动
def step6(table1, data):
    if table1 is None or "YiDong" not in table1:
        return data

    data2 = table1["YiDong"]

    for items in data2:
        code = items["code"][0:-3]

        if code in data:
            data[code]["jianguanleixingyesterday"] = items["jianguanleixingyesterday"]
            data[code]["yidongcishu"] = data[code]["yidongcishu"] + 1

    return data


# 取n10
def step7(table1, data):
    if table1 is None or "N10" not in table1:
        return data

    data2 = table1["N10"]

    for items in data2:
        code = items["code"][0:-3]
        data[code]["n10"] = 1
        if "zuocengzhangting" in items and items["zuocengzhangting"] == "曾涨停":
            data[code]["zuocengzhangting"] = 1

    return data


# 取n20
def step8(table1, data):
    if table1 is None or "N20" not in table1:
        return data

    data2 = table1["N20"]

    for items in data2:
        code = items["code"][0:-3]

        data[code]["n20"] = 1

    return data
