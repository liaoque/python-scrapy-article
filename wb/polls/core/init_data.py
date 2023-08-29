
import polls.core.concept
import polls.core.gn 

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

def step1(table1, fd = 1):
    data2 = {}
    
    if len(table1) == 0 or len(table1[0]["Table1FromJSON"]) == 0:
        return data2
    
    data = table1[0]["Table1FromJSON"]
    
    for items in data:
        items["qushi"] = 0
        if fd == 0:
            # 竞价涨幅
            if items["jingjiazhangfutoday"] >= 0.05:
                items["qushi"] = 1
            elif items["jingjiazhangfutoday"]  < -0.095:
                items["qushi"] = -1
        else:
            # 涨跌幅
            if items["zhangdiefuqianfuquantoday"] >= 0.095:
                items["qushi"] = 1
            elif items["zhangdiefuqianfuquantoday"] < -0.095:
                items["qushi"] = -1
            if items['shoupanjiatoday'] != 0:
                # (收盘价-最低价)/收盘价 > 0.095
                if items['shoupanjiatoday'] - items["lowestpricetoday"] /  items['shoupanjiatoday'] > 0.095:
                    items["qushi"] = 1
                #最高价-收盘价)/收盘价 > 0.095
                if items["qushi"] == "" and items["higestpricetoday"] - items['shoupanjiatoday'] /  items['shoupanjiatoday'] > 0.095:
                    items["qushi"] = -1
                    
        # 过滤概念
        suoshugainian = items["suoshugainian"].split(";")
        items["suoshugainian"] = concept.filter(suoshugainian)
        
        data2[items["code"]] = items
    
    data2 = gn.gn_merge(data2)
    return data2

#炸板
def step2(table1, data):
    
    if len(table1) == 0 or len(table1[0]["JinCengZhangTing"]) == 0:
        return data
    
    data2 = table1[0]["JinCengZhangTing"]
    
    for items in data2:
        data[items["code"]]["zhaban"] = 0
        if items["code"] in data:
            data[items["code"]]["zhaban"] = 1
        
    return data
    
    
# 创百日新高
def step3(table1, data):
    
    if len(table1) == 0 or len(table1[0]["ChuangBaiRiXinGao"]) == 0:
        return data
    
    data2 = table1[0]["ChuangBaiRiXinGao"]
    
    for items in data2:
        data[items["code"]]["chuangbairixingao"] = 0
        if items["code"] in data:
            data[items["code"]]["chuangbairixingao"] = 1
        
    return data


# 取一字板
def step4(table1, data):
    
    if len(table1) == 0 or len(table1[0]["YiZiBan"]) == 0:
        return data
    
    data2 = table1[0]["YiZiBan"]
    
    for items in data2:
        data[items["code"]]["jingjiaweipipeijinetoday"] = 0
        if items["code"] in data:
            data[items["code"]]["jingjiaweipipeijinetoday"] = items["jingjiaweipipeijinetoday"]
        
    return data


# 取首板（连板天数为1）的股票涨停封单额
def step5(table1, data):
    
    if len(table1) == 0 or len(table1[0]["ZhuChuangZhangTing"]) == 0:
        return data
    
    data2 = table1[0]["ZhuChuangZhangTing"]
    
    for items in data2:
        data[items["code"]]["zhangtingfengdanetoday"] = 0
        if items["code"] in data and items["lianbantianshutoday"] == 1:
            data[items["code"]]["zhangtingfengdanetoday"] = items["zhangtingfengdanetoday"]
        
    return data


# 合并 table概念
def step6(table1, name="Table" path="data.xlsx"):
    
    if len(table1) == 0 or len(table1[0][name]) == 0:
        return data
    
    data2 = table1[0][name]
    
    return gn.gn_merge(data2, path)



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    