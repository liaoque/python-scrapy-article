from polls.core import concept, gn
from collections import Counter

"""
Sub 生成所属概念()
    Debug.Print Now & "生成所属概念"
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
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
    'Debug.Print str_cy
    '概念长字符串拆分成数组
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '概念数组转字典去重
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            'If InStr(nogn, ";" & arr(i) & ";") < 1 Then '去掉不要的概念
                'If arr(i) <> "" Then
                    If Not dic.exists(arr(i)) Then
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
                If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35  '小于等于0的变绿
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
                    If rng.Offset(0, 1) > a.Offset(0, 4) Then a.Offset(0, 4).Interior.ColorIndex = 35 '昨比今大变绿
                    a.Offset(0, 4) = a.Offset(0, 4) & " | " & rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 4) = a.Offset(0, 4) & " | 0"
                End If
                
                'a.Offset(0, 4) = lz '把股票个数输出到概念后的第四列
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        Next
    End If
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
            'a.Offset(0, 2) = Evaluate("round(AVERAGEIFS(表[竞价涨幅],表[所属概念],""*;" & a & ";*""),4)")
            a.Offset(0, 2) = Evaluate("round(SUMIFS(表1[昨日自由流通市值],表1[所属概念],""*;" & a & ";*"")/100000000,2)")
            'If a.Offset(0, 2) < 9000 Then a.Offset(0, 3).Interior.ColorIndex = 35
        'Else
            'a.Offset(0, 2) = "-"
        End If
    Next
End Sub
"""


def suo_shu_gai_nian(data1, data2, today, yesterday, fd=0):
    if "yuan_yin" not in yesterday:
        return []

    xia_xian = concept.xia_xian()
    gns = []
    for code, item in data2.items():
        if item["code"][0:5] == "SZ.30" or item["code"][0:6] == "SZ.688" or item["code"][0:6] == "SZ.689":
            if item['jingjiazhangfutoday'] > xia_xian["chuang_ye_set"]:
                gns.extend(item["suoshugainian"])
        else:
            if item['jingjiazhangfutoday'] > xia_xian["zhu_set"]:
                gns.extend(item["suoshugainian"])

    gns = list(set(gns))
    gn_dict = {}
    for gn in gns:
        gn_dict[gn] = {
            "chuang_bai_ri_xin_gao": {
                "today": 0,
                "yesterday": 0,
                "power": 0,
            },
            "liu_tong_shi_zhi": 0,

            "jin_jing_feng": {
                "today": 0,
                "yesterday": 0,
                "count": 0,
                "power": 0,
            },
            "zhang_ting_da_rou": {
                "wei_pi_pei": 0,
                "power": 0,
                "feng_dan_power": 0,
                "feng_dan": 0,
            },
            "die_ting_da_mian": {
                "jin_jia": 0,
                "power": 0,
                "feng_dan_power": 0,
                "feng_dan": 0,
            },

        }

        # 创百日新高
        # 计算创百日新高里面，每个概念对应的股票数量
        if gn in today["yuan_yin"]["chuang_bai_ri_xin_gao_sort"]:
            gn_dict[gn]["chuang_bai_ri_xin_gao"]["today"] = today["yuan_yin"]["chuang_bai_ri_xin_gao_sort"][gn]["count"]
            if gn in yesterday["yuan_yin"]["chuang_bai_ri_xin_gao_sort"]:
                gn_dict[gn]["chuang_bai_ri_xin_gao"]["yesterday"] = \
                    yesterday["yuan_yin"]["chuang_bai_ri_xin_gao_sort"][gn]["count"]

            # 涨停概念对应股票少于昨天的, 说明比昨天的弱
            if gn_dict[gn]["chuang_bai_ri_xin_gao"]["today"] < gn_dict[gn]["chuang_bai_ri_xin_gao"]["yesterday"]:
                gn_dict[gn]["chuang_bai_ri_xin_gao"]["power"] = -1

        # 一字板
        # 计算一字板概念里面，每个概念对应的股票数量， 竞价未匹配数量
        if gn in today["yuan_yin"]["yi_zi_ban_sort"]:
            gn_dict[gn]["jin_jing_feng"]["today"] = today["yuan_yin"]["yi_zi_ban_sort"][gn][
                "gai_nian_jing_jia_wei_pi_pei"]

            gn_dict[gn]["jin_jing_feng"]["count"] = today["yuan_yin"]["yi_zi_ban_sort"][gn]["count"]
            if gn in yesterday["yuan_yin"]["yi_zi_ban_sort"]:
                gn_dict[gn]["jin_jing_feng"]["yesterday"] = yesterday["yuan_yin"]["yi_zi_ban_sort"][gn][
                    "gai_nian_jing_jia_wei_pi_pei"]
            # 竞价未匹配<0 弱
            if gn_dict[gn]["jin_jing_feng"]["today"] < 0:
                gn_dict[gn]["jin_jing_feng"]["power"] = -1
            # 竞价未匹配<昨天 弱
            if gn_dict[gn]["jin_jing_feng"]["today"] < gn_dict[gn]["jin_jing_feng"]["yesterday"]:
                gn_dict[gn]["jin_jing_feng"]["power"] = -1

        # 跌停大面
        # 计算跌停概念里面，每个概念对应， 竞价未匹配数量
        if gn in today["yuan_yin"]["die_ting_sort"]:
            gn_dict[gn]["die_ting_da_mian"]["jin_jia"] = today["yuan_yin"]["die_ting_sort"][gn][
                "gai_nian_jing_jia_wei_pi_pei"]

            if gn_dict[gn]["die_ting_da_mian"]["jin_jia"] > 0:
                gn_dict[gn]["die_ting_da_mian"]["jin_jia"] = 0
            else:
                gn_dict[gn]["die_ting_da_mian"]["jin_jia"] = abs(gn_dict[gn]["die_ting_da_mian"]["jin_jia"])

            # 跌停未匹配 大于 今天的未匹配  弱
            if gn_dict[gn]["die_ting_da_mian"]["jin_jia"] > gn_dict[gn]["jin_jing_feng"]["today"]:
                gn_dict[gn]["die_ting_da_mian"]["power"] = -1

            gn_dict[gn]["die_ting_da_mian"]["feng_dan"] = sum(
                [x["dietingfengdane"] for x in today["yuan_yin"]["die_ting_sort"][gn]["gai_nian_gu_piao"]])

            if gn_dict[gn]["die_ting_da_mian"]["feng_dan"] > gn_dict[gn]["zhang_ting_da_rou"]["feng_dan"]:
                gn_dict[gn]["die_ting_da_mian"]["feng_dan_power"] = -1

        # 涨停大肉, 涨停股票数，封单金额
        if gn in today["yuan_yin"]["lian_zhang_sort"]:
            gn_dict[gn]["zhang_ting_da_rou"]["count"] = today["yuan_yin"]["lian_zhang_sort"][gn]["count"]
            gn_dict[gn]["zhang_ting_da_rou"]["jin_jia"] = today["yuan_yin"]["lian_zhang_sort"][gn][
                "gai_nian_jing_jia_wei_pi_pei"]
            if gn_dict[gn]["zhang_ting_da_rou"]["count"] < 1:
                gn_dict[gn]["zhang_ting_da_rou"]["power"] = -1

            gn_dict[gn]["zhang_ting_da_rou"]["feng_dan"] = sum(
                [x["zhangtingfengdanetoday"] for x in today["yuan_yin"]["lian_zhang_sort"][gn]["gai_nian_gu_piao"]])

            if gn_dict[gn]["zhang_ting_da_rou"]["feng_dan"] < gn_dict[gn]["jin_jing_feng"]["today"]:
                gn_dict[gn]["zhang_ting_da_rou"]["feng_dan_power"] = -1
            elif gn_dict[gn]["zhang_ting_da_rou"]["feng_dan"] > 0:
                gn_dict[gn]["jin_jing_feng"]["power"] = 0

        # 创百日新高， 和 今天封单 非弱
        if gn_dict[gn]["chuang_bai_ri_xin_gao"]["power"] != -1 and gn_dict[gn]["jin_jing_feng"]["power"] != -1:
            # 昨日流通市值
            gn_dict[gn]["liu_tong_shi_zhi"] = sum(
                item["ziyouliutongshizhiyesterday"] for code, item in data1.items() if "suoshugainian" in item)

    return gai_nian_biao_shang_se(gn_dict)


"""
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
"""


def gai_nian_biao_shang_se(gn_dict):
    imax = 0
    isred = 0
    for (gn, item) in gn_dict.items():
        if isred == 0:
            imax = item["jin_jing_feng"]["count"]

        if (item["jin_jing_feng"]["power"] != -1 and item["zhang_ting_da_rou"]["power"] != -1 and
                item["die_ting_da_mian"]["power"] != -1 and item["jin_jing_feng"]["count"] == imax):
            item["jin_jing_feng"]["power"] = 1
            isred = 1

    # 找到百日新高最大的， 然后power 改成1
    maxd = max(gn_dict.items(), key=lambda x: x[1]["chuang_bai_ri_xin_gao"]["today"])
    gn_dict[maxd[0]]["chuang_bai_ri_xin_gao"]["power"] = 1
    return gn_dict
