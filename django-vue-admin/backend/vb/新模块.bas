Attribute VB_Name = "新模块"
Option Explicit
Sub 全部重算()
    Application.ScreenUpdating = False
    'Application.DisplayAlerts = False
    'Application.Calculation = xlCalculationManual
    Dim t, t1, t0
    重新生成超级表
    If Sheet4.Range("H100") <> Evaluate("round(sum(表1[最高价]),2)") Then 新合并概念

    t = Timer
 '   Sheet4.Range("r1") = "昨日连板天数"
'    Sheet4.Range("af1") = "昨日连板天数"
    'tonum
    '重新生成超级表
    增加前后分号
    主线
    
    连涨算法
    
    生成所属概念
    '删除空行
    '去掉中文括号
    
'    取连涨股票
'    生成连涨概念
'    取涨停原因
'    排列涨停原因
    
    '生成所属概念表
    '条件计算
        t1 = Timer - t
        Debug.Print Round(t1, 2)
        
    概念表上色
    '条件计算
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    补涨
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    表筛选
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    '处理连涨天数
    匹配概念
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    条件格式
    '个股查询
    '概念分表2
    t1 = Timer - t
    
 '   If Sheet4.Range("h3") = "封单开" Then
  '      Sheet4.Range("r1") = "连板天数"
  '      Sheet4.Range("af1") = "连板天数"
  '  End If
    'Application.ScreenUpdating = True
    'Application.Calculation = xlCalculationAutomatic
    Debug.Print Now & "完成"
    MsgBox "完成！耗时：" & Round(t1, 2) & " 秒"
End Sub

Sub 去掉中文括号()
        '替换整理概念前后括号
    Range("表[所属概念]").Replace "】", ";", 2
    Range("表[所属概念]").Replace "【", ";", 2
    Range("表1[所属概念]").Replace "】", ";", 2
    Range("表1[所属概念]").Replace "【", ";", 2
End Sub

Sub 生成所属概念表()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Dim i As Integer
    Dim js_cy, js_zb, a, cyset, zbset, lz
    nogn = ";富时罗素概念;富时罗素概念股;标普道琼斯A股;沪股通;深股通;融资融券;转融券标的;送转填权;股权转让;并购重组;超跌;MSCI概念;一季报增长;业绩增长;年报增长;超跌;"
    '取出有效概念合并成一个长字符串
    cyset = Range("设置值[设置值]").Rows(1)
    zbset = Range("设置值[设置值]").Rows(2)
    For Each rng In Range("表[所属概念]")
        If Left(rng.Offset(0, -4), 5) = "SZ.30" Then '创业
            If rng.Offset(0, 1) > cyset Then gnstr = gnstr & rng
        Else '主板
            If rng.Offset(0, 1) > zbset Then gnstr = gnstr & rng
        End If
    Next
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            If InStr(nogn, ";" & arr(i) & ";") < 1 Then '去掉不要的概念
                'If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
'                        js_cy = Evaluate("COUNTIFS(表[ [  代码] ],""SZ.30*"",表[所属概念],""*;" & arr(i) & ";*"")")
'                        js_zb = Evaluate("SUMPRODUCT(IF(ISERROR(FIND(""SZ.30"",表[  代码])),1,0),IF(ISERROR(FIND("";" & arr(i) & ";"",表[所属概念])),0,1))")
'                        dic(arr(i)) = Array(js_cy, js_zb)
                        dic(arr(i)) = Evaluate("COUNTIFS(表[所属概念],""*;" & arr(i) & ";*"")")
                    End If
                'End If
            End If
        Next
    End If
    

    '把字典输出到概念表
    If Range("创业板概念[#data]").Rows.Count > 1 Then Range("创业板概念[#data]").Delete Shift:=xlShiftUp '清空原表
    Range("创业板概念[实际流通]").NumberFormatLocal = "0.0000_ "
    Range("创业板概念[[#Headers],[所属概念]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    Range("创业板概念[[#Headers],[计数]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)

    Set dic = Nothing '关闭字典
    
    Range("创业板概念[所属概念]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("创业板概念[计数]").Replace "1", "", 1 '1是完全匹配
    Range("创业板概念[计数]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    
    '排序
    Range("创业板概念").Sort "计数", 2, , , , , , 1
    Range("表1").Sort "连涨天数", 2, , , , , , 1
    Range("表2").Sort "连涨天数", 2, , , , , , 1
    
    '计算创业板实际流通
    For Each a In Range("创业板概念[所属概念]")
        If a.Offset(0, 1) > 0 Then
            'a.Offset(0, 2) = Evaluate("round(AVERAGEIFS(表[竞价涨幅],表[所属概念],""*;" & a & ";*""),4)")
            a.Offset(0, 2) = Evaluate("round(SUMIFS(表[竞价涨幅],表[所属概念],""*;" & a & ";*""),4)")
        End If
    Next
    
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


'    For Each a In Range("创业板概念[所属概念]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            'a.Offset(0, 2) = Evaluate("Maxifs(表1[连涨天数],表1[所属概念],""*;" & a & ";*"")")
'            Set rng = Sheet7.Rows(2).Find(a)
'            If Not rng Is Nothing Then
'                lz = rng.End(xlDown).Row - 3
'            End If
'            a.Offset(0, 3) = lz
'            If lz < 2 Then a.Offset(0, 3).Interior.ColorIndex = 35
'        End If
'    Next



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
     '   For Each rng1 In Range("概念筛选[概念筛选]")
      '      If rng1 <> "" Then
       '         Set rng2 = Range("创业板概念[所属概念]").Find(rng1.Value, , , 1) '精确
       '         If Not rng2 Is Nothing Then
       '             rng2.Offset(0, 2).Interior.ColorIndex = 36
       '         End If
       '     End If
       ' Next
    
    '取创业板概念最大计数里的最大实际流通
    '改为创业板概念最大计数的都要
    'imax = Evaluate("MAXIFS(创业板概念[实际流通],创业板概念[计数],MAX(创业板概念[计数]))")
'    imax = Evaluate("MAX(创业板概念[计数])")
'        Set rng1 = Range("创业板概念[计数]")
'        Set rng = rng1.Find(imax)
'        If Not rng Is Nothing Then
'            firstAddress = rng.Address
'            Do
'                 rng.Offset(0, 1).Interior.Color = 13421823
'                 Set rng = rng1.FindNext(rng)
'            Loop While Not rng Is Nothing And rng.Address <> firstAddress
'        End If
    'imax = Evaluate("MAX(创业板概念[计数])")
    isred = 0
    For Each rng In Range("创业板概念[所属概念]")
        If isred = 0 Then imax = rng.Offset(0, 3).Value
        'If rng.Offset(0, -3).Interior.ColorIndex <> 35 And rng.Interior.ColorIndex <> 35 And rng.Offset(0, 1).Interior.ColorIndex <> 35 And rng.Offset(0, 2).Interior.ColorIndex <> 35 And rng = imax Then
        ' 今昨竞封  盘中封单总和 跌停封单额  非绿
        If rng.Offset(0, 4).Interior.ColorIndex <> 35 And rng.Offset(0, 5).Interior.ColorIndex <> 35 And rng.Offset(0, 6).Interior.ColorIndex <> 35 And rng.Offset(0, 3) = imax Then
            rng.Offset(0, 3).Interior.Color = 13421823
            'If rng.Offset(0, -3) <> "国企改革" Then isred = isred + 1
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
                'If rng.Offset(0, -3) <> "国企改革" Then isred = isred + 1
            End If
        End If
    Next

    'Range("创业板概念[实际流通]").NumberFormatLocal = "0.00%"
    
End Sub

Sub 条件计算()
    
    Dim tj As Range
    Dim rng As Range
    Dim gn As Range
    Dim iscyb, iszb, i As Integer
    Dim t As String
    Dim 复活概念
    
'    On Error GoTo line2
'    Range("条件[名称]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'    Range("条件备用[名称]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'    Range("趋势[名称]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'    Range("趋势备用[名称]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'line2:

'    Range("条件[    名称]").Interior.Pattern = xlNone
'    Range("条件[竞价涨幅]").Interior.Pattern = xlNone
    Sheet8.Range("A:V").Interior.Pattern = xlNone
'从原始数据表提取自己输入的股票的数据到备用股票
    For Each tj In Range("条件[名称]")
        Set rng = Range("表1[    名称]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("表2[    名称]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
                
        End If
    Next
    For Each tj In Range("条件备用[名称]")
        Set rng = Range("表1[    名称]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("表2[    名称]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
        End If
    Next
    For Each tj In Range("趋势[名称]")
        Set rng = Range("表1[    名称]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("表2[    名称]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
        End If
    Next
    For Each tj In Range("趋势备用[名称]")
        Set rng = Range("表1[    名称]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("表2[    名称]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
        End If
    Next


    '先去掉以前的颜色
    Range("创业板概念[所属概念]").Interior.Pattern = xlNone
    
    '如果有小于-5%的股票就把备用股票添加到条件表
    

    复活概念 = 0
    If Evaluate("MAX(条件[竞价涨幅])") <= -5 Then
        复活概念 = 1
        For Each tj In Range("条件备用[名称]")
            Set rng = Range("条件[名称]").Find(tj)
            'If rng Is Nothing Then Range("条件").ListObject.ListRows.Add.Range = Array("", tj, "", "", tj.Offset(0, 3))
            If rng Is Nothing Then
                For i = 2 To 13
                    If Sheet8.Cells(i, 2) = "" Then
                        Sheet8.Cells(i, 1) = tj.Offset(0, -1)
                        Sheet8.Cells(i, 2) = tj
                        Sheet8.Cells(i, 3) = tj.Offset(0, 1)
                        Sheet8.Cells(i, 4) = tj.Offset(0, 2)
                        If Sheet8.Cells(i, 4) <= -5 Then Sheet8.Cells(i, 4).Interior.ColorIndex = 35
                        Sheet8.Cells(i, 5) = tj.Offset(0, 3)
                        
                        Exit For
                    End If
                Next
            End If
        Next
'        For Each tj In Range("条件[名称]")
'            Set rng = Range("表1[    名称]").Find(tj)
'            If Not rng Is Nothing Then
'                tj.Interior.ColorIndex = 15
'            Else
'                Set rng = Range("表2[    名称]").Find(tj)
'            End If
'            If Not rng Is Nothing Then
'                    tj.Offset(0, -1) = rng.Offset(0, -1)
'                    tj.Offset(0, 1) = rng.Offset(0, 3)
'                    tj.Offset(0, 2) = rng.Offset(0, 4)
'            End If
'        Next
    End If
    

'    If Evaluate("MAX(条件[竞价涨幅])") <= -0.05 Then
'        For Each tj In Range("备用股票2[备用股票2]")
'            Set rng = Range("条件[    名称]").Find(tj)
'            If rng Is Nothing Then Range("条件").ListObject.ListRows.Add.Range = Array("", tj, "", "", tj.Offset(0, 3))
'        Next
'        For Each tj In Range("条件[    名称]")
'            Set rng = Range("表1[    名称]").Find(tj)
'            If Not rng Is Nothing Then
'                tj.Interior.ColorIndex = 15
'            Else
'                Set rng = Range("表2[    名称]").Find(tj)
'            End If
'            If Not rng Is Nothing Then
'                    tj.Offset(0, -1) = rng.Offset(0, -1)
'                    tj.Offset(0, 1) = rng.Offset(0, 3)
'                    tj.Offset(0, 2) = rng.Offset(0, 4)
'            End If
'        Next
'    End If


    

    
    '条件表匹配概念表,让其变黄色
    For Each tj In Range("条件[所属概念]")
        If tj.Offset(0, 1) > -5 Then
            For Each gn In Range("创业板概念[所属概念]")
                If InStr(tj, ";" & gn & ";") > 0 Then
                    If gn.Offset(0, 1) = 0 Then
                        gn.Interior.ColorIndex = 34
                    Else
                        gn.Interior.ColorIndex = 36
                    End If
                End If
            Next
        End If
    Next
    '条件表匹配概念表,让其变绿色
    For Each tj In Range("条件[所属概念]")
        If tj.Offset(0, 1) <= -5 Then
            tj.Offset(0, 1).Interior.ColorIndex = 35
            For Each gn In Range("创业板概念[所属概念]")
                If InStr(tj, ";" & gn & ";") > 0 Then gn.Interior.ColorIndex = 35
            Next
        End If
    Next
    '如果启用了备用股票，条件表匹配概念表,让其绿色复活
    If 复活概念 Then
        For Each tj In Range("条件[所属概念]")
            If tj.Offset(0, 1) > -5 Then
                For Each gn In Range("创业板概念[所属概念]")
                    If InStr(tj, ";" & gn & ";") > 0 And gn.Interior.ColorIndex = 35 Then gn.Interior.ColorIndex = 36
                Next
            End If
        Next
    End If
    
    
    复活概念 = 0
    If Evaluate("MAX(趋势[竞价涨幅])") <= -5 Then
        复活概念 = 1
        For Each tj In Range("趋势备用[名称]")
            Set rng = Range("趋势[名称]").Find(tj)
            'If rng Is Nothing Then Range("趋势").ListObject.ListRows.Add.Range = Array("", tj, "", "", tj.Offset(0, 3))
            If rng Is Nothing Then
                For i = 15 To 30
                    If Sheet8.Cells(i, 2) = "" Then
                        Sheet8.Cells(i, 1) = tj.Offset(0, -1)
                        Sheet8.Cells(i, 2) = tj
                        Sheet8.Cells(i, 3) = tj.Offset(0, 1)
                        Sheet8.Cells(i, 4) = tj.Offset(0, 2)
                        If Sheet8.Cells(i, 4) <= 5 Then Sheet8.Cells(i, 4).Interior.ColorIndex = 35
                        Sheet8.Cells(i, 5) = tj.Offset(0, 3)
                        Exit For
                    End If
                Next
            End If
        Next
'        For Each tj In Range("趋势[名称]")
'            Set rng = Range("表1[    名称]").Find(tj)
'            If Not rng Is Nothing Then
'                tj.Interior.ColorIndex = 15
'            Else
'                Set rng = Range("表2[    名称]").Find(tj)
'            End If
'            If Not rng Is Nothing Then
'                    tj.Offset(0, -1) = rng.Offset(0, -1)
'                    tj.Offset(0, 1) = rng.Offset(0, 3)
'                    tj.Offset(0, 2) = rng.Offset(0, 4)
'            End If
'        Next
    End If

    
    '条件表匹配概念表,让其变黄色
    For Each tj In Range("趋势[所属概念]")
        If tj.Offset(0, 1) > -5 Then
            For Each gn In Range("创业板概念[所属概念]")
                If InStr(tj, ";" & gn & ";") > 0 Then
                    If gn.Offset(0, 1) = 0 Then
                        gn.Interior.ColorIndex = 34
                    Else
                        gn.Interior.ColorIndex = 36
                    End If
                End If
            Next
        End If
    Next
    '条件表匹配概念表,让其变绿色
    For Each tj In Range("趋势[所属概念]")
        If tj.Offset(0, 1) <= -5 Then
            tj.Offset(0, 1).Interior.ColorIndex = 35
            For Each gn In Range("创业板概念[所属概念]")
                If InStr(tj, ";" & gn & ";") > 0 Then gn.Interior.ColorIndex = 35
            Next
        End If
    Next
    '如果启用了备用股票，条件表匹配概念表,让其绿色复活
    If 复活概念 Then
        For Each tj In Range("趋势[所属概念]")
            If tj.Offset(0, 1) > -5 Then
                For Each gn In Range("创业板概念[所属概念]")
                    If InStr(tj, ";" & gn & ";") > 0 And gn.Interior.ColorIndex = 35 Then gn.Interior.ColorIndex = 36
                Next
            End If
        Next
    End If
    '备用股票表匹配概念表,让其变绿色
'    For Each tj In Range("备用股票[所属概念]")
'        If tj.Offset(0, 1) <= -0.05 Then
'            tj.Offset(0, 1).Interior.ColorIndex = 35
'            For Each gn In Range("创业板概念[所属概念]")
'                If InStr(tj, ";" & gn & ";") > 0 Then gn.Interior.ColorIndex = 35
'            Next
'        End If
'    Next
    
'    Range("条件[竞价涨幅]").NumberFormatLocal = "0.00%"
'    Range("条件备用[竞价涨幅]").NumberFormatLocal = "0.00%"
'    Range("趋势[竞价涨幅]").NumberFormatLocal = "0.00%"
'    Range("趋势备用[竞价涨幅]").NumberFormatLocal = "0.00%"
End Sub
Sub tt()
    'Debug.Print Range("c3").Interior.Color
    Dim i As Integer
    i = 2
    Do While Sheet8.Range("A" & i) <> ""
        Debug.Print Sheet8.Range("A" & i)
        i = i + 1
    Loop
End Sub
Sub 表筛选()
    Debug.Print Now & "表筛选"
    Dim h1, h2, yd, i As Integer
    Dim a As Range
    Dim arr
    Dim firstAddress
  '  On Error Resume Next
'    ActiveWorkbook.Names("Criteria").Delete
'    ActiveWorkbook.Names("Extract").Delete

    ActiveSheet.ListObjects("T1_匹配").Unlist
    ActiveSheet.ListObjects("T2_匹配").Unlist
    Dim rng As Range
    Dim rng1 As Range
    Dim rng2 As Range
    Dim allgn As String
    'Sheet4.Range("af2:az1048576").Clear
    Sheet4.Range("i2:bh1048576").Clear
    h1 = 1
    allgn = ""
    For Each a In Range("创业板概念[所属概念]")
        If a.Interior.Color = 13421823 Or a.Offset(0, 3).Interior.Color = 13421823 Then
            allgn = allgn & ";" & a & ";"
            h1 = h1 + 1
            Sheet4.Range("an" & h1) = "*;" & a & ";*"
            Sheet4.Range("ao" & h1) = "SZ.30*"
            'Sheet4.Range("ap" & h1) = "SH.68*"
            Sheet4.Range("am" & h1) = a
            Sheet4.Range("am" & h1).Interior.Color = 13421823
            
            Sheet4.Range("as" & h1) = "*;" & a & ";*"
            Sheet4.Range("at" & h1) = "<>SZ.30*"
            Sheet4.Range("au" & h1) = "<>SH.68*"
            Sheet4.Range("ar" & h1) = a
            Sheet4.Range("ar" & h1).Interior.Color = 13421823
        End If
    Next
    '补涨概念
    
    arr = Split(Sheet4.Range("h9"), ";")
    For i = LBound(arr) To UBound(arr)
        If arr(i) <> "" Then
            
            
            Set a = Range("创业板概念[所属概念]").Find(arr(i), , , 1)
            If Not a Is Nothing Then
                If a.Offset(0, 4).Interior.ColorIndex = 35 Then GoTo NextIteration
            End If

            'Debug.Print arr(i)
            allgn = allgn & ";" & arr(i) & ";"
            h1 = h1 + 1
            Sheet4.Range("an" & h1) = "*;" & arr(i) & ";*"
            Sheet4.Range("ao" & h1) = "SZ.30*"
            'Sheet4.Range("ap" & h1) = "SH.68*"
            Sheet4.Range("am" & h1) = arr(i)
            'Sheet4.Range("am" & h1).Interior.Color = a.Interior.Color
            
            Sheet4.Range("as" & h1) = "*;" & arr(i) & ";*"
            Sheet4.Range("at" & h1) = "<>SZ.30*"
            Sheet4.Range("au" & h1) = "<>SH.68*"
            Sheet4.Range("ar" & h1) = arr(i)
            'Sheet4.Range("ar" & h1).Interior.Color = a.Interior.Color
        End If
NextIteration:
        Debug.Print i
    
    Next
    
    Sheet4.Range("am1") = h1
    Sheet4.Range("ar1") = h1
    
    h1 = 1
    h2 = 2
    ' 主线取前3
    For i = 2 To 4
        
        If InStr(allgn, ";" & Sheet25.Cells(i, 1) & ";") > 0 Then
            h1 = h1 + 1
            
            Set rng2 = Sheet25.Cells(i, 1)
            Set rng2 = Sheet4.Range("A:A").Find(rng2)
            If Not rng2 Is Nothing Then
                Sheet4.Range("aw" & h1) = Sheet25.Cells(i, 1)
                Sheet4.Range("ax" & h1) = "*;" & Sheet25.Cells(i, 1) & ";*"
                Sheet4.Range("ay" & h1) = "SZ.30*"
                'Sheet4.Range("ap" & h1) = "SH.68*"
                
    
                
                Sheet4.Range("ba" & h1) = Sheet25.Cells(i, 1)
                Sheet4.Range("bb" & h1) = "*;" & Sheet25.Cells(i, 1) & ";*"
                Sheet4.Range("bc" & h1) = "<>SZ.30*"
                Sheet4.Range("bd" & h1) = "<>SH.68*"
                Sheet25.Cells(i, 1).Interior.ColorIndex = 38
                Sheet25.Cells(h2, 4) = Sheet25.Cells(i, 1)
                Sheet25.Cells(h2, 5) = Sheet25.Cells(i, 2)
                
                h2 = h2 + 1
            End If
            If h1 > 5 Then
                Exit For
            End If
        End If
    Next

    If Sheet25.Range("d2") = "" Then
        Sheet25.Range("i:j").Sort "主线源数量", 2, , , , , , 1
        Sheet25.Range("d2") = Sheet25.Range("i2")
        Sheet25.Range("e2") = Sheet25.Range("j2")
        
        h1 = h1 + 1
        
        Sheet4.Range("aw" & h1) = Sheet25.Range("d2")
        Sheet4.Range("ax" & h1) = "*;" & Sheet25.Range("d2") & ";*"
        Sheet4.Range("ay" & h1) = "SZ.30*"
        'Sheet4.Range("ap" & h1) = "SH.68*"
        

        
        Sheet4.Range("ba" & h1) = Sheet25.Range("d2")
        Sheet4.Range("bb" & h1) = "*;" & Sheet25.Range("d2") & ";*"
        Sheet4.Range("bc" & h1) = "<>SZ.30*"
        Sheet4.Range("bd" & h1) = "<>SH.68*"
        
        
    End If
    
    Sheet4.Range("aw1") = h1
    Sheet4.Range("ba1") = h1
    
    If h1 = 1 Then
         ActiveSheet.ListObjects.Add(xlSrcRange, Range("j1").CurrentRegion, , xlYes).Name = "T1_匹配"
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("x1").CurrentRegion, , xlYes).Name = "T2_匹配"
       Exit Sub
    End If
    
    
    Dim t, t1, t0
    t = Timer
    
    If h1 > 1 Then
        Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("ax1:ay" & h1), Sheet4.Range("j1:s1")
        Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("bb1:bd" & h1), Sheet4.Range("x1:ag1")
    End If
            t1 = Timer - t
      '  Debug.Print Round(t1, 2) & "----"
        
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("j1").CurrentRegion, , xlYes).Name = "T1_匹配"
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("x1").CurrentRegion, , xlYes).Name = "T2_匹配"

    表筛选2
End Sub


Sub 表筛选2()
    Debug.Print Now & "表筛选2"
    Dim h1, h2, yd, i As Integer
    Dim a As Range
    Dim arr
    Dim firstAddress

    Dim rng As Range
    Dim rng1 As Range
    Dim ngs As Range
    Dim allgn As String

   ' If Sheet4.Range("h3") = "封单关" Then
   '     For Each rng In Range("T1_匹配[  代码]")
   '         Set rng1 = Sheet2.Range("A:A").Find(rng)
   '         rng.Offset(0, 4) = rng1.Offset(0, 5)
   '     Next
   '      For Each rng In Range("T2_匹配[  代码]")
   '         Set rng1 = Sheet2.Range("A:A").Find(rng)
   '         rng.Offset(0, 4) = rng1.Offset(0, 5)
   '     Next
   ' End If
    
    ' 封单开 涨停原因表的昨日连板天数要取table1里的连板天数列
 '   If Sheet4.Range("h3") = "封单开" Then
 '       For Each rng In Range("T1_匹配[  代码]")
 '           Set rng1 = Sheet2.Range("A:A").Find(rng)
 '           rng.Offset(0, 8) = rng1.Offset(0, 25)
 '       Next
 '        For Each rng In Range("T2_匹配[  代码]")
 '           Set rng1 = Sheet2.Range("A:A").Find(rng)
 '           rng.Offset(0, 8) = rng1.Offset(0, 25)
 '       Next
 '   End If
    
        
    Range("T1_匹配").Sort "4日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "4日涨跌幅", 2, , , , , , 1
    yd = Sheet18.Range("a1").End(xlDown).Row '异动表行数
    For Each rng In Range("T1_匹配[  代码]")
        If InStr(Sheet4.Range("H33"), ";" & rng.Offset(0, 1) & ";") Then rng.Offset(0, 1).Interior.ColorIndex = 35
            
            
'        Set rng1 = Sheet16.Range("A:A").Find(rng.Value)
'        If Not rng Is Nothing Then
'            rng.Offset(0, 8) = rng1.Offset(0, 5)
'            rng.Offset(0, 9) = rng1.Offset(0, 4)
'            'rng.Offset(0, 10) = rng1.Offset(0, 10)
'        End If
'        Set rng1 = Sheet18.Range("A:A").Find(rng.Value)
'        If Not rng Is Nothing Then
'            rng.Offset(0, 10) = rng1.Offset(0, 4)
'        End If
        
        'rng.Offset(0, 11) = rng.Offset(0, 6) / rng.Offset(0, 7)
        'rng.Offset(0, 12) = rng.Offset(0, 6) / rng.Offset(0, 5)
        rng.Offset(0, 10) = Evaluate("COUNTIFS(异动!A:A,""" & rng & """,异动!J:J,""连续*"")")
        Set rng1 = Sheet18.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then
            firstAddress = rng1.Address
            'rng.Offset(0, 12) = 0
            Do
                If rng1.Offset(0, 6) <> "" Then
                    rng.Offset(0, 11) = rng1.Offset(0, 6)
                    Exit Do
                End If
                'If rng1.Offset(0, 12) > 0 Then rng.Offset(0, 12) = rng1.Offset(0, 12)
                Set rng1 = Sheet18.Range("A:A").FindNext(rng1)
            Loop While Not rng1 Is Nothing And rng1.Address <> firstAddress
        End If
        Set rng1 = Sheet14.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then rng.Offset(0, 12) = "创百日新高"
        
        Set rng1 = Sheet24.Range("A:A").Find(rng.Value)
        
         If Not rng1 Is Nothing Then
            rng.Offset(0, 12).Interior.ColorIndex = 37
            If rng1.Offset(0, 7) > 0 Then rng.Offset(0, 8).Interior.ColorIndex = 38
            If rng1.Offset(0, 5) > 0 Then rng.Offset(0, 8).Interior.ColorIndex = 38
            If rng1.Offset(0, 6) = "涨停" And rng.Offset(0, 8) = 0 Then
                rng.Offset(0, 8).Interior.ColorIndex = 38
                'rng.Offset(0, 12) = rng.Offset(0, 12) & ";" & "反包"
            End If
        End If
    Next
    
    For Each rng In Range("T2_匹配[  代码]")
        If InStr(Sheet4.Range("H33"), ";" & rng.Offset(0, 1) & ";") Then rng.Offset(0, 1).Interior.ColorIndex = 35
'        Set rng1 = Sheet16.Range("A:A").Find(rng.Value)
'        If Not rng Is Nothing Then
'            rng.Offset(0, 8) = rng1.Offset(0, 5)
'            rng.Offset(0, 9) = rng1.Offset(0, 4)
'            'rng.Offset(0, 10) = rng1.Offset(0, 10)
'        End If
        
        
'        Set rng1 = Sheet18.Range("A:A").Find(rng.Value)
'        If Not rng Is Nothing Then
'            rng.Offset(0, 10) = rng1.Offset(0, 4)
'        End If
        
        'rng.Offset(0, 11) = rng.Offset(0, 6) / rng.Offset(0, 7)
        'rng.Offset(0, 12) = rng.Offset(0, 6) / rng.Offset(0, 5)
        rng.Offset(0, 10) = Evaluate("COUNTIFS(异动!A:A,""" & rng & """,异动!J:J,""连续*"")")
        Set rng1 = Sheet18.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then
            firstAddress = rng1.Address
            'rng.Offset(0, 12) = 0
            Do
                If rng1.Offset(0, 6) <> "" Then
                    rng.Offset(0, 11) = rng1.Offset(0, 6)
                    Exit Do
                End If
                'If rng1.Offset(0, 12) > 0 Then rng.Offset(0, 12) = rng1.Offset(0, 12)
                Set rng1 = Sheet18.Range("A:A").FindNext(rng1)
            Loop While Not rng1 Is Nothing And rng1.Address <> firstAddress
        End If
        Set rng1 = Sheet14.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then rng.Offset(0, 12) = "创百日新高"
        
        Set rng1 = Sheet23.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then
            If rng1.Offset(0, 10) > 0 Then rng.Offset(0, 8).Interior.ColorIndex = 38
            rng.Offset(0, 12).Interior.ColorIndex = 37
            If rng1.Offset(0, 6) = "曾涨停" Then rng.Offset(0, 8).Interior.ColorIndex = 38
            If rng1.Offset(0, 7) = "涨停" And rng.Offset(0, 8) = 0 Then
                rng.Offset(0, 8).Interior.ColorIndex = 38
                'rng.Offset(0, 12) = rng.Offset(0, 12) & ";" & "反包"
            End If
        End If
        
    Next

    
    '去掉25日涨停次数是0的股票
    On Error GoTo line
     Range("T2_匹配[25日涨停次数]").Replace "0", "", 1
     Range("T2_匹配[25日涨停次数]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp

line:

    
    '取封停板时长
    For Each rng In Range("T2_匹配[  代码]")
        Set rng1 = Sheet2.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then
            rng.Offset(0, 13) = Round(rng1.Offset(0, 14) / 100000000, 2)
        End If
    Next
    
    Range("T1_匹配[涨跌幅]").NumberFormatLocal = "0.00% "
    Range("T1_匹配[竞价量比]").NumberFormatLocal = "0.00% "
    Range("T1_匹配[今昨量比]").NumberFormatLocal = "0.00_ "
    Range("T1_匹配[4日涨跌幅]").NumberFormatLocal = "0.00% "
    Range("T1_匹配[120日涨跌幅]").NumberFormatLocal = "0.00% "
    Range("T2_匹配[涨跌幅]").NumberFormatLocal = "0.00% "
    Range("T2_匹配[竞价量比]").NumberFormatLocal = "0.00% "
    Range("T2_匹配[今昨量比]").NumberFormatLocal = "0.00_ "
    Range("T2_匹配[4日涨跌幅]").NumberFormatLocal = "0.00% "
    Range("T2_匹配[120日涨跌幅]").NumberFormatLocal = "0.00% "
    Range("表1").AutoFilter

End Sub










Sub 概念查询()
    Debug.Print Now & "概念查询"
    Application.ScreenUpdating = False
    Dim h1, h2, yd As Integer
    Dim a As Range
    Dim gncs As String
    Dim arr
    Dim i As Integer
    Dim firstAddress
    On Error Resume Next
'    ActiveWorkbook.Names("Criteria").Delete
'    ActiveWorkbook.Names("Extract").Delete

    ActiveSheet.ListObjects("T1_匹配").Unlist
    ActiveSheet.ListObjects("T2_匹配").Unlist
    Dim rng As Range
    Dim rng1 As Range
    'Sheet4.Range("af2:az1048576").Clear
    Sheet4.Range("i2:bd1048576").Clear
    gncs = Sheet4.Range("h19")
    arr = Split(Left(gncs, Len(gncs) - 1), ";")
    h1 = 1
    For i = LBound(arr) To UBound(arr)
        If a <> "" Then
         '   Set a = Range("创业板概念[所属概念]").Find(arr(i), , , 1)
         '   If Not a Is Nothing And a.Offset(0, 4).Interior.ColorIndex = 35 Then
          '     Debug.Print a
          '      GoTo NextIteration
        '    End If
            
            h1 = h1 + 1
            Sheet4.Range("aw" & h1) = arr(i)
            Sheet4.Range("ax" & h1) = "*;" & arr(i) & ";*"
            Sheet4.Range("ay" & h1) = "SZ.30*"
            
            Sheet4.Range("ba" & h1) = arr(i)
            Sheet4.Range("bb" & h1) = "*;" & arr(i) & ";*"
            Sheet4.Range("bc" & h1) = "<>SZ.30*"
            Sheet4.Range("bd" & h1) = "<>SH.68*"
        End If
NextIteration:
        
    Next

    
    Sheet4.Range("aw1") = h1
    Sheet4.Range("ba1") = h1
    
    If h1 > 1 Then
        Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("ax1:ay" & h1), Sheet4.Range("j1:s1")
        Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("bb1:bd" & h1), Sheet4.Range("x1:ag1")
    End If
    
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("j1").CurrentRegion, , xlYes).Name = "T1_匹配"
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("x1").CurrentRegion, , xlYes).Name = "T2_匹配"
    
    
    表筛选2
    匹配概念
    Application.ScreenUpdating = True
    
 
End Sub
Sub 首板概念()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Dim gnstr As String
    Dim hs, i As Integer
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("ao2") = "" Then Exit Sub
    gnstr = ""
    hs = Sheet5.Range("ao1").End(xlDown).Row
    
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("at" & i)
    Next
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
        Next
    End If
    arr = dic.keys
    gnstr = Join(arr, ";") & ";"
    Sheet4.Range("H19") = gnstr
    'MsgBox gnstr
End Sub

Sub 昨首板()
    Dim rng As Range
    Dim h, i As Integer
    Dim gnstr As String
    Set rng = Sheet21.Range("a:a").Find("首板")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    gnstr = ""
    For i = 1 To 256 Step 3
        If Sheet21.Cells(h, i) = "" Then Exit For
        gnstr = gnstr & Sheet21.Cells(h, i) & ";"
    Next
    Sheet4.Range("H19") = gnstr
    'MsgBox gnstr
End Sub


Sub 处理连涨天数()
    Dim tj, rng, r As Range
    For Each tj In Range("条件[名称]")
        Set rng = Range("T1_匹配[    名称]").Find(tj)
        If rng Is Nothing Then Set rng = Range("T2_匹配[    名称]").Find(tj)
        If Not rng Is Nothing Then rng.Offset(0, 6) = tj.Offset(0, 3)
    Next
    For Each tj In Range("趋势[名称]")
        Set rng = Range("T1_匹配[    名称]").Find(tj)
        If rng Is Nothing Then Set rng = Range("T2_匹配[    名称]").Find(tj)
        If Not rng Is Nothing Then rng.Offset(0, 6) = tj.Offset(0, 3)
    Next
    Range("T1_匹配").Sort "竞价涨幅", 2, , , , , , 1
    Range("T2_匹配").Sort "连涨天数", 2, "竞价涨幅", , 2, , , 1
'    Range("T1_匹配[分时量比]").Replace "sam", "", 2
'    Range("T2_匹配[分时量比]").Replace "sam", "", 2
'    Range("表1").Sort "连涨天数", 2, , , , , , 1
'    Range("表2").Sort "连涨天数", 2, , , , , , 1

End Sub
Sub te()
    Debug.Print Len(Sheet4.Range("L2"))
'Range("T1_匹配[分时量比]").Replace "sam", "", 2
End Sub
Sub 匹配概念()
    Debug.Print Now & "匹配概念"
    Dim gp, rng, rng3, rng4, rng5, rng6, rng7 As Range
    Dim temp, qx As String
    Dim js, i, h As Integer
    Dim yz, imax1, imax2, imin1, imin2, ijjlb1, ijjlb2, ijzlb1, ijzlb2 As Double
    qx = Sheet4.Range("H6")
    
    
    If Sheet4.Range("aw1") = 1 Then
        Exit Sub
    End If
    
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
        'For i = 2 To Sheet4.Range("aw1").Value
        For i = 2 To Sheet4.Range("aw1")
            If InStr(gp, ";" & Sheet4.Range("aw" & i) & ";") > 0 Then
                'If Sheet4.Range("am" & i).Interior.Color = 13421823 Then gp.Offset(0, -2).Interior.Color = 13421823
                temp = temp & Sheet4.Range("aw" & i) & ";"
                'js = js + 1
            End If
        Next
        If temp <> "" Then temp = Left(temp, Len(temp) - 1)
        'gp.Offset(0, -1).Value = js
        gp.Value = temp
'        '红
'        If gp.Offset(0, 5) > 1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 1 And gp.Offset(0, 2) >= 0.2 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 0 And gp.Offset(0, 2) >= 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 2) < 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        '绿
'        If gp.Offset(0, 7) > 2 Or gp.Offset(0, 8) <> "" Or gp.Offset(0, 9) > 0 Then gp.Offset(0, -2).Interior.ColorIndex = 35
'        If gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 Then gp.Offset(0, 4).Interior.Color = 13551615
'        If gp.Offset(0, 4) > 1000 Then gp.Offset(0, 4).Interior.ColorIndex = 35
    Next
    
    For Each gp In Range("T2_匹配[所属概念]")
        temp = ""
        js = 0
        'For i = 2 To Sheet4.Range("aR1").Value
        For i = 2 To Sheet4.Range("aw1")
            If InStr(gp, ";" & Sheet4.Range("aw" & i) & ";") > 0 Then
                'If Sheet4.Range("ar" & i).Interior.Color = 13421823 Then gp.Offset(0, -2).Interior.Color = 13421823
                temp = temp & Sheet4.Range("aw" & i) & ";"
                'js = js + 1
            End If
        Next
        If temp <> "" Then temp = Left(temp, Len(temp) - 1)
        'gp.Offset(0, -1).Value = js
        gp.Value = temp
'        '红
'        If gp.Offset(0, 5) > 1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 1 And gp.Offset(0, 2) >= 0.2 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 0 And gp.Offset(0, 2) >= 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 2) < 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        '绿
'        If gp.Offset(0, 7) > 2 Or gp.Offset(0, 8) <> "" Or gp.Offset(0, 9) > 0 Then gp.Offset(0, -2).Interior.ColorIndex = 35
'        If gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 Then gp.Offset(0, 4).Interior.Color = 13551615
'        If gp.Offset(0, 4) > 1000 Then gp.Offset(0, 4).Interior.ColorIndex = 35
'        If gp.Offset(0, 5) = 0 And gp.Offset(0, 2) >= 0.1 Then
'            If Not (gp.Offset(0, 4) >= 100 And gp.Offset(0, 3) >= 0.08) Then gp.Offset(0, -2).Interior.ColorIndex = 35
'        End If
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
        '比较阈值, 价量比大于等于8%
     '   If gp.Offset(0, 3) >= yz And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
        '1：情绪好和差时 ，异动次数大于等于3或者监管类型有数据 且异动是开的情况下
        If (gp.Offset(0, 8) >= 4 And Sheet4.Range("H90") = "异动开" And gp.Offset(0, 10) = "") Then gp.Offset(0, -1).Interior.ColorIndex = 35
       
        
        If qx = "差" Then
          ' 或者停牌非0或今昨量比大于700或者竞价量比大于等于100或 (自由流通市值大于80且不符合塞力斯概念 H13)，其中任何一种情况发生，就名称绿
          '竞价量比大于等于50
            If gp.Offset(0, 9) <> "" Or gp.Offset(0, 5) > 700 Or gp.Offset(0, 4) >= 0.5 Or (gp.Offset(0, 11) > 100 And gp.Offset(0, -1) <> Sheet4.Range("H13")) Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
            End If
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 2) < 0 And Sheet4.Range("H11") <> gp.Offset(0, -1) Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Offset(0, 2).Interior.ColorIndex = 35
            End If
            'If gp.Offset(0, 6) = 2 And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            '情绪差，竞价未匹配大于0的话， 竞价未匹配列和名称列绿这个代码不要了
            If gp <> "" Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Interior.ColorIndex = 35
            End If
            
            '连扳超过2 就绿
            If gp.Offset(0, 6) > 2 Then
                If gp.Column <> 12 And (gp.Offset(0, 6) < Sheet4.Range("H10") Or gp.Offset(0, -1) <> Sheet4.Range("H11")) Then gp.Offset(0, -1).Interior.ColorIndex = 35
                If gp.Column = 12 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            End If
            
            ' 连扳=2 价量比大于等于8%  就绿
            'If gp.Offset(0, 6) = 2 And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            '创业板情绪差原来是4日涨跌幅大于20%就绿改成4日涨跌幅大于100%
            If gp.Column = 12 And gp.Offset(0, 3) > 1 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            
            '这个数字和名称 和主板那里的昨日连板天数最大值数字和名称是一样的，竞价未匹配的绿去除
            If gp.Offset(0, -1) = Sheet4.Range("H11") And gp.Offset(0, 6) = Sheet4.Range("H10") And gp <> "" Then
                gp.Interior.Color = xlNone
                gp.Offset(0, -1).Interior.Color = xlNone
            End If
        Else
             ' 或者停牌非0或今昨量比大于700或者竞价量比大于等于100或 (自由流通市值大于80且不符合塞力斯概念 H13)，其中任何一种情况发生，就名称绿
            If gp.Offset(0, 9) <> "" Or gp.Offset(0, 5) > 700 Or gp.Offset(0, 4) >= 1 Or (gp.Offset(0, 11) > 100 And gp.Offset(0, -1) <> Sheet4.Range("H13")) Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
            End If
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
                
                'If gp.Offset(0, -1).Interior.ColorIndex <> 35 Then
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
    '========================
'    For Each gp In Union(Range("T1_匹配[所属行业]"), Range("T2_匹配[所属行业]"))
'        If qx = "好" Then
'            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then
'                gp.Offset(0, 4).Interior.Color = 13551615
'                If gp.Offset(0, -1).Interior.ColorIndex <> 35 Then
'                    If gp.Column = 12 Then
'                        If gp.Offset(0, 3) >= imax1 Then
'                            imax1 = gp.Offset(0, 3)
'                            'gp.Offset(0, -1).Interior.Color = 13551615
'                        End If
'                    Else
'                        If gp.Offset(0, 3) >= imax2 Then
'                            imax2 = gp.Offset(0, 3)
'                            'gp.Offset(0, -1).Interior.Color = 13551615
'                        End If
'                    End If
'                End If
'            End If
'            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then gp.Offset(0, 5).Interior.Color = 13551615
'        Else '情绪差时
'            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then
'
'                If gp.Offset(0, -1).Interior.ColorIndex <> 35 Then
'                gp.Offset(0, 4).Interior.Color = 13551615
'                    If gp.Column = 12 Then
'                        If gp.Offset(0, 4) >= ijjlb1 Then
'                            ijjlb1 = gp.Offset(0, 4)
'                            'gp.Offset(0, 4).Interior.ColorIndex = 3
'                            'gp.Offset(0, -1).Interior.Color = 13551615
'                        End If
'                        If gp.Offset(0, 3) >= imax1 Then
'                            imax1 = gp.Offset(0, 3)
'                            gp.Offset(0, -1).Interior.Color = 13551615
'                        End If
'                    Else
'                        If gp.Offset(0, 4) >= ijjlb2 Then
'                            ijjlb2 = gp.Offset(0, 4)
'                            'gp.Offset(0, 4).Interior.ColorIndex = 3
'                            'gp.Offset(0, -1).Interior.Color = 13551615
'                        End If
'                        If gp.Offset(0, 3) >= imax2 Then
'                            imax2 = gp.Offset(0, 3)
'                            gp.Offset(0, -1).Interior.Color = 13551615
'                        End If
'                    End If
'                End If
'            End If
'            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then
'
'                'If gp.Offset(0, -1).Interior.ColorIndex <> 35 Then
'                gp.Offset(0, 5).Interior.Color = 13551615
'                    If gp.Column = 12 Then
'                        If gp.Offset(0, 5) >= ijzlb1 Then
'                            ijzlb1 = gp.Offset(0, 5)
'                            'gp.Offset(0, 5).Interior.ColorIndex = 3
'                        End If
'                    Else
'                        If gp.Offset(0, 5) >= ijzlb2 Then
'                            ijzlb2 = gp.Offset(0, 5)
'                            'gp.Offset(0, 5).Interior.ColorIndex = 3
'                        End If
'                    End If
'                'End If
'            End If
'        End If
'
'    Next
    If qx = "好" Then
'        Set rng = Sheet4.Range("P:P").Find(ijjlb1, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'            rng.Offset(0, -5).Interior.Color = 13551615
'        End If
'        Set rng = Range("T2_匹配[竞价量比]").Find(ijjlb2, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'            rng.Offset(0, -5).Interior.Color = 13551615
'        End If
'
'        Set rng = Range("T1_匹配[今昨量比]").Find(ijzlb1, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'        End If
'        Set rng = Range("T2_匹配[今昨量比]").Find(ijzlb2, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'        End If
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
'    imax1 = 0
'    imax2 = 0
'    For Each gp In Union(Range("T1_匹配[    名称]"), Range("T2_匹配[    名称]"))
'        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
'            If gp.Offset(0, 5) < 0.08 Or gp.Offset(0, 5) > 1 Then
'                If gp.Column = 11 Then
'                    If gp.Offset(0, 4) >= imax1 Then
'                        imax1 = gp.Offset(0, 4)
'                        gp.Interior.ColorIndex = 36
'                    End If
'                Else
'                    If gp.Offset(0, 4) >= imax2 Then
'                        imax2 = gp.Offset(0, 4)
'                        gp.Interior.ColorIndex = 36
'                    End If
'                End If
'            End If
'        End If
'    Next

   ' For Each gp In Range("T1_匹配[    名称]")
    '    If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
     '       gp.Interior.ColorIndex = 36
      '      Exit For
    '    End If
  '  Next
  '  For Each gp In Range("T2_匹配[    名称]")
  '      If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
  '          gp.Interior.ColorIndex = 36
   '         Exit For
   '     End If
   ' Next
    
    Range("T1_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    For Each gp In Range("T1_匹配[    名称]")
        If gp.Offset(0, 3) > 0 Then
            Set rng = Sheet2.Range("b:b").Find(gp, , , 1)
            If rng.Offset(0, 23) < 0 Then
                gp.Interior.ColorIndex = 36
                Exit For
            End If
        End If
    Next
    For Each gp In Range("T2_匹配[    名称]")
       If gp.Offset(0, 3) > 0 Then
            Set rng = Sheet2.Range("b:b").Find(gp, , , 1)
            If rng.Offset(0, 23) < 0 Then
                gp.Interior.ColorIndex = 36
                Exit For
            End If
        End If
    Next
    
    
'    For Each gp In Union(Range("T1_匹配[所属行业]"), Range("T2_匹配[所属行业]"))
'        '比较阈值
'        If gp.Offset(0, 3) >= yz Then gp.Offset(0, -1).Interior.ColorIndex = 35
'
'        If qx = "差" Then
'            If gp <> "" Then gp.Offset(0, -1).Interior.ColorIndex = 35 '竞价未匹配不为空的
'            If gp.Offset(0, 8) < 3 And gp.Offset(0, 9) = "" And gp.Offset(0, 10) < 1 Then '异动次数小于3，监管类型没有数据，停牌是0
'                '1情绪差时，昨日连板天数大于1的，只要竞价量比大于等于8%并且小于100%, 今昨量比小于等于500，异动次数小于3，监管类型没有数据，停牌是0 就可以红
'                'If gp.Offset(0, 6) > 1 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 6) < 1 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'
'                If gp.Offset(0, 2) > 0 Then
'                    '2昨日连板天数是1的 如果5日涨跌幅小于20%，竞价量比大于等于8%，今昨量比小于等于500，异动次数小于3，监管类型没有数据，停牌是0就可以红
'                    '如果5日涨跌幅大于等于20% 竞价量比大于等于8%并且今昨量比大于等于100且小于等于500，异动次数小于3，监管类型没数据，停牌是0就可以红，
'                    If gp.Offset(0, 6) = 1 And gp.Offset(0, 3) < 0.2 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'                    If gp.Offset(0, 6) = 1 And gp.Offset(0, 3) >= 0.2 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'                End If
'
'                '3昨日连板天数是0的，如果5日涨跌幅小于10%,竞价量比大于等于8%,今昨量比小于等于500，异动次数小于3，监管类型没有数据，停牌是0就可以红
'                If gp.Offset(0, 6) = 0 And gp.Offset(0, 3) < 0.1 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'            End If
'        Else
'            '1竞价量比大于等于8%并且小于100%, 今昨量比小于等于500，异动次数小于3，监管类型没有数据，停牌是0 就可以红
'            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) <= 1 And gp.Offset(0, 5) <= 500 And gp.Offset(0, 8) < 3 And gp.Offset(0, 9) = "" And gp.Offset(0, 10) < 1 Then gp.Offset(0, -1).Interior.Color = 13421823
'        End If
'
'
'        If gp.Column = 12 Then '如果在第12列，也就是创业版
'            '只要竞价量比大于等于8%，异动次数小于3，监管类型没数据，停牌是0就名称红。
'            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 8) < 3 And gp.Offset(0, 9) = "" And gp.Offset(0, 10) < 1 Then gp.Offset(0, -1).Interior.Color = 13421823
'            '只要移动次数大于等于3或者监管类型有数据或者停牌非0就名称绿
'            If gp.Offset(0, 8) >= 3 Or gp.Offset(0, 9) <> "" Or gp.Offset(0, 10) > 0 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'        Else
'            If qx = "差" Then
'                '如果情绪差，只要竞价量比大于等于8%并且涨跌幅小于0%就股票名称绿。
'                If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 2) < 0 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'                '如果情绪差昨日连板天数大于1，并且竞价量比大于等于8%，就股票名称绿。
'                If gp.Offset(0, 6) > 1 And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'                '如果情绪差，只要竞价未匹配有数值就是名称和竞价未匹配两列都绿;
'                If gp <> "" Then
'                    gp.Offset(0, -1).Interior.ColorIndex = 35
'                    gp.Interior.ColorIndex = 35
'                End If
'                '如果情绪差昨日连板天数大于2的就股票名称绿。
'                If gp.Offset(0, 6) > 2 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'            End If
'        End If
'    Next
    Range("T1_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    For Each gp In Range("T1_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        ' 名称绿色， 竞价未匹配<=0 ， 120日 > 0.25 且 < 0.8 且连板 >0 且 连板是粉色
       ' If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.25 And gp.Offset(0, 8) < 0.8 Then
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 Then
           '' If InStr(gp.Offset(0, 11), "创百日新高") > 0 Or InStr(gp.Offset(0, 11), "反包") > 0 Then
             If InStr(gp.Offset(0, 11), "创百日新高") > 0 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
               ' If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                     gp.Offset(0, -1).Interior.ColorIndex = 46
                    Exit For
                'End If
            End If
        End If
    Next
   
    For Each gp In Range("T2_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        'If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.25 And gp.Offset(0, 8) < 0.8 Then
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.25 Then

            If InStr(gp.Offset(0, 11), "创百日新高") > 0 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
                'If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                     gp.Offset(0, -1).Interior.ColorIndex = 46
                    Exit For
               ' End If
            End If
        End If
    Next
    
    Range("T1_匹配").Sort "4日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "4日涨跌幅", 2, , , , , , 1
    Range("T1_匹配").Sort "昨日连板天数", 2, , , , , , 1
    Range("T2_匹配").Sort "昨日连板天数", 2, , , , , , 1
    
    ' 小于等于5，紫色是需要竞价未匹配小于等于1的， 如果蓝圈的数字大于等于5，紫色不需要需要竞价未匹配小于等于1
    ' 紫色竞价未匹配 设置 1000 就是不需要需要竞价未匹配小于等于1
    Dim zsjjwpp As Integer
    zsjjwpp = 1000
    If Sheet4.Range("H10") <= 5 And qx = "好" Then
        zsjjwpp = 1
    End If
    For Each gp In Range("T1_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        'If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
        ' 非绿，竞价<=0,创百日新高颜色 = 37
        
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= zsjjwpp And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
             'gp.Offset(0, 2).Interior.ColorIndex = 29
            If rng5 = "" Then Set rng5 = gp.Offset(0, 2)
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                Set rng6 = gp.Offset(0, 2)
                Exit For
            End If
        End If
    Next
    
    '昨日连班天数最大，如果有多个昨日连班天数一样大的取这几个昨日连班天数里4日涨跌幅最大的,要非绿的
    If Not rng6 = "" Then
        rng6.Interior.ColorIndex = 29
    ElseIf Not rng5 = "" Then
        rng5.Interior.ColorIndex = 29
    End If
    
    
     For Each gp In Range("T2_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
       ' If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= zsjjwpp And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
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
    
   ' Range("T1_匹配").Sort "4日涨跌幅", 2, , , , , , 1
   ' Range("T2_匹配").Sort "4日涨跌幅", 2, , , , , , 1
    

    
End Sub
Function SortDictionaryByValue(dict10 As Object) As Variant
    Dim keys() As Variant
    keys = dict10.keys
    
    
    Dim i As Long, j As Long
    Dim tempKey As Variant
    
    For i = LBound(keys) To UBound(keys) - 1
        For j = i + 1 To UBound(keys)
            If dict10(keys(i)) < dict10(keys(j)) Then
                tempKey = keys(i)
                keys(i) = keys(j)
                keys(j) = tempKey
            End If
        Next j
    Next i
    
  '  For i = LBound(keys) To UBound(keys) - 1
  '      Debug.Print keys(i)
        
 '   Next i
    
    SortDictionaryByValue = keys
End Function


Sub 补涨()
    Dim rng, lbts, ztlbts As Range
    Dim sb, zsb, jsb, h, i, imax, lbtsss, lbtssszd As Integer
    Dim fd, fd2 As Double
    Dim arr
    Dim gn, outgn, maxgn, fdgn, str, yzgp, gnstrstr, str2 As String
    Dim firstAddress
    gnstrstr = ""
    
    ' 现在源头加一个涨停原因表的首板
    Set rng = Sheet7.Range("a:a").Find("首板")
    jsb = 0 '首板行号
    If Not rng Is Nothing Then jsb = rng.Row + 1
    
    If jsb > 0 Then
        For i = 1 To 256 Step 3
            If Sheet7.Cells(jsb, i) = "" Then Exit For
            gnstrstr = gnstrstr & ";" & Sheet7.Cells(jsb, i)
        Next
    End If
    
    
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
  
    'If sb > 0 And zsb > 0 Then
    If sb > 0 Then
        For i = 1 To 256 Step 3
            If Sheet21.Cells(sb, i) = "" Then Exit For
            '开始对比
           ' Set rng = Sheet21.Rows(zsb).Find(Sheet21.Cells(sb, i), , , 1)
           ' If Not rng Is Nothing Then
            '    If rng.Offset(0, 1) > Sheet21.Cells(sb, i + 1) Then
                   ' Sheet21.Cells(sb, i).Interior.ColorIndex = 35
             '   End If

           ' End If
            '4.找出""昨原因"表首板里非绿的最大股票个数的概念（如果最大股票个数的概念有多个取涨停封单额最大的概念）和最大涨停封单额的概念，填入结果表的补涨里。
            If Sheet21.Cells(sb, i).Interior.ColorIndex <> 35 Then
                Debug.Print Sheet21.Cells(sb, i) & " ---- " & Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1
                
                gnstrstr = gnstrstr & ";" & Sheet21.Cells(sb, i)
'                dict2.Add Sheet21.Cells(sb, i).Value, Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1
'                If imax < Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1 Then
'                    imax = Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1
'                    maxgn = Sheet21.Cells(sb, i)
'                    fd = Sheet21.Cells(sb, i + 1)
'                ElseIf imax = Sheet21.Cells(sb, i).End(xlDown).Row - sb - 1 Then
'                    If fd < Sheet21.Cells(sb, i + 1) Then
'                        maxgn = Sheet21.Cells(sb, i)
'                        fd = Sheet21.Cells(sb, i + 1)
'                    End If
'                    If fd = Sheet21.Cells(sb, i + 1) Then
'                        maxgn = maxgn & ";" & Sheet21.Cells(sb, i)
'                    End If
'                End If
'                If fd2 < Sheet21.Cells(sb, i + 1) Then
'                    fd2 = Sheet21.Cells(sb, i + 1)
'                    fdgn = Sheet21.Cells(sb, i)
'                ElseIf fd2 = Sheet21.Cells(sb, i + 1) Then
'                    fdgn = fdgn & ";" & Sheet21.Cells(sb, i)
'                End If
            End If
        Next
        
'        sortedKeys = SortDictionaryByValue(dict2)
'
'         ' 遇到新股与次新股和国企改革 就找第二梯队的概念
'        If maxgn = "新股与次新股" Or maxgn = "国企改革" Then
'
'
'            secondName = sortedKeys(0)
'
'            If secondName = "新股与次新股" Or secondName = "国企改革" Then
'                secondName = sortedKeys(1)
'
'            End If
'            maxgn = maxgn & ";" & secondName
'        End If
'
'        '相同的最大数量的概念
'        For i = LBound(sortedKeys) + 1 To UBound(sortedKeys)
'            If dict2(sortedKeys(i)) = imax Then
'                 maxgn = maxgn & ";" & sortedKeys(i)
'            End If
'        Next i
        
        Set dict2 = Nothing '关闭字典
    End If
    maxgn = gnstrstr

    
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
    Sheet4.Range("H11").Interior.ColorIndex = xlNone
    
    Range("主创涨停").Sort "连板天数", 2, , , , , , 1
    ' 最大连板天数股票
    lbts = Sheet15.Range("B2")
    '最大连板天数
    lbtsss = Sheet15.Range("G2").Value
    '最大连板天数股票4日涨跌幅
    lbtssszd = 0
    Set rng = Sheet2.Range("b:b").Find(Sheet15.Range("B2"))
    ' 主创涨停4日涨跌幅
    If Not rng Is Nothing Then lbtssszd = rng.Offset(0, 9).Value
    '
    
    Range("表1").Sort "4日涨跌幅", 2, , , , , , 1
     Range("表1").Sort "连板天数", 2, , , , , , 1
    Sheet4.Range("h25") = Sheet2.Range("B2")
    Sheet4.Range("h24") = Sheet2.Range("Z2")
    If InStr(Sheet4.Range("H33"), ";" & Sheet2.Range("B2") & ";") Then
        Sheet4.Range("h25") = Sheet2.Range("B3")
        Sheet4.Range("h24") = Sheet2.Range("z3")
    End If
    
    
    Range("表1").Sort "4日涨跌幅", 2, , , , , , 1
    Range("表1").Sort "昨日连板天数", 2, , , , , , 1
    Set ztlbts = Sheet2.Range("B2")
   ' Set rng = Sheet2.Range("b:b").Find(Sheet4.Range("H33"))
    
    
    
  '  If Sheet4.Range("h3") = "封单开" Then
    
   '     Range("表1").Sort "连板天数", 2, , , , , , 1
   '     Set rng = Sheet2.Range("b:b").Find(Sheet4.Range("H33"))
   '     '改成手动，输入股票名称

   '     If rng.Offset(0, 24) = Sheet2.Range("Z2") Then
  '      'If Sheet28.Range("F2") = Sheet2.Range("Z2") Then
   '         Sheet4.Range("H10") = Sheet2.Range("Z3")
  '          Sheet4.Range("H11") = Sheet2.Range("B3")
  '      Else
  '          Sheet4.Range("H10") = Sheet2.Range("Z2")
 '           Sheet4.Range("H11") = Sheet2.Range("B2")
  '      End If
    
  '  Else
    For i = 2 To 100
        ' 做昨日连板天数 = table1 昨日连板天数
        If InStr(Sheet4.Range("H33"), ";" & Sheet2.Range("B" & i) & ";") Then
        'If Sheet28.Range("E2") = Sheet2.Range("P2") Then
          '  Sheet4.Range("H10") = Sheet2.Range("P3")
          '  Sheet4.Range("H11") = Sheet2.Range("B3")
        Else
            Sheet4.Range("H10") = Sheet2.Range("P" & i)
            Sheet4.Range("H11") = Sheet2.Range("B" & i)
            Exit For
        End If
    Next
 '   End If
    
    Sheet4.Range("H10").Interior.ColorIndex = 35
    If Sheet4.Range("H10") >= 4 Then
        Sheet4.Range("H10").Interior.Color = 13551615
    End If
    
    ' 主创涨停连板天数 = table1连板天数
  '  If lbtsss = Sheet2.Range("P2").Value Then
        ' table1 4日涨跌幅 <=  主创涨停4日涨跌幅
     '   If Sheet2.Range("k2") <= lbtssszd Then
      '      Debug.Print "H11--主创涨停---" & lbts
     '       Sheet4.Range("H11") = lbts
     '   Else
     '       Debug.Print "H11--Table1---" & ztlbts
     '       Sheet4.Range("H11") = ztlbts
     '   End If
      '  Sheet4.Range("H11") = Sheet2.Range("B2")
   ' Else
   '     If Sheet4.Range("h3") = "封单开" Then
   '         Sheet4.Range("H11") = lbts
   '     Else
    '        Sheet4.Range("H11") = ztlbts
    '    End If
   ' End If
    
    Set rng = Sheet2.Range("b:b").Find(Sheet4.Range("H11"))
    If Not rng Is Nothing Then
        If Sheet4.Range("h3") = "封单开" Then
            If rng.Offset(0, 5) < -0.04 Then Sheet4.Range("H11").Interior.ColorIndex = 35
        Else
            If rng.Offset(0, 4) < -0.04 Then Sheet4.Range("H11").Interior.ColorIndex = 35
        End If
    End If
    
    Range("表1").Sort "120日涨跌幅", 2, , , , , , 1
    Sheet4.Range("H12") = Sheet2.Range("B2")
    If Sheet2.Range("k2").Value <= -0.2 Then
        Sheet4.Range("H12").Interior.ColorIndex = 35
    End If
    
    ' 塞力斯模式 就是table1里面120日涨跌幅最大并且昨日自由流通市值大于100亿并且table1的5日涨跌幅大于0
    For Each rng In Range("表1[  代码]")
        '
        If rng.Offset(0, 13) > 0 And rng.Offset(0, 14) / 10000 > 1000000 Then
             Sheet4.Range("H13") = rng.Offset(0, 1)
             Exit For
        End If
    Next
    
    
    
    
    
  '  Set rng = Sheet2.Range("b:b").Find(yzgp)
  '  If Not rng Is Nothing Then
  '      Sheet4.Range("H11") = yzgp
  '      Sheet4.Range("H12") = rng.Offset(0, 9)
  '  End If
    
    '3、在"table1"中找到5日涨跌幅最大的股票，这个例子是尚太科技，用这个股票的所属概念比对昨原因表里的首板的非绿的概念找出相同的概念。
    Set rng = Sheet2.Range("N:N").Find(Evaluate("max(Table1!N:N)"))
    If Not rng Is Nothing Then
        gn = gn & rng.Offset(0, -9)
        '处理风口
        '删除风口
       ' If Left(rng.Offset(0, -13), 5) = "SH.68" Then
       '     Sheet4.Range("H35") = "科创板"
       ' ElseIf Left(rng.Offset(0, -13), 5) = "SZ.30" Then
       '     Sheet4.Range("H35") = "创业板"
       ' Else
       '     Sheet4.Range("H35") = "主板"
       ' End If
    End If
  '  Debug.Print gn
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
  '  str = ";"
  '  arr = Split(outgn & maxgn & ";" & fdgn & ";", ";")
  '  For i = LBound(arr) To UBound(arr)
  '      If arr(i) <> "" Then
  '          If InStr(str, ";" & arr(i) & ";") = 0 Then str = str & arr(i) & ";"
  '      End If
  '  Next
  
    str2 = ""
      
    '如果当天一字板 表是空的，就昨原因里首板的所有概念里非绿的概念加入 结果表的补涨框
   ' If Sheet19.Range("a2") = "" Then
        For i = 1 To 256 Step 3
            If Sheet21.Cells(sb, i) = "" Then Exit For
            '开始对比
            If Sheet21.Cells(sb, i).Interior.ColorIndex <> 35 Then
                If InStr(str2, ";" & Sheet21.Cells(sb, i) & ";") = 0 Then
                    str2 = str2 & Sheet21.Cells(sb, i) & ";"
                End If
            End If
        Next
   ' End If
    
    '所有补涨概念
    fd = 0 '默认封单为关
    If Sheet4.Range("h3") = "封单开" Then fd = 1 '如果封单是开，那么设置fd=1
    str = ";"
    arr = Split(outgn & maxgn & ";" & fdgn & ";" & str2 & ";", ";")
    For i = LBound(arr) To UBound(arr)
        If arr(i) <> "" Then
            If InStr(str, ";" & arr(i) & ";") = 0 Then
                ' 创业板概念 找不到的概念直接加入
                Set gn = Range("创业板概念[所属概念]").Find(arr(i), , , 1)
                If gn Is Nothing Then
                  '  str = str & arr(i) & ";"
                Else
                    If fd = 1 Then
                        ' 封单开， 三列都不是绿的
                        If gn.Offset(0, 4).Interior.ColorIndex <> 35 And gn.Offset(0, 5).Interior.ColorIndex <> 35 And gn.Offset(0, 6).Interior.ColorIndex <> 35 Then
                            str = str & arr(i) & ";"
                        End If
                    Else
                         ' 封单关， 今昨竞封, 跌停封单额 不是绿的
                        If gn.Offset(0, 4).Interior.ColorIndex <> 35 And gn.Offset(0, 6).Interior.ColorIndex <> 35 Then
                            str = str & arr(i) & ";"
                        End If
                    End If
                End If
            End If
        End If
    Next
    

    
    
    Sheet4.Range("h9") = str
    
    '
    '昨标高
End Sub
Sub ystest()
    MsgBox Sheet21.Range("a2").Interior.ColorIndex
End Sub

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

Sub 风口昨首板()
    Dim a As Range
    Dim sb, i As Integer
    Dim gn As String
 
    gn = ";"
    For Each a In Range("创业板概念[所属概念]")
        If a.Interior.Color = 13421823 Or a.Offset(0, 3).Interior.Color = 13421823 Then
            gn = gn & a & ";"
        End If
    Next
    
    Set a = Sheet21.Range("a:a").Find("首板")
    sb = 0 '首板行号
    If Not a Is Nothing Then sb = a.Row + 1
    For i = 1 To 256 Step 3
        If Sheet21.Cells(sb, i) = "" Then Exit For
        If Sheet21.Cells(sb, i).Interior.ColorIndex <> 35 Then gn = gn & Sheet21.Cells(sb, i) & ";"
    Next
    
    Sheet4.Range("H19") = gn
End Sub

Sub test1()
Dim rng As Range
Dim a
    a = Sheet21.Range("a44").End(xlDown).Row
    MsgBox a

End Sub

Sub 条件格式()
    
'    Range("T1_匹配").FormatConditions.Delete
'    Range("T2_匹配").FormatConditions.Delete
    
'    With Union(Range("T1_匹配[竞价量比]"), Range("T2_匹配[竞价量比]")).FormatConditions _
'        .Add(Type:=xlCellValue, Operator:=xlGreater, Formula1:="=0.08")
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
    
'    With Union(Range("T1_匹配[今昨量比]"), Range("T2_匹配[今昨量比]")).FormatConditions _
'        .Add(Type:=xlCellValue, Operator:=xlGreaterEqual, Formula1:="=100")
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Union(Range("T1_匹配[25日涨停次数]"), Range("T2_匹配[25日涨停次数]")).FormatConditions _
'        .Add(Type:=xlCellValue, Operator:=xlLess, Formula1:="=1")
'        .Interior.ColorIndex = 35
'        .Font.ColorIndex = 14
'    End With
    
    
'    With Union(Range("T1_匹配[企业性质]"), Range("T2_匹配[企业性质]")).FormatConditions _
'        .Add(Type:=xlTextString, String:="国资", TextOperator:=xlContains)
'        .Font.Color = -16383844
'    End With
    
'    Range("T1_匹配").AutoFilter Field:=10, Criteria1:="<>*国资*"
'    On Error GoTo line1
'    Range("T1_匹配[企业性质]").SpecialCells(12).ClearContents
'line1:
'    Range("T1_匹配").AutoFilter Field:=10
'
'    Range("T2_匹配").AutoFilter Field:=10, Criteria1:="<>*国资*"
'    On Error GoTo line2
'    Range("T2_匹配[企业性质]").SpecialCells(12).ClearContents
'line2:
'    Range("T2_匹配").AutoFilter Field:=10
'
'===============================================
'    With Range("T1_匹配[25日涨停次数]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T1_匹配[昨日连板天数]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T1_匹配[今昨量比]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T2_匹配[封停板时长]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T2_匹配[25日涨停次数]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T2_匹配[昨日连板天数]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'==========================================
'    With Range("T1_匹配[分时量比]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.ColorIndex = 45
'    End With
'    With Range("T2_匹配[分时量比]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.ColorIndex = 45
'    End With
    'Debug.Print Range("R8").font.colorindex
    
    
'==============================================
'    Dim a As Range
'    For Each a In Range("T1_匹配[竞价量比]")
'        If a >= 0.08 Then
'            a.Interior.Color = 13551615
'            a.Font.Color = -16383844
'            a.Offset(0, -10).Interior.Color = 13551615
'            a.Offset(0, -10).Font.Color = -16383844
'        End If
'        If a >= 1 Then
'            a.Interior.ColorIndex = 35
'            a.Offset(0, -10).Interior.ColorIndex = 35
'        End If
'    Next
'    For Each a In Range("T2_匹配[竞价量比]")
'        If a >= 0.08 Then
'            a.Interior.Color = 13551615
'            a.Font.Color = -16383844
'            a.Offset(0, -10).Interior.Color = 13551615
'            a.Offset(0, -10).Font.Color = -16383844
'        End If
'        If a >= 1 Then
'            a.Interior.ColorIndex = 35
'            a.Offset(0, -10).Interior.ColorIndex = 35
'        End If
'    Next
 '===============================================================
End Sub


Sub 概念分表2()
    Dim a As Range '概念计数单元格
    Dim b As Range '结果表里的匹配单元格
    Dim 概念数, c, r As Integer
    
    '清除上次结果
    Sheet5.Cells.Clear
    Sheet7.Cells.Clear
'    Range("T1_匹配").Sort Header:=xlYes, key1:=Range("T1_匹配[竞价涨幅]"), Order1:=xlDescending
'    Range("T2_匹配").Sort Header:=xlYes, key1:=Range("T2_匹配[竞价涨幅]"), Order1:=xlDescending
    概念数 = -1
    For Each a In Range("创业板概念[实际流通]") '查找所有中标的概念
        If a.Interior.Color <> 16777215 Then '如果不是没有底色的
            概念数 = 概念数 + 1
            c = 概念数 * 4 + 1
            
            '创业板
            r = 3
            Sheet5.Cells(1, c) = a.Offset(0, -2)  '写入概念标题
            Sheet5.Cells(2, c) = "代码"
            Sheet5.Cells(2, c + 1) = "名称"
            Sheet5.Cells(2, c + 2) = "竞价涨幅"
            For Each b In Range("表[所属概念]")
                If Left(b.Offset(0, -4), 5) = "SZ.30" Then
                    If InStr(b, ";" & a.Offset(0, -2) & ";") > 0 Then
                        Sheet5.Cells(r, c) = b.Offset(0, -4)
                        Sheet5.Cells(r, c + 1) = b.Offset(0, -3)
                        Sheet5.Cells(r, c + 2) = b.Offset(0, 1)
                        'If Sheet5.Cells(r, c + 2) > 0.01 Then Sheet5.Cells(r, c + 2).Interior.Color = 13421823
                        r = r + 1
                    End If
                End If
            Next
        End If
        Sheet5.Columns(c + 2).NumberFormatLocal = "0.00%"
    Next
            '主板
    概念数 = -1
    For Each a In Range("主板概念[实际流通]") '查找所有中标的概念
        If a.Interior.Color <> 16777215 Then '如果不是没有底色的
            概念数 = 概念数 + 1
            c = 概念数 * 4 + 1
            
            '创业板
            r = 3
            Sheet7.Cells(1, c) = a.Offset(0, -2)  '写入概念标题
            Sheet7.Cells(2, c) = "代码"
            Sheet7.Cells(2, c + 1) = "名称"
            Sheet7.Cells(2, c + 2) = "竞价涨幅"
            For Each b In Range("表[所属概念]")
                If Left(b.Offset(0, -4), 5) = "SZ.30" Then
                    If InStr(b, ";" & a.Offset(0, -2) & ";") > 0 Then
                        Sheet7.Cells(r, c) = b.Offset(0, -4)
                        Sheet7.Cells(r, c + 1) = b.Offset(0, -3)
                        Sheet7.Cells(r, c + 2) = b.Offset(0, 1)
                        'If Sheet5.Cells(r, c + 2) > 0.01 Then Sheet5.Cells(r, c + 2).Interior.Color = 13421823
                        r = r + 1
                    End If
                End If
            Next
            Sheet7.Columns(c + 2).NumberFormatLocal = "0.00%"
        End If
    Next

    
    'MsgBox "概念分表完成!"
End Sub

Sub 个股查询()
    Dim tj, gn1 As String
    Dim rng, gn As Range
    Application.ScreenUpdating = False
    '先去掉以前的颜色
    Range("创业板概念[计数]").Interior.Pattern = xlNone
    'Range("主板概念[计数]").Interior.Pattern = xlNone
    Sheet4.Range("H30").Interior.Pattern = xlNone
    'tj = InputBox("请输入股票名称")
    tj = Sheet4.Range("H30")
    If tj = "" Then Exit Sub
    '查询这个股票的概念
    gn1 = ""
    Set rng = Range("表1[    名称]").Find(tj)
    If rng Is Nothing Then Set rng = Range("表2[    名称]").Find(tj)
    If Not rng Is Nothing Then
        gn1 = rng.Offset(0, 3)
        If rng.Offset(0, 5) < 1 Then Sheet4.Range("H30").Interior.ColorIndex = 35
    End If
    If Sheet4.Range("H30").Interior.ColorIndex <> 35 Then
        Set rng = Range("T1_匹配[    名称]").Find(tj)
        If rng Is Nothing Then Set rng = Range("T2_匹配[    名称]").Find(tj)
        If rng Is Nothing Then Sheet4.Range("H30").Interior.ColorIndex = 35
    End If
    
    '匹配这些概念
    For Each gn In Range("创业板概念[所属概念]")
        If InStr(gn1, ";" & gn & ";") > 0 Then gn.Offset(0, 1).Interior.ColorIndex = 22
    Next
'    For Each gn In Range("主板概念[所属概念]")
'        If InStr(gn1, ";" & gn & ";") > 0 Then gn.Offset(0, 1).Interior.ColorIndex = 22
'    Next
    Application.ScreenUpdating = True
End Sub

