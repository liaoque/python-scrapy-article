
import polls.core.concept

"""
Sub 取连涨股票()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    Range("表1").Sort "趋势", 2, , , , , , 1
    'Range("表2").Sort "连涨天数", 2, , , , , , 1
    Sheet5.Range("a2:h99999").Clear
    'nogn = ";富时罗素概念;富时罗素概念股;标普道琼斯A股;沪股通;深股通;融资融券;转融券标的;送转填权;股权转让;并购重组;超跌;MSCI概念;一季报增长;业绩增长;年报增长;超跌;"
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("表1[  代码]")
        If rng.Offset(0, 18) = "涨停大肉" Then
            Sheet5.Range("a" & h) = rng
            Sheet5.Range("b" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            'Set dic = CreateObject("scripting.dictionary")
            For i = LBound(arr) To UBound(arr)
                'If InStr(nogn, ";" & arr(i) & ";") < 1 Then '去掉不要的概念
                    If arr(i) <> "" Then
                        If Not dic.exists(arr(i)) Then
                            dic(arr(i)) = 1
                        End If
                    End If
                'End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            'Set dic = Nothing '关闭字典
            Sheet5.Range("c" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("d" & h) = rng.Offset(0, 16)
            Sheet5.Range("h" & h) = Round(rng.Offset(0, 21) / 100000000, 2) '未匹配金额
            'Sheet5.Range("e" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next
    '主创涨停
    If Sheet15.Range("a2") <> "" Then
        h = Sheet15.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Sheet5.Range("a:a").Find(Sheet15.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 4) = Sheet15.Range("i" & i)
            End If
        Next
    End If
'    For Each rng In Range("表2[  代码]")
'        If rng.Offset(0, 7) < 1 Then Exit For
'        Sheet5.Range("a" & h) = rng
'        Sheet5.Range("b" & h) = rng.Offset(0, 1)
'        arr = Split(rng.Offset(0, 4), ";")
'        'Set dic = CreateObject("scripting.dictionary")
'        For i = LBound(arr) To UBound(arr)
'            If InStr(nogn, ";" & arr(i) & ";") < 1 Then '去掉不要的概念
'                If arr(i) <> "" Then
'                    If Not dic.exists(arr(i)) Then
'                        dic(arr(i)) = 1
'                    End If
'                End If
'            End If
'        Next
'        arr1 = dic.keys()
'        dic.RemoveAll
'        'Set dic = Nothing '关闭字典
'        Sheet5.Range("c" & h) = ";" & Join(arr1, ";") & ";"
'        Sheet5.Range("d" & h) = rng.Offset(0, 7)
'        Sheet5.Range("e" & h) = rng.Offset(0, 11)
'        h = h + 1
'    Next
    Set dic = Nothing '关闭字典
    
End Sub
"""

#取连涨股票
def step1(table1, data):

    lianzhanggupiao = {}
    for items in data:
        
        if items["qushi"] == 1:
            items["suoshugainian"] = list(set(items["suoshugainian"]))
            lianzhanggupiao[items["code"]] = {
                "code":items["code"],
                "briefname":items["briefname"],
                "suoshugainian":items["suoshugainian"], # 概念
                "lianxuzhangtingtianshuonehundred":items["lianxuzhangtingtianshuonehundred"], # 25日涨停次数
                "jingjiaweipipeijinetoday": items["jingjiaweipipeijinetoday"], # 未匹配金额
                "zhangtingfengdanetoday": 0, # 封单额
            }
    
    if len(table1) > 0 and len(table1[0]["ZhuChuangZhangTing"]) > 0:
        return lianzhanggupiao
    
    for items in table1[0]["ZhuChuangZhangTing"]:
        if items["code"] in lianzhanggupiao:
            lianzhanggupiao[items["code"]]["zhangtingfengdanetoday"] = items["zhangtingfengdanetoday"]
    
    return lianzhanggupiao

"""
Sub 取跌停股票()
    Dim rng, rng2 As Range
    Dim dic As Object
    Dim arr, arr1
    Range("表1").Sort "趋势", 2, , , , , , 1
    Sheet5.Range("i2:o99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("表1[  代码]")
        'If rng.Offset(0, 18) = "" Then Exit For
        If rng.Offset(0, 18) = "跌停大面" Then
            Sheet5.Range("i" & h) = rng
            Sheet5.Range("j" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("k" & h) = ";" & Join(arr1, ";") & ";"
            
            'Sheet5.Range("l" & h) = Round(rng.Offset(0, 21) / 100000000, 2) '未匹配金额
            Set rng2 = Sheet22.Range("a:a").Find(rng, , , 1) '精确
            If Not rng2 Is Nothing Then
                Sheet5.Range("l" & h) = Round(rng2.Offset(0, 4) / 100000000, 2) '未匹配金额
            Else
                Sheet5.Range("l" & h) = 0
            End If
            Sheet5.Range("m" & h) = rng.Offset(0, 3)
            h = h + 1
        End If
    Next

    Set dic = Nothing '关闭字典
    
"""
def step2(table1, data):
    
    dietinggupiao = {}
    for items in data:
        if items["qushi"] == -1:
            items["suoshugainian"] = list(set(items["suoshugainian"]))
            dietinggupiao[items["code"]] = {
                "code":items["code"],
                "briefname":items["briefname"],
                "suoshugainian":items["suoshugainian"], # 概念
                "dietingfengdane": items["dietingfengdane"], 
                "jingjiaweipipeijine": 0, 
            }
            
            
    if len(table1) > 0 and len(table1[0]["YiZiDieTing"]) > 0:
        return dietinggupiao
    
    for items in table1[0]["YiZiDieTing"]:
        if items["code"] in dietinggupiao:
            dietinggupiao[items["code"]]["jingjiaweipipeijine"] = items["jingjiaweipipeijine"]
            
    return dietinggupiao
           
    
"""
Sub 取炸板股票()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("表1").Sort "趋势", 2, , , , , , 1
    Sheet5.Range("q2:w99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("表1[  代码]")
        If rng.Offset(0, 19) = "炸板" Then
            Sheet5.Range("q" & h) = rng
            Sheet5.Range("r" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("s" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("t" & h) = rng.Offset(0, 6) '涨跌幅
            Sheet5.Range("u" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '关闭字典
    
End Sub
"""
def step3(table1, data):
    
    zhabangupiao = {}
    for items in data:
        if items["zhaban"] == 1:
            items["suoshugainian"] = list(set(items["suoshugainian"]))
            zhabangupiao[items["code"]] = {
                "code":items["code"],
                "briefname":items["briefname"],
                "suoshugainian":items["suoshugainian"], # 概念
                "zhangdiefuqianfuquantoday": items["zhangdiefuqianfuquantoday"], 
                "ziyouliutongshizhiyesterday": items["ziyouliutongshizhiyesterday"], 
            }
        
    return zhabangupiao


# 取一字板
def step4(table1, data):
    
    if len(table1) > 0 and len(table1[0]["YiZiBan"]) > 0:
        return data
    
    data2 = table1[0]["YiZiBan"]
    
    for items in data2:
        data[items["code"]]["yiziban"] = 0
        if items["code"] in data:
            data[items["code"]]["yiziban"] = items["jingjiaweipipeijinetoday"]
        
    return data


# 取首板（连板天数为1）的股票涨停封单额
def step5(table1, data):
    
    if len(table1) > 0 and len(table1[0]["ZhuChuangZhangTing"]) > 0:
        return data
    
    data2 = table1[0]["ZhuChuangZhangTing"]
    
    for items in data2:
        data[items["code"]]["zhuchuangzhangting"] = 0
        if items["code"] in data and items["lianbantianshutoday"] == 1:
            data[items["code"]]["zhuchuangzhangting"] = items["zhangtingfengdanetoday"]
        
    return data

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    