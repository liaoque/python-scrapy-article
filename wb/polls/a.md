Sub 生成所属概念()
    Debug.Print Now & "生成所属概念"
    On Error Resume Next

    Dim rng As Range
    Dim dic As Object
    Dim gnstr As String
    Dim arr
    Dim i As Integer
    Dim js_cy, js_zb, a, cyset, zbset, lz, jj

    
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

    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                    If Not dic.exists(arr(i)) Then
                        dic(arr(i)) = 1 'Evaluate("COUNTIFS(表[所属概念],""*;" & arr(i) & ";*"")")
                    End If
        Next
    End If
    

    '把字典输出到概念表
    If Range("创业板概念[#data]").Rows.Count > 1 Then Range("创业板概念[#data]").Delete Shift:=xlShiftUp '清空原表
    Sheet4.Range("a2:g10000").Clear
    Range("创业板概念[实际流通]").NumberFormatLocal = "0.00"
    Range("创业板概念[[#Headers],[所属概念]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)

    Set dic = Nothing '关闭字典
    
    Range("创业板概念[所属概念]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp

    '今百日新高输出到概念表
    Set rng = Sheet7.Range("a:a").Find("创百日新高")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("创业板概念[所属概念]")
                lz = 0
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 1) = lz & " | " & rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 1) = lz & " | 0"
                End If

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
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    a.Offset(0, 1) = a.Offset(0, 1) & " | " & rng.Offset(0, 1)
                Else
                    a.Offset(0, 1) = a.Offset(0, 1) & " | 0"
                End If
                arr = Split(a.Offset(0, 1), " | ")
                If arr(1) * 1 = 0 Or arr(1) * 1 < arr(2) * 1 Then a.Offset(0, 1).Interior.ColorIndex = 35
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
                lz = 0
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 3) = lz
                    a.Offset(0, 4) = rng.Offset(0, 1)
                Else
                    a.Offset(0, 4) = 0
                End If
                If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35  '小于等于0的变绿

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
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    If rng.Offset(0, 1) > a.Offset(0, 4) Then a.Offset(0, 4).Interior.ColorIndex = 35 '昨比今大变绿
                    a.Offset(0, 4) = a.Offset(0, 4) & " | " & rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 4) = a.Offset(0, 4) & " | 0"
                End If
                
        Next
    End If
        '计算盘中封单总和
    If Sheet4.Range("h3") = "封单开" Then
        If Sheet5.Range("a2") <> "" Then
            h = Sheet5.Range("a1").End(xlDown).Row
            Debug.Print "行数=" & h
            For Each a In Range("创业板概念[所属概念]")
                    a.Offset(0, 5) = Evaluate("round(SUMIFS(连涨股票!E2:E" & h & ",连涨股票!F2:F" & h & ",""*;" & a & ";*"")/100000000,2)")
                    If a.Offset(0, 5) < (Left(a.Offset(0, 4), InStr(a.Offset(0, 4), " ") - 1)) * 1 Then a.Offset(0, 5).Interior.ColorIndex = 35
                    If a.Offset(0, 5) > 0 And a.Offset(0, 5) > (Left(a.Offset(0, 4), InStr(a.Offset(0, 4), " ") - 1)) * 1 Then a.Offset(0, 4).Interior.Pattern = xlNone
            Next
        End If
    End If
        '计算跌停封单总和

    If Sheet5.Range("a2") <> "" Then
        h = Sheet5.Range("i1").End(xlDown).Row
        Debug.Print "行数=" & h
        
        If Sheet4.Range("h3") = "封单开" Then
            For Each a In Range("创业板概念[所属概念]")
                Sheet4.Range("g1") = "跌停封单额"
                a.Offset(0, 6) = Evaluate("round(SUMIFS(连涨股票!M2:M" & h & ",连涨股票!N2:N" & h & ",""*;" & a & ";*"")/100000000,2)")
                If a.Offset(0, 6) > a.Offset(0, 5) Then a.Offset(0, 6).Interior.ColorIndex = 35
            Next
        Else
            For Each a In Range("创业板概念[所属概念]")
                Sheet4.Range("g1") = "跌停未匹配"
                jj = Evaluate("SUMIFS(连涨股票!L2:L" & h & ",连涨股票!N2:N" & h & ",""*;" & a & ";*"")")
                If jj > 0 Then jj = 0
                If jj < 0 Then jj = Abs(jj)
                a.Offset(0, 6) = jj
                arr = Split(a.Offset(0, 4), " | ")
                If a.Offset(0, 6) > arr(0) * 1 Then a.Offset(0, 6).Interior.ColorIndex = 35
            Next
        End If
        
    End If
    
    '计算创业板实际流通
    For Each a In Range("创业板概念[所属概念]")
        If a.Offset(0, 1).Interior.ColorIndex <> 35 Or a.Offset(0, 4).Interior.ColorIndex <> 35 Then
            a.Offset(0, 2) = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & a & ";*"")/100000000,2)")
        End If
    Next
End Sub



Sub 概念表上色()
    Debug.Print Now & "概念表上色"
    Dim rng1 As Range
    Dim rng2 As Range
    Dim rng3 As Range
    Dim rng As Range
    Dim imax As Integer
    Dim isred As Integer
    Dim firstAddress
    Dim arr
   '先去掉以前的颜色
    Range("创业板概念[实际流通]").Interior.Pattern = xlNone
    On Error GoTo line1
    Range("概念筛选[概念筛选]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
line1:
        For Each rng1 In Range("概念筛选[概念筛选]")
            If rng1 <> "" Then
                Set rng2 = Range("创业板概念[所属概念]").Find(rng1.Value, , , 1) '精确
                If Not rng2 Is Nothing Then
                    rng2.Offset(0, 2).Interior.ColorIndex = 36
                End If
            End If
        Next
    
    '取创业板概念最大计数里的最大实际流通
    '改为创业板概念最大计数的都要

    isred = 0
    For Each rng In Range("创业板概念[所属概念]")
        If isred = 0 Then imax = rng.Offset(0, 3).Value
        If rng.Offset(0, 4).Interior.ColorIndex <> 35 And rng.Offset(0, 5).Interior.ColorIndex <> 35 And rng.Offset(0, 6).Interior.ColorIndex <> 35 And rng.Offset(0, 3) = imax Then
            rng.Offset(0, 3).Interior.Color = 13421823
            isred = isred + 1
        End If
    Next
    imax = 0
    For Each rng In Range("创业板概念[今昨百日新高]")
        If rng.Interior.ColorIndex <> 35 Then
            arr = Split(rng, " | ")
            If arr(0) * 1 > imax Then imax = arr(0)
        End If
    Next
    For Each rng In Range("创业板概念[今昨百日新高]")
        If rng.Interior.ColorIndex <> 35 Then
            arr = Split(rng, " | ")
            If arr(0) * 1 = imax Then
                rng.Offset(0, -1).Interior.Color = 13421823
            End If
        End If
    Next

    
End Sub