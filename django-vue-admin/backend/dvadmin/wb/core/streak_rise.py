from dvadmin.wb.core import concept, gn

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


# 取连涨股票
def lian_zhang_gu_piao(data):
    lianzhanggupiao = {}
    for (code, items) in data.items():
        if items["qushi"] != 1:
            continue
        items["suoshugainian"] = list(set(items["suoshugainian"]))
        lianzhanggupiao[code] = {
            "code": items["code"],
            "briefname": items["briefname"],
            "suoshugainian": items["suoshugainian"],  # 概念
            "lianxuzhangtingtianshuonehundred": items["lianxuzhangtingtianshuonehundred"],  # 25日涨停次数
            "jingjiaweipipeijinetoday": items["jingjiaweipipeijinetoday"],  # 未匹配金额
            "zhangtingfengdanetoday": items["zhangtingfengdanetoday"],  # 未匹配金额
            "zhangfu120": items["zhangfu120"],
        }

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


def die_ting_gu_piao(data):
    dietinggupiao = {}
    for (code, items) in data.items():
        if items["qushi"] == -1:
            items["suoshugainian"] = list(set(items["suoshugainian"]))
            dietinggupiao[code] = {
                "code": items["code"],
                "briefname": items["briefname"],
                "suoshugainian": items["suoshugainian"],  # 概念
                "dietingfengdane": items["dietingfengdane"],
                "jingjiaweipipeijinetoday": items["jingjiaweipipeijinetoday"],
                "zhangtingfengdanetoday": 0,
                "zhangfu120": items["zhangfu120"],
            }

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


def zha_ban_gu_piao(data):
    zhabangupiao = {}
    for (code, items) in data.items():
        if items["zha_ban"] != 1:
            continue
        items["suoshugainian"] = list(set(items["suoshugainian"]))
        zhabangupiao[code] = {
            "code": items["code"],
            "briefname": items["briefname"],
            "suoshugainian": items["suoshugainian"],  # 概念
            "zhangdiefuqianfuquantoday": items["zhangdiefuqianfuquantoday"],
            "ziyouliutongshizhiyesterday": items["ziyouliutongshizhiyesterday"],
            "zhangfu120": items["zhangfu120"],
        }

    return zhabangupiao


"""
Sub 取创百日新高股票()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("表1").Sort "趋势", 2, , , , , , 1
    Sheet5.Range("y2:ae99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("表1[  代码]")
        If rng.Offset(0, 20) = "创百日新高" Then
            Sheet5.Range("y" & h) = rng
            Sheet5.Range("z" & h) = rng.Offset(0, 1)
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
            Sheet5.Range("aa" & h) = ";" & Join(arr1, ";") & ";"
            'Sheet5.Range("ab" & h) = rng.Offset(0, 6) '涨跌幅
            Sheet5.Range("ab" & h) = Round(rng.Offset(0, 21) / 100000000, 2) '未匹配金额
            Sheet5.Range("ac" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '关闭字典
    
End Sub
"""


def bai_ri_xin_gao_gu_piao(data):
    chuangbairixingao = {}
    for (code, items) in data.items():
        if items["chuang_bai_ri_xin_gao"] != 1:
            continue
        items["suoshugainian"] = list(set(items["suoshugainian"]))
        chuangbairixingao[code] = {
            "code": items["code"],
            "briefname": items["briefname"],
            "suoshugainian": items["suoshugainian"],  # 概念
            "jingjiaweipipeijinetoday": items["jingjiaweipipeijinetoday"],
            "ziyouliutongshizhiyesterday": items["ziyouliutongshizhiyesterday"],
            "zhangtingfengdanetoday": items["zhangtingfengdanetoday"],
            "zhangfu120": items["zhangfu120"],
        }

    return chuangbairixingao


"""
Sub 取一字板股票()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("表1").Sort "趋势", 2, , , , , , 1
    Sheet5.Range("ag2:am99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("表1[  代码]")
        If rng.Offset(0, 21) <> "" Then
            Sheet5.Range("ag" & h) = rng
            Sheet5.Range("ah" & h) = rng.Offset(0, 1)
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
            Sheet5.Range("ai" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("aj" & h) = Round(rng.Offset(0, 21) / 100000000, 2) '未匹配金额
            Sheet5.Range("ak" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '关闭字典
    
End Sub
"""


def yi_zi_ban_gu_piao(data):
    yiziban = {}

    for (code, items) in data.items():
        if items["yi_zi_ban"] != 1:
            continue

        items["suoshugainian"] = list(set(items["suoshugainian"]))
        yiziban[code] = {
            "code": items["code"],
            "briefname": items["briefname"],
            "suoshugainian": items["suoshugainian"],  # 概念
            "jingjiaweipipeijinetoday": items["jingjiaweipipeijinetoday"],
            "ziyouliutongshizhiyesterday": items["ziyouliutongshizhiyesterday"],
            "zhangtingfengdanetoday": items["zhangtingfengdanetoday"],
            "zhangfu120": items["zhangfu120"],
        }

    return yiziban


"""
Sub 取首板股票()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("表1").Sort "趋势", 2, , , , , , 1
    Sheet5.Range("ag2:am99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("表1[  代码]")
        If rng.Offset(0, 21) <> "" Then
            Sheet5.Range("ag" & h) = rng
            Sheet5.Range("ah" & h) = rng.Offset(0, 1)
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
            Sheet5.Range("ai" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("aj" & h) = Round(rng.Offset(0, 21) / 100000000, 2) '未匹配金额
            Sheet5.Range("ak" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '关闭字典
    
End Sub
"""


def shou_ban_gu_piao(data):
    shoubangupiao = {}
    for (code, items) in data.items():
        if items["shou_ban"] == 0:
            continue

        items["suoshugainian"] = list(set(items["suoshugainian"]))
        shoubangupiao[code] = {
            "code": items["code"],
            "briefname": items["briefname"],
            "suoshugainian": items["suoshugainian"],  # 概念
            "jingjiaweipipeijinetoday": items["jingjiaweipipeijinetoday"],
            "zhangtingfengdanetoday": items["zhangtingfengdanetoday"],
            "ziyouliutongshizhiyesterday": items["ziyouliutongshizhiyesterday"],
            "zhangfu120": items["zhangfu120"],
        }

    return shoubangupiao


"""
Sub 生成连涨概念()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr

    'nogn = ";富时罗素概念;富时罗素概念股;标普道琼斯A股;沪股通;深股通;融资融券;转融券标的;送转填权;股权转让;并购重组;超跌;MSCI概念;一季报增长;业绩增长;年报增长;超跌;"
    '取出有效概念合并成一个长字符串
    Sheet6.Range("a2:b99999").Clear
    If Sheet5.Range("a2") = "" Then Exit Sub
    hs = Sheet5.Range("a1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("c" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            'If InStr(nogn, ";" & arr(i) & ";") < 1 Then '去掉不要的概念
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        'dic(arr(i)) = Evaluate("COUNTIFS(连涨股票!C:C,""*;" & arr(i) & ";*"")")
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    'If Range("创业板概念[#data]").Rows.Count > 1 Then Range("创业板概念[#data]").Delete Shift:=xlShiftUp '清空原表
    'Range("创业板概念[实际流通]").NumberFormatLocal = "0.0000_ "
    'Range("创业板概念[[#Headers],[所属概念]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    'Range("创业板概念[[#Headers],[计数]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)
    
    Sheet6.Range("a2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("b2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '关闭字典
    'Sheet6.Range("a:b").Sort "连涨股票数", 2, , , , , , 1
End Sub
"""


def step6(data):
    suoshugainian = [suoshugainian for (code, item) in data.items() for suoshugainian in item["suoshugainian"]]
    unique_suoshugainian = list(set(suoshugainian))
    lianzhanggainian = {gn: suoshugainian.count(gn) for gn in unique_suoshugainian}
    sorted_lian_zhang = sorted(lianzhanggainian.items(), key=lambda x: x[1], reverse=True)
    lianzhanggainian = dict(sorted_lian_zhang)
    return lianzhanggainian


def lian_zhang_gai_nian(data):
    return step6(data)


"""
Sub 生成跌停概念()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("d2:e99999").Clear
    If Sheet5.Range("i2") = "" Then Exit Sub
    '取出有效概念合并成一个长字符串
    hs = Sheet5.Range("i1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("k" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    
    Sheet6.Range("d2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("e2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '关闭字典
    'Sheet6.Range("a:b").Sort "连涨股票数", 2, , , , , , 1
End Sub
"""


def die_ting_gai_nian(data):
    return step6(data)


"""
Sub 生成炸板概念()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("g2:h99999").Clear
    If Sheet5.Range("s2") = "" Then Exit Sub
    '取出有效概念合并成一个长字符串
    hs = Sheet5.Range("s1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("s" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    
    Sheet6.Range("g2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("h2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '关闭字典
    'Sheet6.Range("a:b").Sort "连涨股票数", 2, , , , , , 1
End Sub
"""


def zha_ban_gai_nian(data):
    return step6(data)


"""
Sub 生成创百日新高概念()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("j2:k99999").Clear
    If Sheet5.Range("aa2") = "" Then Exit Sub
    '取出有效概念合并成一个长字符串
    hs = Sheet5.Range("aa1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("aa" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    
    Sheet6.Range("j2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("k2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '关闭字典
    'Sheet6.Range("a:b").Sort "连涨股票数", 2, , , , , , 1
End Sub
"""


def chuang_bai_ri_xin_gao_gai_nian(data):
    return step6(data)


"""
Sub 生成一字板概念()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("m2:n99999").Clear
    If Sheet5.Range("ai2") = "" Then Exit Sub
    '取出有效概念合并成一个长字符串
    hs = Sheet5.Range("ai1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("ai" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    
    Sheet6.Range("m2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("n2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '关闭字典
    'Sheet6.Range("a:b").Sort "连涨股票数", 2, , , , , , 1
End Sub
"""


def yi_zi_ban_gai_nian(data):
    return step6(data)


"""
Sub 生成首板概念()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("p2:q99999").Clear
    If Sheet5.Range("aq2") = "" Then Exit Sub
    '取出有效概念合并成一个长字符串
    hs = Sheet5.Range("aq1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("aq" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    
    Sheet6.Range("p2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("q2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '关闭字典
    'Sheet6.Range("a:b").Sort "连涨股票数", 2, , , , , , 1
End Sub
"""


def shou_ban_gai_nian(data):
    return step6(data)


"""
Sub 取涨停原因()
    Dim rng As Range
    If Sheet5.Range("a2") = "" Then Exit Sub
    hs = Sheet5.Range("a1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("c" & i), ";")
        概念 = ""
        计数 = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("a:a").Find(a, , , 1) '精确
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = 概念 & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("f" & i) = 概念
        Sheet5.Range("g" & i) = 计数
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(表1[实际流通],表1[所属概念],""*;" & 概念 & ";*"")") + Evaluate("SUMIFS(表2[实际流通],表2[所属概念],""*;" & 概念 & ";*"")")
    Next
    '计算原因计数
'    For i = 2 To hs
'
'    Next
    Sheet5.Range("a:h").Sort "涨停大肉数", 2, , , , , , 1
End Sub
"""


def step12(lianzhanggupiao, lianzhanggainian):
    lianzhanggupiao2 = {}
    for (code, items) in lianzhanggupiao.items():
        items["yuanyin"] = []
        items["cishu"] = 0
        for (gn, count) in lianzhanggainian.items():
            if gn not in items["suoshugainian"]:
                continue
            if count > items["cishu"]:
                items["yuanyin"].append(gn)
                items["cishu"] = count
            elif count == items["cishu"]:
                items["yuanyin"].append(gn)
        lianzhanggupiao2[code] = items
    return lianzhanggupiao2


def zhang_ting_shi_pei_gu_piao(lianzhanggupiao, lianzhanggainian):
    return step12(lianzhanggupiao, lianzhanggainian)


"""
Sub 取跌停原因()
    Dim rng As Range
    If Sheet5.Range("i2") = "" Then Exit Sub
    hs = Sheet5.Range("i1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("k" & i), ";")
        概念 = ""
        计数 = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("d:d").Find(a, , , 1) '精确
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = 概念 & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("n" & i) = 概念
        Sheet5.Range("o" & i) = 计数
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(表1[实际流通],表1[所属概念],""*;" & 概念 & ";*"")") + Evaluate("SUMIFS(表2[实际流通],表2[所属概念],""*;" & 概念 & ";*"")")
    Next
    Sheet5.Range("i:o").Sort "跌停大面数", 2, , , , , , 1
End Sub
"""


def die_ting_shi_pei_gu_piao(dietinggupiao, dietinggainian):
    return step12(dietinggupiao, dietinggainian)


"""
Sub 取炸板原因()
    Dim rng As Range
    If Sheet5.Range("q2") = "" Then Exit Sub
    hs = Sheet5.Range("q1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("s" & i), ";")
        概念 = ""
        计数 = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("g:g").Find(a, , , 1) '精确
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = 概念 & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("v" & i) = 概念
        Sheet5.Range("w" & i) = 计数
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(表1[实际流通],表1[所属概念],""*;" & 概念 & ";*"")") + Evaluate("SUMIFS(表2[实际流通],表2[所属概念],""*;" & 概念 & ";*"")")
    Next
    Sheet5.Range("q:w").Sort "炸板数", 2, , , , , , 1
End Sub
"""


def zha_ban_shi_pei_gu_piao(zhabangupiao, zhabangainian):
    return step12(zhabangupiao, zhabangainian)


"""
Sub 取创百日新高原因()
    Dim rng As Range
    If Sheet5.Range("y2") = "" Then Exit Sub
    hs = Sheet5.Range("y1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("aa" & i), ";")
        概念 = ""
        计数 = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("j:j").Find(a, , , 1) '精确
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = 概念 & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("ad" & i) = 概念
        Sheet5.Range("ae" & i) = 计数
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(表1[实际流通],表1[所属概念],""*;" & 概念 & ";*"")") + Evaluate("SUMIFS(表2[实际流通],表2[所属概念],""*;" & 概念 & ";*"")")
    Next
    Sheet5.Range("y:ae").Sort "创百日新高数", 2, , , , , , 1
End Sub

"""


def chuang_bai_ri_xin_gao_shi_pei_gai_nian(chuangbairixingao, chuangbairixingaogainnian):
    return step12(chuangbairixingao, chuangbairixingaogainnian)


"""
Sub 取一字板原因()
    Dim rng As Range
    If Sheet5.Range("ag2") = "" Then Exit Sub
    hs = Sheet5.Range("ag1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("ai" & i), ";")
        概念 = ""
        计数 = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("m:m").Find(a, , , 1) '精确
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = 概念 & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("al" & i) = 概念
        Sheet5.Range("am" & i) = 计数
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(表1[实际流通],表1[所属概念],""*;" & 概念 & ";*"")") + Evaluate("SUMIFS(表2[实际流通],表2[所属概念],""*;" & 概念 & ";*"")")
    Next
    Sheet5.Range("ag:am").Sort "今竞封数", 2, , , , , , 1
End Sub
"""


def yi_zi_ban_shi_pei_gu_piao(yizibangupiao, yizibangainian):
    return step12(yizibangupiao, yizibangainian)


"""
Sub 取首板原因()
    Dim rng As Range
    If Sheet5.Range("ao2") = "" Then Exit Sub
    hs = Sheet5.Range("ao1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("aq" & i), ";")
        概念 = ""
        计数 = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("p:p").Find(a, , , 1) '精确
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = 概念 & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > 计数 Then
                        计数 = rng.Offset(0, 1)
                        概念 = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("at" & i) = 概念
        Sheet5.Range("au" & i) = 计数
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(表1[实际流通],表1[所属概念],""*;" & 概念 & ";*"")") + Evaluate("SUMIFS(表2[实际流通],表2[所属概念],""*;" & 概念 & ";*"")")
    Next
    Sheet5.Range("ao:au").Sort "首板数", 2, , , , , , 1
End Sub
"""


def shou_ban_shi_pei_gu_piao(shoubangupiao, shoubangainian):
    return step12(shoubangupiao, shoubangainian)


"""
Sub 排列涨停原因()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    Sheet7.Cells.Clear
    If Sheet5.Range("a2") = "" Then Exit Sub
    概念计数 = 0
    hs = Sheet5.Range("a1").End(xlDown).Row
    Sheet7.Cells(1, 1) = "日期"
    Sheet7.Cells(1, 2) = Date
    Sheet7.Cells(2, 1) = "涨停大肉"
    Sheet7.Cells(2, 1).Interior.ColorIndex = 36
    For i = 2 To hs
        arr = Split(Sheet5.Range("f" & i), ";")
        '概念 = Sheet5.Range("f" & i)
        For Each 概念 In arr
            If 概念 <> "" Then
                If Not dic.exists(概念) Then
                    dic(概念) = 1
                    Sheet7.Cells(3, 概念计数 * 3 + 1) = 概念

                    Sheet7.Cells(3, 概念计数 * 3 + 2) = 容量

                    Sheet7.Cells(4, 概念计数 * 3 + 1) = "名称"
                    Sheet7.Cells(4, 概念计数 * 3 + 2) = "竞价未匹配"
                    Set rng = Sheet5.Range("f:f").Find(";" & 概念 & ";", , , 2) '模糊
                    h = 4
                    If Not rng Is Nothing Then
                        未匹配求和 = 0
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            h = h + 1
                            Sheet7.Cells(h, 概念计数 * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, 概念计数 * 3 + 2) = rng.Offset(0, 2) '未匹配金额
                            未匹配求和 = 未匹配求和 + rng.Offset(0, 2)
                            Set rng = Sheet5.Range("f:f").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(3, 概念计数 * 3 + 2) = 未匹配求和
                    概念计数 = 概念计数 + 1
                    
                End If
            End If
        Next
    Next
End Sub
"""


def zhang_ting_yuan_yin(lianzhanggupiao, lianzhanggainian):
    lian_zhang_sort = {}
    for (gn, count) in lianzhanggainian.items():
        gn_item = {
            "suoshugainian": gn,  # 概念
            "count": 0,  # 含有该概念股票数量
            "gai_nian_gu_piao": [],  # 含有该概念的股票
            "gai_nian_jing_jia_wei_pi_pei": 0,  # 竞价未匹配
            "zhangfu120": 0,
            "color": 0,
            "gai_nian_feng_dan_jin_e": 0,
            "gai_nian_die_ting_feng_dan_jin_e": 0,
        }
        # gainian["gai_nian_gu_piao"] = []
        join_lian_zhang = 0
        for (code, item) in lianzhanggupiao.items():
            if gn in item["yuanyin"]:
                gn_item["gai_nian_gu_piao"].append(item)
                join_lian_zhang = 1

        gn_item["count"] = len(gn_item["gai_nian_gu_piao"])
        gn_item["gai_nian_jing_jia_wei_pi_pei"] = sum(
            [x['jingjiaweipipeijinetoday'] for x in gn_item["gai_nian_gu_piao"]])

        gn_item["gai_nian_feng_dan_jin_e"] = sum(
            [x['zhangtingfengdanetoday'] for x in gn_item["gai_nian_gu_piao"]])

        gn_item["gai_nian_die_ting_feng_dan_jin_e"] = sum(
            [x['dietingfengdane'] for x in gn_item["gai_nian_gu_piao"] if 'dietingfengdane' in x])

        gn_item["zhangfu120"] = sum(
            [x['zhangfu120'] for x in gn_item["gai_nian_gu_piao"] if "zhangfu120" in x])
        if join_lian_zhang == 1:
            lian_zhang_sort[gn] = gn_item

    sorted_lian_zhang = sorted(lian_zhang_sort.items(), key=lambda x: x[1]["count"], reverse=True)
    lian_zhang_sort = dict(sorted_lian_zhang)

    return lian_zhang_sort


"""
Sub 排列跌停原因()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("i2") = "" Then Exit Sub
    概念计数 = 0
    hs = Sheet5.Range("i1").End(xlDown).Row
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "跌停大面"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    行数 = 行数 + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("n" & i), ";")
        '概念 = Sheet5.Range("f" & i)
        For Each 概念 In arr
            If 概念 <> "" Then
                If Not dic.exists(概念) Then
                    dic(概念) = 1
                    Sheet7.Cells(行数, 概念计数 * 3 + 1) = 概念
                    '容量 = Sheet5.Range("h" & i)
                    '容量 = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & 概念 & ";*"")/100000000,2)")
                    'Sheet7.Cells(行数, 概念计数 * 3 + 2) = 容量
                    'If 容量 < 9000 Then Sheet7.Cells(行数, 概念计数 * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 1) = "名称"
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 2) = "竞价未匹配"
                    Set rng = Sheet5.Range("n:n").Find(";" & 概念 & ";", , , 2) '模糊
                    If Not rng Is Nothing Then
                        h = 行数 + 2
                        未匹配求和 = 0
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, 概念计数 * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, 概念计数 * 3 + 2) = rng.Offset(0, -2)
                            未匹配求和 = 未匹配求和 + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("n:n").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(行数, 概念计数 * 3 + 2) = 未匹配求和
                    概念计数 = 概念计数 + 1
                End If
            End If
        Next
    Next
End Sub
"""


def step18(dietinggupiao, dietinggainian):
    return zhang_ting_yuan_yin(dietinggupiao, dietinggainian)


def die_ting_yuan_yin(dietinggupiao, dietinggainian):
    return step18(dietinggupiao, dietinggainian)


"""
Sub 排列炸板原因()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("q2") = "" Then Exit Sub
    概念计数 = 0
    hs = Sheet5.Range("q1").End(xlDown).Row
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "炸板"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    行数 = 行数 + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("v" & i), ";")
        '概念 = Sheet5.Range("f" & i)
        For Each 概念 In arr
            If 概念 <> "" Then
                If Not dic.exists(概念) Then
                    dic(概念) = 1
                    Sheet7.Cells(行数, 概念计数 * 3 + 1) = 概念
                    '容量 = Sheet5.Range("h" & i)
                    '容量 = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & 概念 & ";*"")/100000000,2)")
                    'Sheet7.Cells(行数, 概念计数 * 3 + 2) = 容量
                    'If 容量 < 9000 Then Sheet7.Cells(行数, 概念计数 * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 1) = "名称"
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 2) = "涨跌幅"
                    Set rng = Sheet5.Range("v:v").Find(";" & 概念 & ";", , , 2) '模糊
                    If Not rng Is Nothing Then
                        h = 行数 + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, 概念计数 * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, 概念计数 * 3 + 2) = rng.Offset(0, -2)
                            Sheet7.Cells(h, 概念计数 * 3 + 2).NumberFormatLocal = "0.00%"
                            h = h + 1
                             Set rng = Sheet5.Range("v:v").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    
                    概念计数 = 概念计数 + 1
                End If
            End If
        Next
    Next
End Sub
"""


def zha_ban_yuan_yin(zhabangupiao, zhabangainian):
    return step18(zhabangupiao, zhabangainian)


"""
Sub 排列创百日新高原因()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("y2") = "" Then Exit Sub
    概念计数 = 0
    hs = Sheet5.Range("y1").End(xlDown).Row
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "创百日新高"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    行数 = 行数 + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("ad" & i), ";")
        '概念 = Sheet5.Range("f" & i)
        For Each 概念 In arr
            If 概念 <> "" Then
                If Not dic.exists(概念) Then
                    dic(概念) = 1
                    Sheet7.Cells(行数, 概念计数 * 3 + 1) = 概念
                    '容量 = Sheet5.Range("h" & i)
                    '容量 = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & 概念 & ";*"")/100000000,2)")
                    'Sheet7.Cells(行数, 概念计数 * 3 + 2) = 容量
                    'If 容量 < 9000 Then Sheet7.Cells(行数, 概念计数 * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 1) = "名称"
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 2) = "竞价未匹配"
                    未匹配求和 = 0
                    Set rng = Sheet5.Range("ad:ad").Find(";" & 概念 & ";", , , 2) '模糊
                    If Not rng Is Nothing Then
                        h = 行数 + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, 概念计数 * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, 概念计数 * 3 + 2) = rng.Offset(0, -2) '竞价未匹配
                            未匹配求和 = 未匹配求和 + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("ad:ad").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(行数, 概念计数 * 3 + 2) = 未匹配求和
                    概念计数 = 概念计数 + 1
                End If
            End If
        Next
    Next
End Sub
"""


def chuang_bai_ri_xin_gao_yuan_yin(chuangbairixingao, chuangbairixingaogainnian):
    return step18(chuangbairixingao, chuangbairixingaogainnian)


"""
Sub 排列一字板原因()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("ag2") = "" Then Exit Sub
    概念计数 = 0
    hs = Sheet5.Range("ag1").End(xlDown).Row
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "今竞封"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    行数 = 行数 + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("al" & i), ";")
        '概念 = Sheet5.Range("f" & i)
        For Each 概念 In arr
            If 概念 <> "" Then
                If Not dic.exists(概念) Then
                    dic(概念) = 1
                    Sheet7.Cells(行数, 概念计数 * 3 + 1) = 概念
                    '容量 = Sheet5.Range("h" & i)
                    '容量 = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & 概念 & ";*"")/100000000,2)")
                    'Sheet7.Cells(行数, 概念计数 * 3 + 2) = 容量
                    'If 容量 < 9000 Then Sheet7.Cells(行数, 概念计数 * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 1) = "名称"
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 2) = "竞价未匹配"
                    未匹配求和 = 0
                    Set rng = Sheet5.Range("al:al").Find(";" & 概念 & ";", , , 2) '模糊
                    If Not rng Is Nothing Then
                        h = 行数 + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, 概念计数 * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, 概念计数 * 3 + 2) = rng.Offset(0, -2)
                            未匹配求和 = 未匹配求和 + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("al:al").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(行数, 概念计数 * 3 + 2) = 未匹配求和
                    概念计数 = 概念计数 + 1
                End If
            End If
        Next
    Next
End Sub
"""


def yi_zi_ban_yuan_yin(yizibangupiao, yizibangainian):
    return step18(yizibangupiao, yizibangainian)


"""
Sub 排列首板原因()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("ao2") = "" Then Exit Sub
    概念计数 = 0
    hs = Sheet5.Range("ao1").End(xlDown).Row
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "首板"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    行数 = 行数 + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("at" & i), ";")
        '概念 = Sheet5.Range("f" & i)
        For Each 概念 In arr
            If 概念 <> "" Then
                If Not dic.exists(概念) Then
                    dic(概念) = 1
                    Sheet7.Cells(行数, 概念计数 * 3 + 1) = 概念
                    '容量 = Sheet5.Range("h" & i)
                    '容量 = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & 概念 & ";*"")/100000000,2)")
                    'Sheet7.Cells(行数, 概念计数 * 3 + 2) = 容量
                    'If 容量 < 9000 Then Sheet7.Cells(行数, 概念计数 * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 1) = "名称"
                    Sheet7.Cells(行数 + 1, 概念计数 * 3 + 2) = "涨停封单额"
                    未匹配求和 = 0
                    Set rng = Sheet5.Range("at:at").Find(";" & 概念 & ";", , , 2) '模糊
                    If Not rng Is Nothing Then
                        h = 行数 + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, 概念计数 * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, 概念计数 * 3 + 2) = rng.Offset(0, -2)
                            未匹配求和 = 未匹配求和 + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("at:at").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(行数, 概念计数 * 3 + 2) = 未匹配求和
                    概念计数 = 概念计数 + 1
                End If
            End If
        Next
    Next
End Sub
"""


def shou_ban_yuan_yin(shoubangupiao, shoubangainian):
    return step18(shoubangupiao, shoubangainian)


"""
Sub 排列竞涨停竞跌停()
    Dim dic As Object
    Dim rng As Range
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "竞涨停"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    竞涨停 = Evaluate("round(SUM(一字板!E:E)/100000000,2)")
    Sheet7.Cells(行数 + 1, 1) = 竞涨停
    Sheet7.Cells(行数 + 3, 1) = "竞跌停"
    Sheet7.Cells(行数 + 3, 1).Interior.ColorIndex = 36
    竞跌停 = Evaluate("round(SUM(一字跌停!E:E)/100000000,2)")
    Sheet7.Cells(行数 + 4, 1) = 竞跌停
    
    Set rng = Sheet21.Range("A:A").Find("竞跌停")
    If Not rng Is Nothing Then
        If 竞跌停 > rng.Offset(1, 0) Then
            Sheet4.Range("H6") = "好"
            Sheet4.Range("H6").Interior.Color = 13421823
            Exit Sub
        End If
        If 竞跌停 < rng.Offset(1, 0) Then
            Sheet4.Range("H6") = "差"
            Sheet4.Range("H6").Interior.ColorIndex = 35
            Exit Sub
        End If
    End If
    Set rng = Sheet21.Range("A:A").Find("竞涨停")
    If Not rng Is Nothing Then
        If 竞涨停 > rng.Offset(1, 0) Then
            Sheet4.Range("H6") = "好"
            Sheet4.Range("H6").Interior.Color = 13421823
            Exit Sub
        End If
        If 竞涨停 < rng.Offset(1, 0) Then
            Sheet4.Range("H6") = "差"
            Sheet4.Range("H6").Interior.ColorIndex = 35
            Exit Sub
        End If
    End If
    Sheet4.Range("H6") = "平"
    Sheet4.Range("H6").Interior.Color = RGB(255, 255, 255)
End Sub
"""


def jing_jia_info(yizibangupiao, dietinggupiao):
    jin_jia = {
        "zhang_ting": sum([x['jingjiaweipipeijinetoday'] for (code, x) in yizibangupiao.items()]),
        "zhang_ting_count": len(yizibangupiao.items()),
        "die_ting": sum([x['jingjiaweipipeijinetoday'] for (code, x) in dietinggupiao.items()]),
        "die_ting_count": len(dietinggupiao.items()),
        "qing_xu": 0,
    }
    return jin_jia


"""
Sub 排列5日涨跌幅()
    '主板
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "主板"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    最高 = Evaluate("MAXIFS(表1[5日涨跌幅],表1[ [  代码] ],""<>SH.68*"",表1[ [  代码] ],""<>SZ.30*"")")
    Sheet7.Cells(行数 + 1, 1) = "代码"
    Sheet7.Cells(行数 + 1, 2) = "名称"
    Sheet7.Cells(行数 + 1, 3) = "所属概念"
    Sheet7.Cells(行数 + 1, 4) = "5日涨跌幅"
    Set rng = Range("表1[5日涨跌幅]").Find(最高)
    If Not rng Is Nothing Then
        h = 行数 + 2
'        firstAddress = rng.Address
'        Do
            Sheet7.Cells(h, 1) = rng.Offset(0, -13)
            Sheet7.Cells(h, 2) = rng.Offset(0, -12)
            Sheet7.Cells(h, 3) = rng.Offset(0, -9)
            Sheet7.Cells(h, 4) = Format(rng, "0.00%")
'            h = h + 1
'             Set rng = Range("表1[5日涨跌幅]").FindNext(rng)
'        Loop While Not rng Is Nothing And rng.Address <> firstAddress
    End If
    
    '创业板
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "创业板"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    最高 = Evaluate("MAXIFS(表1[5日涨跌幅],表1[ [  代码] ],""=SZ.30*"")")
    Sheet7.Cells(行数 + 1, 1) = "代码"
    Sheet7.Cells(行数 + 1, 2) = "名称"
    Sheet7.Cells(行数 + 1, 3) = "所属概念"
    Sheet7.Cells(行数 + 1, 4) = "5日涨跌幅"
    Set rng = Range("表1[5日涨跌幅]").Find(最高)
    If Not rng Is Nothing Then
        h = 行数 + 2
'        firstAddress = rng.Address
'        Do
            Sheet7.Cells(h, 1) = rng.Offset(0, -13)
            Sheet7.Cells(h, 2) = rng.Offset(0, -12)
            Sheet7.Cells(h, 3) = rng.Offset(0, -9)
            Sheet7.Cells(h, 4) = Format(rng, "0.00%")
'            h = h + 1
'             Set rng = Range("表1[5日涨跌幅]").FindNext(rng)
'        Loop While Not rng Is Nothing And rng.Address <> firstAddress
    End If
    
    '科创板
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "科创板"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    最高 = Evaluate("MAXIFS(表1[5日涨跌幅],表1[ [  代码] ],""=SH.68*"")")
    Sheet7.Cells(行数 + 1, 1) = "代码"
    Sheet7.Cells(行数 + 1, 2) = "名称"
    Sheet7.Cells(行数 + 1, 3) = "所属概念"
    Sheet7.Cells(行数 + 1, 4) = "5日涨跌幅"
    Set rng = Range("表1[5日涨跌幅]").Find(最高)
    If Not rng Is Nothing Then
        h = 行数 + 2
'        firstAddress = rng.Address
'        Do
            Sheet7.Cells(h, 1) = rng.Offset(0, -13)
            Sheet7.Cells(h, 2) = rng.Offset(0, -12)
            Sheet7.Cells(h, 3) = rng.Offset(0, -9)
            Sheet7.Cells(h, 4) = Format(rng, "0.00%")
'            h = h + 1
'             Set rng = Range("表1[5日涨跌幅]").FindNext(rng)
'        Loop While Not rng Is Nothing And rng.Address <> firstAddress
    End If
End Sub
"""


def max_zhang_fu5_gu_piao(data):
    data2 = {
        "zhu_ban": {"zhangfu5": -1000, "suoshugainian": [], "code": ""},
        "chuang_ye_ban": {"zhangfu5": -1000, "suoshugainian": [], "code": ""},
        "ke_chuang_ban": {"zhangfu5": -1000, "suoshugainian": [], "code": ""},
    }

    sorted_lian_zhang = sorted(data.items(), key=lambda x: x[1]["zhangfu5"], reverse=True)
    data = dict(sorted_lian_zhang)
    for (code, item) in data.items():
        prefix = code[0:2]
        if prefix != '68' and prefix != '30':
            if data2["zhu_ban"]["code"] == "":
                data2["zhu_ban"] = item

        elif prefix == '30':
            if data2["chuang_ye_ban"]["code"] == "":
                data2["chuang_ye_ban"] = item

        elif prefix == '68':
            if data2["ke_chuang_ban"]["code"] == "":
                data2["ke_chuang_ban"] = item
        if data2["zhu_ban"]["code"] != "" and data2["chuang_ye_ban"]["code"] != "" and data2["ke_chuang_ban"][
            "code"] != "":
            break
    return data2


def shang_zhang_sort(data):
    jin_jia = {
        "shang_zhang_count": len([x for x in data.items() if x["zhangdiefuqianfuquantoday"] > 0]),
    }
    return jin_jia
