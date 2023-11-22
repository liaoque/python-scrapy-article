from dvadmin.wb.core import concept, gn
from dvadmin.wb.utils import gp
from dvadmin.wb.config import code_config

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


def tag_zhangting_dieting(data):
    data2 = {}
    xia_xian = code_config.CodeConfig().getCodeConfig()
    fd = xia_xian['fd']
    for (code, items) in data.items():

        items["qushi"] = 0
        if fd == 0:
            # 竞价涨幅
            if items["jingjiazhangfutoday"] / 100 >= 0.05:
                items["qushi"] = 1
            elif items["jingjiazhangfutoday"] / 100 < -0.095:
                items["qushi"] = -1
        else:
            # 涨跌幅
            if items["zhangdiefuqianfuquantoday"] / 100 >= 0.095:
                items["qushi"] = 1
            elif items["zhangdiefuqianfuquantoday"] / 100 < -0.095:
                items["qushi"] = -1

            if items['shoupanjiatoday'] != 0:
                # (收盘价-最低价)/收盘价 > 0.095
                # if (items['shoupanjiatoday'] - items["lowestpricetoday"]) / items['shoupanjiatoday'] > 0.095:
                #     items["qushi"] = "涨停大肉"
                # 最高价-收盘价)/收盘价 > 0.095
                if items["qushi"] == 0 and (items["higestpricetoday"] - items['shoupanjiatoday']) / items[
                    'shoupanjiatoday'] > 0.095:
                    items["qushi"] = -1
        data2[code] = items

    return data2


def tag_all(table1, data):
    if table1 is None:
        return data
    # 炸板
    data = tag_zha_ban(table1, data)
    data = tag_chuang_bai_ri_xin_gao(table1, data)
    data = tag_yi_zi_ban(table1, data)
    data = tag_yi_die_ting(table1, data)
    data = tag_shou_ban(table1, data)
    data = tag_yi_dong(table1, data)
    data = tag_n10(table1, data)
    data = tag_n20(table1, data)
    data = tag_zhu_xian_yuan(table1, data)

    return data


def tag_zha_ban(table1, data):
    for code, item in data.items():
        data[code]["zha_ban"] = 0

    if "JinCengZhangTing" not in table1:
        return data

    data2 = table1["JinCengZhangTing"]
    for items in data2:

        code2 = gp.getCode(items["code"])
        if code2 not in data:
            continue
        data[code2]["zha_ban"] = 1
    return data


def tag_chuang_bai_ri_xin_gao(table1, data):
    if "ChuangBaiRiXinGao" not in table1:
        return data

    for code, item in data.items():
        data[code]["chuang_bai_ri_xin_gao"] = 0

    data2 = table1["ChuangBaiRiXinGao"]
    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["chuang_bai_ri_xin_gao"] = 1
    return data

def tag_yi_die_ting(table1, data):
    if "YiZiDieTing" not in table1:
        return data
    data2 = table1["YiZiDieTing"]
    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["jingjiaweipipeijinetoday"] = items["jingjiaweipipeijine"]

    return data

def tag_yi_zi_ban(table1, data):
    if "YiZiBan" not in table1:
        return data

    for code, item in data.items():
        data[code]["jingjiaweipipeijinetoday"] = 0
        data[code]["yi_zi_ban"] = 0

    data2 = table1["YiZiBan"]
    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["jingjiaweipipeijinetoday"] = items["jingjiaweipipeijinetoday"]
        data[code]["yi_zi_ban"] = 1
    return data


# 取首板（连板天数为1）的股票涨停封单额
def tag_shou_ban(table1, data):
    if "ZhuChuangZhangTing" not in table1:
        return data

    for code, item in data.items():
        data[code]["zhangtingfengdanetoday"] = 0
        data[code]["zhu_chuang_zhang_ting"] = 0
        data[code]["shou_ban"] = 0
        # data[code]["lianbantianshuyesterday"] = 0
        data[code]["lianbantianshutoday"] = 0

    data2 = table1["ZhuChuangZhangTing"]
    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["zhu_chuang_zhang_ting"] = 1
        data[code]["lian_ban_tian_shu"] = items["code"]
        data[code]["zhangtingfengdanetoday"] = float(items["zhangtingfengdanetoday"])
        data[code]["lianbantianshuyesterday"] = items["lianbantianshuyesterday"]
        data[code]["lianbantianshutoday"] = items["lianbantianshutoday"]
        if items["lianbantianshutoday"] != 1:
            continue
        data[code]["shou_ban"] = 1

    return data


# 取异动
def tag_yi_dong(table1, data):
    if "YiDong" not in table1:
        return data

    for code, item in data.items():
        data[code]["jianguanleixingyesterday"] = ""
        data[code]["lianxuzhangtingtianshuyesterday"] = 0
        data[code]["yidongcishu"] = 0
        data[code]["yi_dong"] = 0

    data2 = table1["YiDong"]

    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["jianguanleixingyesterday"] = items["jianguanleixingyesterday"]
        data[code]["lianxuzhangtingtianshuyesterday"] = items["lianxuzhangtingtianshuyesterday"]
        data[code]["yidongcishu"] = data[code]["yidongcishu"] + 1
        data[code]["yi_dong"] = 1

    return data


# 取异动
def tag_yi_zi_die_ting(table1, data):
    if "YiZiDieTing" not in table1:
        return data

    for code, item in data.items():
        data[code]["jingjiaweipipeijinetoday"] = 0
        data[code]["yi_zi_die_ting"] = 0

    data2 = table1["YiZiDieTing"]

    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["jingjiaweipipeijinetoday"] = items["jingjiaweipipeijinetoday"]
        data[code]["yi_zi_die_ting"] = 1

    return data


# 取n10
def tag_n10(table1, data):
    if "N10" not in table1:
        return data

    for code, item in data.items():
        data[code]["n"] = 0
        data[code]["N_zuocengzhangting"] = 0

    data2 = table1["N10"]

    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["n"] = 1
        if "zuocengzhangting" in items and items["zuocengzhangting"] == "曾涨停":
            data[code]["N_zuocengzhangting"] = 1

    return data


# 取n20
def tag_n20(table1, data):
    if "N20" not in table1:
        return data

    for code, item in data.items():
        data[code]["n"] = 0
        data[code]["N_zuidazhangfu"] = 0

    data2 = table1["N20"]

    for items in data2:
        code = gp.getCode(items["code"])
        if code not in data:
            continue
        data[code]["n"] = 1
        if "zuidazhangfu" in items and items["zuidazhangfu"] > 0:
            data[code]["N_zuidazhangfu"] = items["zuidazhangfu"]

    return data


def tag_zhu_xian_yuan(table1, data):
    if "ZhuXianYuan" not in table1:
        return data

    for code, item in data.items():
        data[code]["n"] = 0
        data[code]["zhu_xian_yuan"] = 0
        data[code]["z_zhangfu10"] = 0
        data[code]["z_zhangfu30"] = 0

    data2 = table1["ZhuXianYuan"]

    for items in data2:
        code = gp.getCode(items["code"])
        if code in data:
            data[code]["zhu_xian_yuan"] = 1
            if "zhangfu10" in items and items["zhangfu10"] > 0:
                data[code]["z_zhangfu10"] = items["zhangfu10"]
            if "zhangfu30" in items and items["zhangfu30"] > 0:
                data[code]["z_zhangfu30"] = items["zhangfu30"]

    return data
