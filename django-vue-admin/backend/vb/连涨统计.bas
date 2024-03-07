Attribute VB_Name = "连涨统计"
Sub 连涨算法()
    'Application.ScreenUpdating = False
    't = Timer
    Debug.Print Now & "连涨算法"
    Debug.Print Now & "取连涨股票"
    取连涨股票
    Debug.Print Now & "取跌停股票"
    取跌停股票
    Debug.Print Now & "取炸板股票"
    取炸板股票
    Debug.Print Now & "取创百日新高股票"
    取创百日新高股票
    Debug.Print Now & "取一字板股票"
    取一字板股票
    Debug.Print Now & "取首板股票"
    取首板股票
    
    Debug.Print Now & "生成连涨概念"
    生成连涨概念
    Debug.Print Now & "生成跌停概念"
    生成跌停概念
    Debug.Print Now & "生成炸板概念"
    生成炸板概念
    Debug.Print Now & "生成创百日新高概念"
    生成创百日新高概念
    Debug.Print Now & "生成一字板概念"
    生成一字板概念
    Debug.Print Now & "生成首板概念"
    生成首板概念
    
    Debug.Print Now & "取涨停原因"
    取涨停原因
    Debug.Print Now & "取跌停原因"
    取跌停原因
    Debug.Print Now & "取炸板原因"
    取炸板原因
    Debug.Print Now & "取创百日新高原因"
    取创百日新高原因
    Debug.Print Now & "取一字板原因"
    取一字板原因
    Debug.Print Now & "取首板原因"
    取首板原因
    
    Debug.Print Now & "排列涨停原因"
    排列涨停原因
    Debug.Print Now & "排列跌停原因"
    排列跌停原因
    Debug.Print Now & "排列炸板原因"
    排列炸板原因
    Debug.Print Now & "排列创百日新高原因"
    排列创百日新高原因
    Debug.Print Now & "排列一字板原因"
    排列一字板原因
    Debug.Print Now & "排列首板原因"
    排列首板原因
    
    排列竞涨停竞跌停
    排列5日涨跌幅
    '连涨记录
    'Application.ScreenUpdating = True
    'MsgBox "耗时：" & Round(Timer - t, 2) & "秒"
End Sub
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
                        If Not dic.Exists(arr(i)) Then
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
            Set rng = Sheet2.Range("a:a").Find(Sheet15.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 25) = Sheet15.Range("g" & i)
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
                    If Not dic.Exists(arr(i)) Then
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
    
End Sub
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
                    If Not dic.Exists(arr(i)) Then
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
Sub 取创百日新高股票()
    Dim rng, rng2 As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("表1").Sort "趋势", 2, , , , , , 1
    Sheet5.Range("y2:ae99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    i = 2
    For Each rng In Range("表1[  代码]")
     
        If rng.Offset(0, 20) = "创百日新高" Then
            Sheet5.Range("y" & h) = rng
            Sheet5.Range("z" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
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
            '   Set rng2 = Sheet15.Range("a:a").Find(rng, , , 1)
            '  If Not rng2 Is Nothing Then
            '    Sheet5.Range("ab" & h) = rng2.Offset(0, 8)
            '  End If
            h = h + 1
        End If
        
        
    Next

    Set dic = Nothing '关闭字典
    
End Sub
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
                    If Not dic.Exists(arr(i)) Then
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
Sub 取首板股票()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("表1").Sort "趋势", 2, , , , , , 1
    Sheet5.Range("ao2:au99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("表1[  代码]")
        If rng.Offset(0, 23) <> "" Then
            Sheet5.Range("ao" & h) = rng
            Sheet5.Range("ap" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("aq" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("ar" & h) = Round(rng.Offset(0, 23) / 100000000, 2) '涨停封单额
            Sheet5.Range("as" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '关闭字典
    
End Sub

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
                    If Not dic.Exists(arr(i)) Then
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
                    If Not dic.Exists(arr(i)) Then
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
                    If Not dic.Exists(arr(i)) Then
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
                    If Not dic.Exists(arr(i)) Then
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
                    If Not dic.Exists(arr(i)) Then
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
                    If Not dic.Exists(arr(i)) Then
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
    ' 连涨大肉股
    Range("连涨大肉股").Sort "涨停大肉数", 2, , , , , , 1
   ' Sheet5.Range("a:h").Sort "涨停大肉数", 2, , , , , , 1
End Sub

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
    Range("跌停大面股").Sort "跌停大面数", 2, , , , , , 1
   ' Sheet5.Range("i:o").Sort "跌停大面数", 2, , , , , , 1
End Sub
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
      Range("炸板股").Sort "炸板数", 2, , , , , , 1
   ' Sheet5.Range("q:w").Sort "炸板数", 2, , , , , , 1
End Sub
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
   ' Sheet5.Range("y:ae").Sort "创百日新高数", 2, , , , , , 1
     Range("百日新高股").Sort "创百日新高数", 2, , , , , , 1
End Sub

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
    'Sheet5.Range("ag:am").Sort "今竞封数", 2, , , , , , 1
      Range("一字板股").Sort "今竞封数", 2, , , , , , 1
End Sub

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
   ' Sheet5.Range("ao:au").Sort "首板数", 2, , , , , , 1
     Range("首板股").Sort "首板数", 2, , , , , , 1
End Sub

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
                If Not dic.Exists(概念) Then
                    dic(概念) = 1
                    Sheet7.Cells(3, 概念计数 * 3 + 1) = 概念
                    '容量 = Sheet5.Range("h" & i)
                    '容量 = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & 概念 & ";*"")/100000000,2)") ' + Evaluate("SUMIFS(表2[实际流通],表2[所属概念],""*;" & 概念 & ";*"")")
                    Sheet7.Cells(3, 概念计数 * 3 + 2) = 容量
                    'If 容量 < 9000 Then Sheet7.Cells(3, 概念计数 * 3 + 2).Interior.ColorIndex = 35
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
                            Sheet7.Cells(h, 概念计数 * 3 + 2) = rng.Offset(0, -1) '未匹配金额
                            未匹配求和 = 未匹配求和 + Sheet7.Cells(h, 概念计数 * 3 + 2)
                            Set rng = Sheet5.Range("f:f").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                        
                       ' For g = 5 To h
                        '    code = Sheet7.Range("a" & g)
                         '   Set rng = Sheet2.Range("b:b").Find(code, , , 1) '
                          '  Sheet7.Cells(g, 概念计数 * 3 + 2) = rng.Offset(0, 16) '未匹配金额
                         '   未匹配求和 = 未匹配求和 + rng.Offset(0, 16)
                       ' Next
                        
                    End If
                    Sheet7.Cells(3, 概念计数 * 3 + 2) = 未匹配求和
                    概念计数 = 概念计数 + 1
                    
                End If
            End If
        Next
    Next
End Sub

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
                If Not dic.Exists(概念) Then
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
                If Not dic.Exists(概念) Then
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
                If Not dic.Exists(概念) Then
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
                If Not dic.Exists(概念) Then
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
                If Not dic.Exists(概念) Then
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

Sub 排列竞涨停竞跌停()
    Dim dic As Object
    Dim rng As Range

    行数 = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(行数, 1) = "竞涨停"
    Sheet7.Cells(行数, 1).Interior.ColorIndex = 36
    竞涨停 = Evaluate("round(SUM(一字板!E:E)/100000000,1)")
    Sheet7.Cells(行数 + 1, 1) = 竞涨停
    Sheet7.Cells(行数 + 3, 1) = "竞跌停"
    Sheet7.Cells(行数 + 3, 1).Interior.ColorIndex = 36
    竞跌停 = Evaluate("round(SUM(一字跌停!E:E)/100000000,1)")
    Sheet7.Cells(行数 + 4, 1) = 竞跌停
    
     ' 这里无论是算出好还是差，如果最近一天的上涨列数据是大于4000家，就强制改成差
   ' If Evaluate("COUNTIFS(表1[ [涨跌幅] ],"">0"")") > 4000 Then Sheet4.Range("H6") = "差"
    Sheet7.Cells(行数, 7) = "上涨数量"
    Sheet7.Cells(行数 + 1, 7) = Evaluate("COUNTIFS(表1[ [涨跌幅] ],"">0"")")
    Sheet7.Cells(行数, 7).Interior.ColorIndex = 36
    Set rng = Sheet21.Range("A:A").Find("竞跌停")
    If Not rng Is Nothing Then
      Sheet7.Cells(行数 + 4, 2) = 竞跌停 - rng.Offset(1, 0)
      '  If 竞跌停 > rng.Offset(1, 0) Then
      '      Sheet4.Range("H6") = "好"
      '      Sheet4.Range("H6").Interior.Color = 13421823
      '      Exit Sub
      '  End If
      '  If 竞跌停 < rng.Offset(1, 0) Then
      '      Sheet4.Range("H6") = "差"
      '      Sheet4.Range("H6").Interior.ColorIndex = 35
      '      Exit Sub
      '  End If
    End If
    Set rng = Sheet21.Range("A:A").Find("竞涨停")
    If Not rng Is Nothing Then
        Sheet7.Cells(行数 + 1, 2) = 竞涨停 - rng.Offset(1, 0)
       ' If 竞涨停 > rng.Offset(1, 0) Then
       '     Sheet4.Range("H6") = "好"
       '     Sheet4.Range("H6").Interior.Color = 13421823
       '     Exit Sub
       ' End If
       ' If 竞涨停 < rng.Offset(1, 0) Then
       '     Sheet4.Range("H6") = "差"
       '     Sheet4.Range("H6").Interior.ColorIndex = 35
       '     Exit Sub
       ' End If
    End If
    '先看涨停原因表里的竞涨停金额减 昨原因表的竞涨停金额 获得数据保存 ，然后看涨停原因表里的竞跌停减去昨原因表的竞跌停 获得数字保存
    '然后把第一个保存的数字减去第二个保存的数字，正数情绪好，负数情绪差
    Sheet7.Cells(行数 + 4, 3) = Sheet7.Cells(行数 + 4, 2) + Sheet7.Cells(行数 + 1, 2)
    If Sheet7.Cells(行数 + 4, 3) > 0 Then
        Sheet4.Range("H6") = "好"
        Sheet4.Range("H6").Interior.Color = 13421823
    ElseIf Sheet7.Cells(行数 + 4, 3) < 0 Then
        Sheet4.Range("H6") = "差"
        Sheet4.Range("H6").Interior.ColorIndex = 35
    Else
        Sheet4.Range("H6") = "平"
        Sheet4.Range("H6").Interior.Color = RGB(255, 255, 255)
    End If
    
    
    ' 这里无论是算出好还是差，如果最近一天的上涨列数据是大于4000家，就强制改成差
    Set rng = Sheet21.Range("G:G").Find("上涨数量")
    If Not rng Is Nothing Then
        If rng.Offset(1, 0) > 4000 Then
            Sheet4.Range("H6") = "差"
            Sheet4.Range("H6").Interior.ColorIndex = 34
        End If
    End If
    
   
        
   
End Sub

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



Sub 连涨记录()
    On Error Resume Next
    Range("图表[日期]").Replace Date, "", 1
    Range("图表[日期]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    日期 = Date
    涨停 = Sheet5.Range("a1").End(xlDown).Row - 1
    连板 = Evaluate("COUNTIF(连涨股票!D2:D" & 涨停 + 1 & ","">1"")")
    主板最高 = Evaluate("MAX(表2[连涨天数])")
    主板次高 = Evaluate("LARGE(表2[连涨天数],2)")
    创业最高 = Evaluate("MAX(表1[连涨天数])")
    主板名称 = ""
    For i = 2 To 涨停 + 1
        If Left(Sheet5.Range("a" & i), 5) <> "SZ.30" And Sheet5.Range("d" & i) = 主板最高 Then
            If 主板名称 = "" Then
                主板名称 = Sheet5.Range("b" & i) & vbLf & Sheet5.Range("f" & i)
            Else
                主板名称 = 主板名称 & vbLf & Sheet5.Range("b" & i) & vbLf & Sheet5.Range("f" & i)
            End If
        End If
    Next
    Range("图表").ListObject.ListRows.Add.Range = Array(日期, 连板, 涨停, "", 主板最高, 主板次高, 创业最高, 主板名称)
    Dim Wb As Workbook
    'Application.DisplayAlerts = False
    Set Wb = Workbooks.Open(ThisWorkbook.Path & "\复盘记录.xlsx")
    'Wb.Range("图表").ListObject.ListRows.Add.Range = Array(日期, 连板, 涨停, "", 主板最高, 主板次高, 创业最高, 主板名称)
    Wb.Sheets("Sheet2").Range("图表[日期]").Replace Date, "", 1
    Wb.Sheets("Sheet2").Range("图表[日期]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    Wb.Sheets("Sheet2").Range("图表").ListObject.ListRows.Add.Range = Array(日期, 连板, 涨停, "", 主板最高, 主板次高, 创业最高, 主板名称)
    行数 = Wb.Sheets("sheet1").UsedRange.Rows.Count
    Sheet7.UsedRange.Rows.Copy Wb.Sheets("sheet1").Range("a" & 行数 + 1)
    Wb.Close True
    MsgBox "已导出"
End Sub

Sub sss()
    Sheet5.Range("a:g").Sort "涨停大肉数", 2, , , , , , 1
End Sub
