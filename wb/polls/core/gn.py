import openpyxl
from polls.core import concept

"""
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
"""


def gn_merge(data, path="data.xlsx"):
    # 打开 Excel 文件
    workbook = openpyxl.load_workbook(path)

    # 选择工作表（可以根据工作表名称或索引来选择）
    sheet = workbook['Table3']

    data2 = {}
    for row in sheet.iter_rows(min_row=1, values_only=True):
        code = row[0]
        if code == "代码":
            continue
        data2[code] = row

    # 遍历行
    for (code, item) in data.items():
        if "suoshugainian" in item and isinstance(item["suoshugainian"], list):
            suoshugainian = item["suoshugainian"]
            suoshuhangye = item["suoshuhangye"].split("-")[1:2]
        else:

            if "belongtogainian" in item:
                suoshugainian = item["belongtogainian"].split(";")
                suoshuhangye = item["belongtohangye"].split("-")[1:2]
                del item["belongtogainian"]
                del item["belongtohangye"]
            else:
                suoshugainian = item["suoshugainian"].split(";")
                suoshuhangye = item["suoshuhangye"].split("-")[1:2]


        if code  in data2:
            gn = data2[code][2]
            suoshugainian2 = gn.split(",")
            suoshugainian2.extend(suoshuhangye)
            suoshugainian.extend(suoshugainian2)


        item["suoshugainian"] = concept.filter1(suoshugainian)
        a = item["suoshugainian"]
        a = ["电力" if x == "电力设备" else x for x in a]
        a = ["电力" if x == "电力物联网" else x for x in a]
        a = ["零售" if x == "新零售" else x for x in a]
        a = ["电力" if x == "风电" else x for x in a]
        # a = ["电力" if x == "风电" else x for x in a]
        a = ["国企改革" if x == "央企国资改革" else x for x in a]
        a = ["国企改革" if x == "地方国资改革" else x for x in a]
        a = ["新股与次新股" if x == "开板次新" else x for x in a]
        a = ["新股与次新股" if x == "次新股" else x for x in a]
        a = ["新股与次新股" if x == "核准制次新股" else x for x in a]
        a = [x.replace("概念", "") if x.find("概念") > 0 else x for x in a]
        item["suoshugainian"] = list(set(["新股与次新股" if x == "注册制次新股" else x for x in a]))

        data[code] = item

    return data
