Attribute VB_Name = "采集版模块"


Sub tonum()

    Dim c As Integer
    Dim r As Integer
    Dim arr
    
    For i = 1 To 14
        r = Worksheets(i).Range("a1").End(xlDown).Row
        c = Worksheets(i).Range("a1").End(xlToRight).Column
        arr = Worksheets(i).Cells(2, 1).Resize(r - 1, c)
        Worksheets(i).Cells(2, 1).Resize(r - 1, c) = arr
    Next
    
    'MsgBox "已转为数字"

End Sub

Sub 重新生成超级表()
    Debug.Print Now & "重新生成超级表"
    On Error Resume Next
    Sheet1.ListObjects("表").Unlist
    Sheet1.Cells.ClearFormats
    Sheet1.ListObjects.Add(xlSrcRange, Sheet1.Range("a1").CurrentRegion, , xlYes).Name = "表"
    Sheet2.ListObjects("表1").Unlist
    Sheet2.Cells.ClearFormats
    Sheet2.ListObjects.Add(xlSrcRange, Sheet2.Range("a1").CurrentRegion, , xlYes).Name = "表1"
    Sheet16.ListObjects("qs").Unlist
    Sheet16.Cells.ClearFormats
    Sheet16.ListObjects.Add(xlSrcRange, Sheet16.Range("a1").CurrentRegion, , xlYes).Name = "qs"
End Sub
Sub cc()
   ' Range("表1[趋势]") = ""
     Debug.Print Sheet27.UsedRange.Rows.Count
End Sub

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
            If rng.Offset(0, 1) >= 0.05 Then rng.Offset(0, 14) = "涨停大肉"
            If rng.Offset(0, 1) < -0.095 Then rng.Offset(0, 14) = "跌停大面"
        Else '否则（封单开）
            If rng.Offset(0, 2) > 0.095 Then rng.Offset(0, 14) = "涨停大肉"
            If rng.Offset(0, 2) < -0.095 Then rng.Offset(0, 14) = "跌停大面"
            If rng.Offset(0, 4) <> 0 Then '防止收盘价为0，被除数不能为0
                'If (rng.Offset(0, 4) - rng.Offset(0, 5)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = "涨停大肉" '(收盘价-最低价)/收盘价 > 0.095
                If rng.Offset(0, 14) = "" And (rng.Offset(0, 3) - rng.Offset(0, 4)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = "跌停大面" '最高价-收盘价)/收盘价 > 0.095
            End If
        End If

'        If rng.Offset(0, 2) >= zf Then rng.Offset(0, 14) = "涨停大肉"
'        If rng.Offset(0, 14) = "" And rng.Offset(0, 6) <> 0 Then '昨日收盘价<>0
'            If (rng.Offset(0, 4) - rng.Offset(0, 5)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = "涨停大肉"
'            'If (rng.Offset(0, 4) - rng.Offset(0, 6)) / rng.Offset(0, 6) > 0.095 Then rng.Offset(0, 14) = "涨停大肉" '(收盘价-昨日收盘价)/昨日收盘价
'        End If
'
'        If rng.Offset(0, 14) = "" And rng.Offset(0, 4) <> 0 Then
'            If (rng.Offset(0, 3) - rng.Offset(0, 4)) / rng.Offset(0, 4) > 0.095 Then
'                rng.Offset(0, 14) = "跌停大面"
'            Else
'
'                If rng.Offset(0, 14) = "" And rng.Offset(0, 2) < -0.095 Then rng.Offset(0, 14) = "跌停大面"
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
                Sheet19.Range("h" & i) = rng.Offset(0, 15) + 1
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
Sub 生成所属概念()
    Debug.Print Now & "生成所属概念"
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng, gp As Range
    Dim dic As Object
    Dim gnstr As String
    Dim arr
    Dim i As Integer
    Dim js_cy, js_zb, a, cyset, zbset, lz, jj
    a = 0
    
    '取出有效概念合并成一个长字符串
 '   cyset = Range("设置值[设置值]").Rows(1)
 '   zbset = Range("设置值[设置值]").Rows(2)
 '   For Each rng In Sheet1.Range("表[所属概念]")
 '       If Left(rng.Offset(0, -4), 5) = "SZ.30" Or Left(rng.Offset(0, -4), 6) = "SH.688" Or Left(rng.Offset(0, -4), 6) = "SH.689" Then '创业
'            If rng.Offset(0, 5) > cyset Then gnstr = gnstr & rng
'        Else '主板
'            If rng.Offset(0, 5) > zbset Then gnstr = gnstr & rng
'        End If
'    Next

    '现在封单关所属概念从一字板表取
    ' 封单开所属概念从主创涨停表取
    If Sheet4.Range("h3") = "封单开" Then
        For Each rng In Sheet15.Range("A2:A3000")
            If rng = "" Then Exit For
            
            Set gp = Sheet2.Range("A:A").Find(rng, , , 1)
            If Not gp Is Nothing Then
              gnstr = gnstr & gp.Offset(0, 4)
            End If
            
        Next
    Else
        For Each rng In Sheet19.Range("A2:A3000")
            If rng = "" Then Exit For
            If rng.Offset(0, 4) > 0 Then
                Set gp = Sheet2.Range("A:A").Find(rng, , , 1)
                If Not gp Is Nothing Then
                 gnstr = gnstr & gp.Offset(0, 4)
                End If
            End If
        Next
    End If



    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            'If InStr(nogn, ";" & arr(i) & ";") < 1 Then '去掉不要的概念
                'If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
'                        js_cy = Evaluate("COUNTIFS(表[ [  代码] ],""SZ.30*"",表[所属概念],""*;" & arr(i) & ";*"")")
'                        js_zb = Evaluate("SUMPRODUCT(IF(ISERROR(FIND(""SZ.30"",表[  代码])),1,0),IF(ISERROR(FIND("";" & arr(i) & ";"",表[所属概念])),0,1))")
'                        dic(arr(i)) = Array(js_cy, js_zb)
                        dic(arr(i)) = 1 'Evaluate("COUNTIFS(表[所属概念],""*;" & arr(i) & ";*"")")
                    End If
                'End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    If Range("创业板概念[#data]").Rows.Count > 1 Then Range("创业板概念[#data]").Delete Shift:=xlShiftUp '清空原表
    Sheet4.Range("a2:g10000").Clear
    Range("创业板概念[实际流通]").NumberFormatLocal = "0.00"
    Range("创业板概念[[#Headers],[所属概念]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    'Range("创业板概念[[#Headers],[计数]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)

    Set dic = Nothing '关闭字典
    
    Range("创业板概念[所属概念]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("创业板概念[计数]").Replace "1", "", 1 '1是完全匹配
    'Range("创业板概念[计数]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp

    '今百日新高输出到概念表
    Set rng = Sheet7.Range("a:a").Find("创百日新高")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                
                ' 查涨停原因的创百日新高，合并概念的金额
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 1) = lz & " | " & rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 1) = lz & " | 0"
                    'a.Offset(0, 1).Interior.ColorIndex = 35 '中音数为0的绿
                End If
                'If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35

        Next
    End If
       '昨百日新高输出到概念表
    Set rng = Sheet21.Range("a:a").Find("创百日新高")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 1) = a.Offset(0, 1) & " | " & rng.Offset(0, 1)
                    'If a.Offset(0, 5) > a.Offset(0, 4) Then a.Offset(0, 5).Interior.ColorIndex = 35
                Else
                    a.Offset(0, 1) = a.Offset(0, 1) & " | 0"
                End If
                arr = Split(a.Offset(0, 1), " | ")
                If arr(1) * 1 = 0 Or arr(1) * 1 < arr(2) * 1 Then a.Offset(0, 1).Interior.ColorIndex = 35
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        Next
    End If
    
    '今竞封输出到概念表
    Set rng = Sheet7.Range("a:a").Find("今竞封")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    Sheet4.Range("d1") = "今竞封数"
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
                a.Offset(0, 3) = 0
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 3) = lz
                    a.Offset(0, 4) = rng.Offset(0, 1)
                Else
                    a.Offset(0, 4) = 0
                End If
                
                If a.Offset(0, 4) <= 0 And a.Offset(0, 3) > 0 Then a.Offset(0, 4).Interior.ColorIndex = 35    '小于等于0的变绿
                
                'If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35

        Next
    End If
    '排序
    Range("创业板概念").Sort "今竞封数", 2, , , , , , 1
    
    '如果封单开，D列改为涨停大肉原因
    If Sheet4.Range("h3") = "封单开" Then
        Sheet4.Range("d1") = "涨停大肉数"
        For Each a In Range("创业板概念[所属概念]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(3).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - 4
                End If
                a.Offset(0, 3) = lz
                If lz < 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
            End If
        Next
    
        '排序
        Range("创业板概念").Sort "涨停大肉数", 2, , , , , , 1
    End If
    '昨竞封输出到概念表
    Set rng = Sheet21.Range("a:a").Find("今竞封")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    If a.Offset(0, 3) > 0 And rng.Offset(0, 1) > a.Offset(0, 4) Then a.Offset(0, 4).Interior.ColorIndex = 35 '昨比今大变绿
                    a.Offset(0, 4) = a.Offset(0, 4) & " | " & rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 4) = a.Offset(0, 4) & " | 0"
                End If
                
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        Next
    End If
    
    '新加
    Set rng = Sheet21.Range("a:a").Find("涨停大肉")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
                
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    arr = Split(a.Offset(0, 4), " | ")
                    lz = Round(rng.Offset(0, 1) / 100000000, 2)
                    If a.Offset(0, 3) > 0 And lz > arr(0) * 1 Then a.Offset(0, 4).Interior.ColorIndex = 35  '昨比今大变绿
                    a.Offset(0, 4) = a.Offset(0, 4) & " | " & lz
                    
                Else
                    a.Offset(0, 4) = a.Offset(0, 4) & " | 0"
                End If
                
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        Next
    End If
    
   '   For Each a In Range("创业板概念[所属概念]")
    '
     '       If a.Offset(0, 1) = "0 | 0 | 0" Then
      '          a.Offset(0, 1).Interior.ColorIndex = xlNone
       '     End If
        '
       '     If a.Offset(0, 4) = "0 | 0 | 0" Then
        '        a.Offset(0, 4).Interior.ColorIndex = xlNone
       '     End If
   '
    '    Next
    
        '计算盘中封单总和
    If Sheet4.Range("h3") = "封单开" Then
        If Sheet5.Range("a2") <> "" Then
            h = Sheet5.Range("a1").End(xlDown).Row
            Debug.Print "行数=" & h
            For Each a In Range("创业板概念[所属概念]")
                'If a.Offset(0, 3) = 0 Then Exit For
                'If a.Offset(0, 3) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 Then
                    a.Offset(0, 5) = Evaluate("round(SUMIFS(连涨股票!E2:E" & h & ",连涨股票!F2:F" & h & ",""*;" & a & ";*"")/100000000,2)")
                    If a.Offset(0, 5) < (Left(a.Offset(0, 4), InStr(a.Offset(0, 4), " ") - 1)) * 1 Then a.Offset(0, 5).Interior.ColorIndex = 35
                    If a.Offset(0, 5) > 0 And a.Offset(0, 5) > (Left(a.Offset(0, 4), InStr(a.Offset(0, 4), " ") - 1)) * 1 Then a.Offset(0, 4).Interior.Pattern = xlNone
                'End If
            Next
        End If
    End If
        '计算跌停封单总和
    
    If Sheet5.Range("a2") <> "" Then
        h = Sheet5.Range("i1").End(xlDown).Row
        Debug.Print "行数=" & h
        
        If Sheet4.Range("h3") = "封单开" Then
             Sheet4.Range("g1") = "跌停封单额"
            For Each a In Range("创业板概念[所属概念]")
               
                a.Offset(0, 6) = Evaluate("round(SUMIFS(连涨股票!M2:M" & h & ",连涨股票!N2:N" & h & ",""*;" & a & ";*"")/100000000,2)")
                If a.Offset(0, 6) > a.Offset(0, 5) Then a.Offset(0, 6).Interior.ColorIndex = 35
            Next
        Else
            Sheet4.Range("g1") = "跌停未匹配"
            For Each a In Range("创业板概念[所属概念]")
                
                jj = Evaluate("SUMIFS(连涨股票!L2:L" & h & ",连涨股票!N2:N" & h & ",""*;" & a & ";*"")")
                If jj > 0 Then jj = 0
                If jj < 0 Then jj = Abs(jj)
                a.Offset(0, 6) = jj
                arr = Split(a.Offset(0, 4), " | ")
                 '跌停未匹配 > 今竞封 则绿
                If a.Offset(0, 6) > arr(0) * 1 Then a.Offset(0, 6).Interior.ColorIndex = 35
                
                ' 跌停未匹配 是绿色， 且今竞封数是 0， 跌停未匹配 还原成 无色
                If a.Offset(0, 6).Interior.ColorIndex = 35 And a.Offset(0, 3) = 0 Then a.Offset(0, 6).Interior.Pattern = xlNone
                ' a.Offset(0, 6).Interior.ColorIndex = 35
            Next
        End If
        
    End If
    
    
 '   '计算创业板实际流通
 '   For Each a In Range("创业板概念[所属概念]")
 '       If a.Offset(0, 1).Interior.ColorIndex <> 35 Or a.Offset(0, 4).Interior.ColorIndex <> 35 Then
 '          'a.Offset(0, 2) = Evaluate("round(AVERAGEIFS(表[竞价涨幅],表[所属概念],""*;" & a & ";*""),4)")
 '           a.Offset(0, 2) = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & a & ";*"")/100000000,2)")
 '           'If a.Offset(0, 2) < 9000 Then a.Offset(0, 3).Interior.ColorIndex = 35
 '       'Else
 '           'a.Offset(0, 2) = "-"
 '       End If
 '   Next
 
End Sub
Sub sssa()
    arr = Split([b3], " | ")
    MsgBox "值为:" & arr(1)
End Sub
Sub 生成所属概念旧()
    Debug.Print Now & "生成所属概念"
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim gnstr As String
    Dim arr
    Dim i As Integer
    Dim js_cy, js_zb, a, cyset, zbset, lz

    
    '取出有效概念合并成一个长字符串
    cyset = Range("设置值[设置值]").Rows(1)
    zbset = Range("设置值[设置值]").Rows(2)
    For Each rng In Sheet1.Range("表[所属概念]")
        If Left(rng.Offset(0, -4), 5) = "SZ.30" Or Left(rng.Offset(0, -4), 6) = "SH.688" Or Left(rng.Offset(0, -4), 6) = "SH.689" Then '创业
            If rng.Offset(0, 5) > cyset Then gnstr = gnstr & rng
        Else '主板
            If rng.Offset(0, 5) > zbset Then gnstr = gnstr & rng
        End If
    Next
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            'If InStr(nogn, ";" & arr(i) & ";") < 1 Then '去掉不要的概念
                'If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
'                        js_cy = Evaluate("COUNTIFS(表[ [  代码] ],""SZ.30*"",表[所属概念],""*;" & arr(i) & ";*"")")
'                        js_zb = Evaluate("SUMPRODUCT(IF(ISERROR(FIND(""SZ.30"",表[  代码])),1,0),IF(ISERROR(FIND("";" & arr(i) & ";"",表[所属概念])),0,1))")
'                        dic(arr(i)) = Array(js_cy, js_zb)
                        dic(arr(i)) = Evaluate("COUNTIFS(表[所属概念],""*;" & arr(i) & ";*"")")
                    End If
                'End If
            'End If
        Next
    End If
    

    '把字典输出到概念表
    If Range("创业板概念[#data]").Rows.Count > 1 Then Range("创业板概念[#data]").Delete Shift:=xlShiftUp '清空原表
    Range("创业板概念[实际流通]").NumberFormatLocal = "0.00"
    Range("创业板概念[[#Headers],[所属概念]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    Range("创业板概念[[#Headers],[计数]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)

    Set dic = Nothing '关闭字典
    
    Range("创业板概念[所属概念]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("创业板概念[计数]").Replace "1", "", 1 '1是完全匹配
    Range("创业板概念[计数]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    
    
    'Range("表1").Sort "连涨天数", 2, , , , , , 1

    
    '计算连涨天数=ma
'    For Each a In Range("创业板概念[所属概念]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
'            Set rng = Sheet2.Range("E:E").Find(";" & a & ";")
'            If Not rng Is Nothing Then lz = rng.Offset(0, 3)
'            Set rng = Sheet3.Range("E:E").Find(";" & a & ";")
'            If Not rng Is Nothing Then
'                If rng.Offset(0, 3) > lz Then lz = rng.Offset(0, 3)
'            End If
'            a.Offset(0, 3) = lz
'            If lz = 0 Then a.Offset(0, 3).Interior.ColorIndex = 35
'        End If
'    Next
    Debug.Print Now & "生成所属概念--计算涨停跌停"
    '涨停大肉原因小于2的绿
    For Each a In Range("创业板概念[所属概念]")
        If a.Offset(0, 1) > 0 Then
            lz = 0
            'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
            Set rng = Sheet7.Rows(3).Find(a, , , 1)
            If Not rng Is Nothing Then
                lz = rng.End(xlDown).Row - 4
            End If
            a.Offset(0, 3) = lz
            If lz < 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        End If
    Next
    '跌停大面原因大于1的绿
    Set rng = Sheet7.Range("a:a").Find("跌停大面")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                End If
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
            End If
        Next
    End If
    
    
    '今竞封输出到概念表
    Set rng = Sheet7.Range("a:a").Find("涨停大肉")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 4) = rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 4) = 0
                End If
                If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35

            End If
        Next
    End If
    
    '昨竞封输出到概念表
    Set rng = Sheet21.Range("a:a").Find("涨停大肉")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 5) = rng.Offset(0, 1)
                    If a.Offset(0, 5) > a.Offset(0, 4) Then a.Offset(0, 5).Interior.ColorIndex = 35
                End If
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
            End If
        Next
    End If
    
'    '涨停大肉小于2的绿
'    For Each a In Range("创业板概念[所属概念]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
'            Set rng = Sheet6.Range("a:a").Find(a)
'            If Not rng Is Nothing Then
'                lz = rng.Offset(0, 1)
'            End If
'            a.Offset(0, 3) = lz
'            If lz < 2 Then a.Offset(0, 3).Interior.ColorIndex = 35
'        End If
'    Next
'
'    '跌停大面大于2的绿
'    For Each a In Range("创业板概念[所属概念]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            Set rng = Sheet6.Range("d:d").Find(a)
'            If Not rng Is Nothing Then
'                lz = rng.Offset(0, 1)
'            End If
'            a.Offset(0, 4) = lz
'            If lz >= 2 Then a.Offset(0, 4).Interior.ColorIndex = 35
'        End If
'    Next

    '排序
    Range("创业板概念").Sort "涨停大肉", 2, , , , , , 1
    
'    For Each a In Range("创业板概念[所属概念]")
'        'If a.Offset(0, 3) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 Then
'            a.Offset(0, 6) = Evaluate("round(SUMIFS(表1[涨停封单额],表1[所属概念],""*;" & a & ";*"")/100000000,4)")
'            If a.Offset(0, 5) <> "" And a.Offset(0, 6) > a.Offset(0, 5) Then a.Offset(0, 5).Interior.ColorIndex = 0
'            If a.Offset(0, 6) > a.Offset(0, 4) Then a.Offset(0, 4).Interior.ColorIndex = 0
'        'End If
'    Next
    '计算盘中封单总和
    If Sheet4.Range("h3") = "封单开" Then
        If Sheet5.Range("a2") <> "" Then
            h = Sheet5.Range("a1").End(xlDown).Row
            Debug.Print "行数=" & h
            For Each a In Range("创业板概念[所属概念]")
                If a.Offset(0, 3) = 0 Then Exit For
                'If a.Offset(0, 3) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 Then
                    a.Offset(0, 6) = Evaluate("round(SUMIFS(连涨股票!E2:E" & h & ",连涨股票!F2:F" & h & ",""*;" & a & ";*"")/100000000,2)")
                    If a.Offset(0, 5) <> "" And a.Offset(0, 6) > a.Offset(0, 5) Then a.Offset(0, 5).Interior.ColorIndex = 0
                    If a.Offset(0, 6) <= a.Offset(0, 4) Then
                        a.Offset(0, 4).Interior.ColorIndex = 35
                        a.Offset(0, 5).Interior.ColorIndex = 35
                    Else
                        a.Offset(0, 4).Interior.ColorIndex = 0
                        a.Offset(0, 5).Interior.ColorIndex = 0
                    End If
                'End If
            Next
        End If
    End If
    Debug.Print Now & "生成所属概念--计算实际流通"
    '计算创业板实际流通
    For Each a In Range("创业板概念[所属概念]")
        If a.Offset(0, 1) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 And a.Offset(0, 5).Interior.ColorIndex <> 35 Then
            'a.Offset(0, 2) = Evaluate("round(AVERAGEIFS(表[竞价涨幅],表[所属概念],""*;" & a & ";*""),4)")
            a.Offset(0, 2) = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & a & ";*"")/100000000,2)")
            'If a.Offset(0, 2) < 9000 Then a.Offset(0, 3).Interior.ColorIndex = 35
        'Else
            'a.Offset(0, 2) = "-"
        End If
    Next
End Sub

Sub tjtest()
    a = "房地产"
    Debug.Print Evaluate("round(SUMIFS(连涨股票!E2:E214,连涨股票!F2:F214,""*;" & a & ";*"")/100000000,4)")
End Sub

Sub 新合并概念()
    Dim i, j, dm
    Dim arr
    Dim rng As Range
    Dim Wb As Workbook
    If Sheet4.Range("H100") = Evaluate("round(sum(表1[最高价]),2)") Then
        If MsgBox("检测到已经合并过概念了，确定要重复合并吗？", 1) <> vbOK Then Exit Sub
    Else
        If MsgBox("检测到数据更新后，没有合并概念。你确认要合并吗?", 1) <> vbOK Then Exit Sub
    End If
    
    Application.ScreenUpdating = False
    重新生成超级表
    '概念去中括号
'    Range("表[所属概念]").Replace "【", ";", 2
'    Range("表1[所属概念]").Replace "【", ";", 2
'    Range("表2[所属概念]").Replace "【", ";", 2
'    Range("表[所属概念]").Replace "】", ";", 2
'    Range("表1[所属概念]").Replace "】", ";", 2
'    Range("表2[所属概念]").Replace "】", ";", 2
'    Sheet2.Range("k1") = "主力净额"
'    Sheet3.Range("k1") = "主力净额"
    'Open ThisWorkbook.Path & "\概念.txt" For Input As #1
    Set Wb = GetObject(ThisWorkbook.Path & "\data.xlsx")
    i = 2
    With Wb.Sheets("table3")
        'Do While Not EOF(1)
        Do While .Range("a" & i) <> ""
            'Line Input #1, j
            j = .Range("c" & i)
            'arr = Split(j, "|")
            
            Set rng = Range("表[  代码]").Find(.Range("a" & i), LookAt:=xlPart)  '模糊查找，单元格匹配模式
            If Not rng Is Nothing Then
                dm = Replace(.Range("c" & i), ",", ";") & ";" & rng.Offset(0, 2)
                'dm = ";" & dm & "】"
                'dm = Left(rng.Offset(0, 4).Value, Len(rng.Offset(0, 4).Value) - 1) & ";" & dm
                rng.Offset(0, 4).Value = rng.Offset(0, 4).Value & ";" & dm & ";"
                'rng.Offset(0, 4).Value = ";" & dm & ";"
            End If
            
            Set rng = Range("表1[  代码]").Find(.Range("a" & i), LookAt:=xlPart) '模糊查找，单元格匹配模式
            'If rng Is Nothing Then Set rng = Range("表2[  代码]").Find(.Range("a" & i), LookAt:=xlPart)
            If Not rng Is Nothing Then
                dm = Replace(.Range("c" & i), ",", ";") & ";" & rng.Offset(0, 2)
                'dm = ";" & dm & "】"
                'dm = Left(rng.Offset(0, 4).Value, Len(rng.Offset(0, 4).Value) - 1) & ";" & dm
                rng.Offset(0, 4).Value = rng.Offset(0, 4).Value & ";" & dm & ";"
                'rng.Offset(0, 4).Value = ";" & dm & ";"
                'rng.Offset(0, 10).Value = .Range("d" & i)
                'rng.Offset(0, 11).Value = .Range("e" & i)
                
            End If
            i = i + 1
        Loop
    End With
    'Close #1
    Wb.Close False
    Set Wb = Nothing
    
    For Each rng In Sheet1.Range("表[所属概念]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
    Next
    For Each rng In Sheet2.Range("表1[所属概念]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
    Next
    
    '概念去重复分号
    Range("表[所属概念]").Replace ";;", ";", 2
    Range("表1[所属概念]").Replace ";;", ";", 2

    '概念去空格
    Range("表[所属概念]").Replace " ", "", 2
    Range("表1[所属概念]").Replace " ", "", 2
    'Range("表2[所属概念]").Replace " ", "", 2
    '概念去空格结束
    '电力设备变电力
    Range("表[所属概念]").Replace ";电力设备;", ";电力;", 2
    Range("表1[所属概念]").Replace ";电力设备;", ";电力;", 2
     Range("表[所属概念]").Replace ";电力物联网;", ";电力;", 2
    Range("表1[所属概念]").Replace ";电力物联网;", ";电力;", 2
    'Range("表2[所属概念]").Replace ";电力设备;", ";电力;", 2
    
    Range("表[所属概念]").Replace ";新零售;", ";零售;", 2
    Range("表1[所属概念]").Replace ";新零售;", ";零售;", 2

    Range("表[所属概念]").Replace ";风电;", ";电力;", 2
    Range("表1[所属概念]").Replace ";风电;", ";电力;", 2
    'Range("表2[所属概念]").Replace ";风电;", ";电力;", 2

    Range("表[所属概念]").Replace ";央企国资改革;", ";国企改革;", 2
    Range("表1[所属概念]").Replace ";央企国资改革;", ";国企改革;", 2
    Range("表[所属概念]").Replace ";地方国资改革;", ";国企改革;", 2
    Range("表1[所属概念]").Replace ";地方国资改革;", ";国企改革;", 2
    'Range("表2[所属概念]").Replace ";央企国企改革;", ";国企改革;", 2

    Range("表[所属概念]").Replace ";开板次新;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";开板次新;", ";新股与次新股;", 2
    Range("表[所属概念]").Replace ";次新股;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";次新股;", ";新股与次新股;", 2
    Range("表[所属概念]").Replace ";核准制次新股;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";核准制次新股;", ";新股与次新股;", 2
    Range("表[所属概念]").Replace ";注册制次新股;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";注册制次新股;", ";新股与次新股;", 2
    
'    Range("表[所属概念]").Replace What:=";??国资改革;", Replacement:=";", LookAt:=xlPart, _
'        MatchCase:=False, SearchFormat:=False, ReplaceFormat:=False
'    Range("表1[所属概念]").Replace What:=";??国资改革;", Replacement:=";", LookAt:=xlPart, _
'        MatchCase:=False, SearchFormat:=False, ReplaceFormat:=False
    
    Sheet4.Range("H100") = Evaluate("round(sum(表1[最高价]),2)")
    Application.ScreenUpdating = True
    re
    MsgBox "概念合并完成!"
End Sub
Sub test()
   ' Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("an1:ap2"), Sheet4.Range("j1:s1")
   ' Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("as1:au2"), Sheet4.Range("x1:ag1")
    Debug.Print Sheet26.Cells(1, 2)
    Range("表1").Sort "4日涨跌幅", 2, , , , , , 1
    Range("表1").Sort "连板天数", 2, , , , , , 1
    Dim CurrentDate As Date
    CurrentDate = Date
    Dim cybgd As String '创业板高度
    Dim lastRow As Long
    With Sheet15
        lastRow = .Cells(.Rows.Count, 1).End(xlUp).Row - 1
    End With

    
    For i = 2 To 200 Step 1
        If InStr(Sheet2.Range("a" & i), ".300") > 0 Or InStr(Sheet2.Range("a" & i), ".301") > 0 Then
            cybgd = Sheet2.Range("z" & i)
            Exit For
        End If
        
    Next
    
    For i = 2 To 200 Step 1
        If Sheet27.Cells(i, 1) = "" Then
            
            Sheet27.Cells(i, 1) = CurrentDate
            Sheet27.Cells(i, 1).Offset(0, 1) = lastRow
            
            Sheet27.Cells(i, 1).Offset(0, 2) = Evaluate("COUNTIFS(表1[ [跌停封单额] ],"">0"")")
            Sheet27.Cells(i, 1).Offset(0, 3) = Evaluate("COUNTIFS(表1[ [连板天数] ],""1"")")
            Sheet27.Cells(i, 1).Offset(0, 4) = Evaluate("COUNTIFS(表1[ [连板天数] ],"">1"")")
            Sheet27.Cells(i, 1).Offset(0, 5) = Sheet2.Range("z2") ' 总高度
        Sheet27.Cells(i, 1).Offset(0, 6) = Sheet4.Range("H25") ' 龙头
        
        
'            If Not rng Is Nothing Then lz = rng.Offset(0, 3)
        Set rng = Sheet5.Range("B:B").Find(Sheet27.Cells(i, 1).Offset(0, 6))  ' 龙头 涨停原因
        If Not rng Is Nothing Then
            Sheet27.Cells(i, 1).Offset(0, 7) = rng.Offset(0, 4) ' 龙头
            Debug.Print "SUMIFS(连涨大肉股[涨停封单额],连涨大肉股[涨停大肉原因],""*" & rng.Offset(0, 4) & "*"")"
            
            Sheet27.Cells(i, 1).Offset(0, 8) = Evaluate("SUMIFS(连涨大肉股[涨停封单额],连涨大肉股[涨停大肉原因],""*" & rng.Offset(0, 4) & "*"")")  ' 龙头
            Sheet27.Cells(i, 1).Offset(0, 9) = Evaluate("SUMIFS(首板股[涨停封单额],首板股[首板原因],""*" & rng.Offset(0, 4) & "*"")")  ' 龙头
        End If
    
        
            
            Sheet27.Cells(i, 1).Offset(0, 10) = cybgd '创业板高度
            
            
            Sheet27.Cells(i, 1).Offset(0, 11) = Sheet25.Range("e2")
            Sheet27.Cells(i, 1).Offset(0, 12) = Sheet25.Range("e3")
            Sheet27.Cells(i, 1).Offset(0, 13) = Sheet25.Range("d2")
            Sheet27.Cells(i, 1).Offset(0, 14) = Sheet25.Range("d3")
            
            'Sheet27.Cells(i, 1).Offset(0, 12) = Sheet2.Range("b2")
            Sheet27.Cells(i, 1).Offset(0, 15) = Sheet4.Range("H6")
            Sheet27.Cells(i, 1).Offset(0, 15).Interior.ColorIndex = Sheet4.Range("H6").Interior.ColorIndex
            
            Sheet27.Cells(i, 1).Offset(0, 16) = Evaluate("COUNTIFS(表1[ [涨跌幅] ],"">0"")")
            Sheet27.Cells(i, 1).Offset(0, 17) = Sheet27.Cells(i, 1).Offset(0, 16) / lastRow
            Range("表1").Sort "120日涨跌幅", 2, , , , , , 1
            For j = 1 To 1000 Step 1
                If Sheet2.Cells(1 + j, 15) / 10000 / 10000 > 100 Then
                    Sheet27.Cells(i, 1).Offset(0, 18) = Sheet2.Cells(1 + j, 2)
                    Exit For
                End If
            Next
            Exit For
        End If
    Next
    
End Sub
Sub re()
        '概念去重复分号
    Range("表[所属概念]").Replace ";;", ";", 2
    Range("表1[所属概念]").Replace ";;", ";", 2
    
    '概念去空格
    Range("表[所属概念]").Replace " ", "", 2
    Range("表1[所属概念]").Replace " ", "", 2
    'Range("表2[所属概念]").Replace " ", "", 2
    '概念去空格结束
    '电力设备变电力
    Range("表[所属概念]").Replace ";电力设备;", ";电力;", 2
    Range("表1[所属概念]").Replace ";电力设备;", ";电力;", 2
    Range("表[所属概念]").Replace ";电力物联网;", ";电力;", 2
    Range("表1[所属概念]").Replace ";电力物联网;", ";电力;", 2
    'Range("表2[所属概念]").Replace ";电力设备;", ";电力;", 2
    
    Range("表[所属概念]").Replace ";风电;", ";电力;", 2
    Range("表1[所属概念]").Replace ";风电;", ";电力;", 2
    'Range("表2[所属概念]").Replace ";风电;", ";电力;", 2
    
    'Range("表[所属概念]").Replace ";??国企改革;", ";", 2
    'Range("表1[所属概念]").Replace ";??国企改革;", ";", 2
    'Range("表2[所属概念]").Replace ";央企国企改革;", ";国企改革;", 2
    
    Range("表[所属概念]").Replace ";开板次新;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";开板次新;", ";新股与次新股;", 2
    Range("表[所属概念]").Replace ";次新股;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";次新股;", ";新股与次新股;", 2
    Range("表[所属概念]").Replace ";核准制次新股;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";核准制次新股;", ";新股与次新股;", 2
    Range("表[所属概念]").Replace ";注册制次新股;", ";新股与次新股;", 2
    Range("表1[所属概念]").Replace ";注册制次新股;", ";新股与次新股;", 2
End Sub

Sub 导出涨停原因()
    Dim Wb As Workbook
    myPath = Left(ThisWorkbook.Path, Len(ThisWorkbook.Path) - 6) & "\template.xlsm"
    Debug.Print myPath
    Range("表1").Sort "4日涨跌幅", 2, , , , , , 1
    Range("表1").Sort "连板天数", 2, , , , , , 1
    
    
    Set rng = Sheet21.Range("a:a").Find("首板")
    sb = 0 '首板行号
    If Not rng Is Nothing Then sb = rng.Row
     For j = 1 To 256 Step 1
        If Sheet21.Cells(sb + j, 1) = "" Then Exit For

    Next
    
    行数 = Sheet7.UsedRange.Rows.Count + 2
    Debug.Print Sheet27.UsedRange.Rows.Count
    
    
    Dim lastRow As Long
    With Sheet15
        lastRow = .Cells(.Rows.Count, 1).End(xlUp).Row - 1
    End With

    Dim CurrentDate As Date
    CurrentDate = Date
    Dim cybgd As String '创业板高度
    
    For i = 2 To 200 Step 1
        If InStr(Sheet2.Range("a" & i), ".300") > 0 Or InStr(Sheet2.Range("a" & i), ".301") > 0 Then
            cybgd = Sheet2.Range("z" & i)
            Exit For
        End If
        
    Next
    
    i = Sheet27.UsedRange.Rows.Count + 1
   
    If Sheet27.Cells(i, 1) = "" Then
       
        Sheet27.Cells(i, 1) = CurrentDate
        Sheet27.Cells(i, 1).Offset(0, 1) = lastRow
        
        Sheet27.Cells(i, 1).Offset(0, 2) = Evaluate("COUNTIFS(表1[ [跌停封单额] ],"">0"")")
        Sheet27.Cells(i, 1).Offset(0, 3) = Evaluate("COUNTIFS(表1[ [连板天数] ],""1"")")
        Sheet27.Cells(i, 1).Offset(0, 4) = Evaluate("COUNTIFS(表1[ [连板天数] ],"">1"")")
        Sheet27.Cells(i, 1).Offset(0, 5) = Sheet2.Range("z2") ' 总高度
        Sheet27.Cells(i, 1).Offset(0, 6) = Sheet4.Range("H25") ' 龙头
        
        
'            If Not rng Is Nothing Then lz = rng.Offset(0, 3)
        Set rng = Sheet5.Range("B:B").Find(Sheet27.Cells(i, 1).Offset(0, 6))  ' 龙头 涨停原因
        If Not rng Is Nothing Then
            Sheet27.Cells(i, 1).Offset(0, 7) = rng.Offset(0, 4) ' 龙头
            Debug.Print "SUMIFS(连涨大肉股[涨停封单额],连涨大肉股[涨停大肉原因],""*" & rng.Offset(0, 4) & "*"")"
            
            Sheet27.Cells(i, 1).Offset(0, 8) = Evaluate("SUMIFS(连涨大肉股[涨停封单额],连涨大肉股[涨停大肉原因],""*" & rng.Offset(0, 4) & "*"")")  ' 龙头
            Sheet27.Cells(i, 1).Offset(0, 9) = Evaluate("SUMIFS(首板股[涨停封单额],首板股[首板原因],""*" & rng.Offset(0, 4) & "*"")")  ' 龙头
        End If
    
        
        Sheet27.Cells(i, 1).Offset(0, 10) = cybgd '创业板高度
        
        
        Sheet27.Cells(i, 1).Offset(0, 11) = Sheet25.Range("e2")
        Sheet27.Cells(i, 1).Offset(0, 12) = Sheet25.Range("e3")
        Sheet27.Cells(i, 1).Offset(0, 13) = Sheet25.Range("d2")
        Sheet27.Cells(i, 1).Offset(0, 14) = Sheet25.Range("d3")
        
        'Sheet27.Cells(i, 1).Offset(0, 12) = Sheet2.Range("b2")
        Sheet27.Cells(i, 1).Offset(0, 15) = Sheet4.Range("H6")
        Sheet27.Cells(i, 1).Offset(0, 15).Interior.ColorIndex = Sheet4.Range("H6").Interior.ColorIndex
        
        Sheet27.Cells(i, 1).Offset(0, 16) = Evaluate("COUNTIFS(表1[ [涨跌幅] ],"">0"")")
        Sheet27.Cells(i, 1).Offset(0, 17) = Sheet27.Cells(i, 1).Offset(0, 16) / lastRow
        
        Range("表1").Sort "120日涨跌幅", 2, , , , , , 1
        For j2 = 1 To 1000 Step 1
             If Sheet2.Cells(1 + j2, 15) / 10000 / 10000 > 50 Then
                 Sheet27.Cells(i, 1).Offset(0, 18) = Sheet2.Cells(1 + j2, 2)
                 Exit For
             End If
         Next
    End If
    
    
    
    
    
    Set Wb = Workbooks.Open(myPath)
    Sheet7.Cells.Copy
    'Wb.Sheet21.Range("a1").PasteSpecial
    Wb.Sheets("昨原因").Range("a1").PasteSpecial
    

    Sheet21.Rows(sb & ":" & (sb + j)).Copy

        
    Wb.Sheets("昨原因").Range("a" & 行数).PasteSpecial
    
    Wb.Sheets("昨原因").Range("a" & 行数) = "昨首板"
    
    
    ' 主线 按颜色排序
 '   Range("表1").Sort "4日涨跌幅", 2, , , , , , 1
    
    
    
    行数 = Sheet27.UsedRange.Rows.Count + 1
    
    Sheet27.Rows("1:" & (行数)).Copy
    Wb.Sheets("主线折线图").Range("a1").PasteSpecial
    

    
    Wb.Save
    Wb.Close
    Set Wb = Nothing
End Sub
Sub 删除空行()
    'On Error Resume Next
    Range("表[  代码]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    Range("表1[  代码]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("表2[  代码]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
End Sub


Sub 画折线图()
    Dim ChartSheet As Chart
    Dim RangeToChart As Range
    Debug.Print "A2:B" & Sheet26.UsedRange.Rows.Count
    
    ' 定义要绘图的数据范围
    Set RangeToChart = Sheet26.Range("A1:C3")

    ' 创建图表
    Set ChartSheet = Charts.Add
    ChartSheet.SetSourceData Source:=RangeToChart
    ChartSheet.ChartType = xlLine

    ' 可选：格式化图表（标题、轴名称等）
    With ChartSheet
        .HasTitle = True
        .ChartTitle.Text = "时间销售额"
        .Axes(xlCategory, xlPrimary).HasTitle = True
        .Axes(xlCategory, xlPrimary).AxisTitle.Text = "日期"
        .Axes(xlValue, xlPrimary).HasTitle = True
        .Axes(xlValue, xlPrimary).AxisTitle.Text = "数量"
    End With
End Sub


