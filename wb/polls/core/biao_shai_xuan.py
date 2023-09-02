"""
Sub 表筛选()
    Debug.Print Now & "表筛选"
    Dim h1, h2, yd, i As Integer
    Dim a As Range
    Dim arr
    Dim firstAddress
    On Error Resume Next

    ActiveSheet.ListObjects("T1_匹配").Unlist
    ActiveSheet.ListObjects("T2_匹配").Unlist
    Dim rng As Range
    Dim rng1 As Range
    Sheet4.Range("i2:au1048576").Clear
    h1 = 1
    For Each a In Range("创业板概念[所属概念]")
        If a.Interior.Color = 13421823 Or a.Offset(0, 3).Interior.Color = 13421823 Then
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
    Next
    
    Sheet4.Range("am1") = h1
    Sheet4.Range("ar1") = h1


    If h1 > 1 Then
        Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("an1:ap" & h1), Sheet4.Range("j1:s1")
        Range("表1[#ALL]").AdvancedFilter 2, Sheet4.Range("as1:au" & h1), Sheet4.Range("x1:ag1")
    End If
    
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("j1").CurrentRegion, , xlYes).Name = "T1_匹配"
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("x1").CurrentRegion, , xlYes).Name = "T2_匹配"
    Range("T1_匹配").Sort "4日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "4日涨跌幅", 2, , , , , , 1
    yd = Sheet18.Range("a1").End(xlDown).Row '异动表行数
    For Each rng In Range("T1_匹配[  代码]")
        rng.Offset(0, 10) = Evaluate("COUNTIFS(异动!A:A," " " & rng & " " ",异动!J:J," " 连续* " " ) ")
        Set rng1 = Sheet18.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then
            firstAddress = rng1.Address
            Do
                If rng1.Offset(0, 6) <> "" Then
                    rng.Offset(0, 11) = rng1.Offset(0, 6)
                    Exit Do
                End If
                Set rng1 = Sheet18.Range("A:A").FindNext(rng1)
            Loop While Not rng1 Is Nothing And rng1.Address <> firstAddress
        End If
        Set rng1 = Sheet14.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then rng.Offset(0, 12) = "创百日新高"
        
        Set rng1 = Sheet24.Range("A:A").Find(rng.Value)
        
         If Not rng1 Is Nothing Then
            rng.Offset(0, 12).Interior.ColorIndex = 37
            If rng1.Offset(0, 5) > 0 Then rng.Offset(0, 8).Interior.ColorIndex = 38
        End If
    Next
    
    For Each rng In Range("T2_匹配[  代码]")
        
        rng.Offset(0, 10) = Evaluate("COUNTIFS(异动!A:A," " " & rng &  " " ",异动!J:J," " 连续* " ")")
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
            rng.Offset(0, 12).Interior.ColorIndex = 28
            If rng1.Offset(0, 6) = "曾涨停" Then rng.Offset(0, 8).Interior.ColorIndex = 38
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
"""


def biao_shai_xuan(d, data1):
    chuang_gn = [gn for (gn, item) in d["chuang_ye_ban_gn"].items() if
                 item["jin_jing_feng"]["power"] == 1 or item["jin_jing_feng"]["chuang_bai_ri_xin_gao"] == 1]
    zhu_gn = d["bu_zhang_data"]["gn"]

    chuang_data = filter(lambda x: len([set(x[1]["suoshugainian"]) | set(chuang_gn)]) > 0, data1.items())
    chuang_data = sorted(chuang_data, key=lambda x: x[1]["zhangdie4thday"], reverse=True)

    chuang_data = {key: value for key, value in chuang_data}

    zhu_data = filter(lambda x: len([set(x[1]["suoshugainian"]) | set(zhu_gn)]) > 0, data1.items())
    zhu_data = sorted(zhu_data, key=lambda x: x[1]["zhangdie4thday"], reverse=True)
    zhu_data = {key: value for key, value in zhu_data}

    return {
        "chuang_gn": chuang_gn,
        "zhu_gn": zhu_gn,
        "chuang_data": chuang_data,
        "zhu_data": zhu_data,
    }
