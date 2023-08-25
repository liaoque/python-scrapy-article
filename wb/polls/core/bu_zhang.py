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
    Sheet4.Range("h9") = str
    昨标高
End Sub
"""
def bu_zhang(data, yeasterday, yester_yesterday):
    imax = 0 # 最多概念
    maxgn = [] # 最大概念
    fd = 0 #封单
    fd2 = 0 # 封单2
    fdgn = 0 # 封单概念
    for item2 in yeaster["shou_ban_sort"]:
        item2["color"] = 0
        for item in yester_yesterday["shou_ban_sort"]:
            if item2["suoshugainian"] == item["suoshugainian"] and item["gai_nian_jing_jia_wei_pi_pei"] > item2["gai_nian_jing_jia_wei_pi_pei"]:
                item2["color"] = 35
        
        if item2["color"] != 35:
            if imax < len(item2["gai_nian_gu_piao"]):
            
                imax = len(item2["gai_nian_gu_piao"])
                maxgn.append(item2["suoshugainian"])
                fd = item2["jingjiaweipipeijinetoday"]
                
            elif imax == len(item2["gai_nian_gu_piao"]):
            
                if fd < item2["jingjiaweipipeijinetoday"]:
                    maxgn.append(item2["suoshugainian"])
                    fd = item2["jingjiaweipipeijinetoday"]
                elif fd == item2["jingjiaweipipeijinetoday"]:
                    maxgn.append(item2["suoshugainian"])
            
        if fd2 < item2["jingjiaweipipeijinetoday"]:
            fdgn.append(item2["suoshugainian"])
            fd2 = item2["jingjiaweipipeijinetoday"]
        elif fd2 == item2["jingjiaweipipeijinetoday"]:
            fdgn.append(item2["suoshugainian"])
            
            
    gn = []
    outgn = ";"
    yzgp = "" #阈值股票名
    if yeasterday["day_5_sort"]["zhu_ban"]["zhangfu5"] != -1000:
        gn = (yeasterday["day_5_sort"]["zhu_ban"]["suoshugainian"])
        fd = yeasterday["day_5_sort"]["zhu_ban"]["zhangfu5"]
        yzgp = yeasterday["day_5_sort"]["zhu_ban"]["code"]
        
    if yeasterday["day_5_sort"]["chuang_ye_ban"]["zhangfu5"] != -1000:
        if fd < yeasterday["day_5_sort"]["chuang_ye_ban"]["zhangfu5"]:
            fd = yeasterday["day_5_sort"]["chuang_ye_ban"]["zhangfu5"]
            gn = (yeasterday["day_5_sort"]["chuang_ye_ban"]["suoshugainian"])
            yzgp = yeasterday["day_5_sort"]["chuang_ye_ban"]["code"]
            
    if yeasterday["day_5_sort"]["ke_chuang_ban"]["zhangfu5"] != -1000:
        if fd < yeasterday["day_5_sort"]["ke_chuang_ban"]["zhangfu5"]:
            fd = yeasterday["day_5_sort"]["ke_chuang_ban"]["zhangfu5"]
            gn = (yeasterday["day_5_sort"]["ke_chuang_ban"]["suoshugainian"])
            yzgp = yeasterday["day_5_sort"]["ke_chuang_ban"]["code"]
    
    # 取出阈值股票的5日涨幅
    yzcode  = {}
    for x in data:
        if x["code"] == yzgp:
            yzcode = x
            break
    
    # '3、在"table1"中找到5日涨跌幅最大的股票，这个例子是尚太科技，用这个股票的所属概念比对昨原因表里的首板的非绿的概念找出相同的概念。
    
    max_code = max([x["zhangfu5"] for x in data])
    gn.extend(max_code["suoshugainian"])
    for item2 in yeaster["shou_ban_sort"]:
        gn.append(item2["suoshugainian"])
    
    gn.extend(maxgn)
    gn.extend(fdgn)
    
    return {
        "yzcode": yzcode,
        "gn":gn,
    }