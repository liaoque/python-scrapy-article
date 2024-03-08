from dvadmin.wb.config import code_config
"""
Sub 主线()

    Dim t, t1, t0
    Dim gp, ngp As Range
    Dim dic, dic2, dic3, dic4 As Object
    Set dic = CreateObject("scripting.dictionary")
    Set dic2 = CreateObject("scripting.dictionary")
    Set dic3 = CreateObject("scripting.dictionary")
    Set dic4 = CreateObject("scripting.dictionary")
    Dim nogn As String
    Dim arr() As String
    Dim arr2() As String
        t = Timer


    nogn2 = Sheet4.Range("h39")

    Sheet25.Cells.Clear


    h = Sheet23.Range("a1").End(xlDown).Row
    For i = 2 To h
        Set ngp = Sheet23.Range("a" & i)
        Set rng = Range("表1[  代码]").Find(ngp, , , 1)

        If Not rng Is Nothing Then
          '  rng.Offset(0, 24) = "N10"
            ngp.Offset(0, 3) = rng.Offset(0, 4)
        End If
    Next
'
'    For Each gp In Sheet23.Range("D:D")
'
'        If gp <> "所属概念" And gp <> "" Then
'            nogn = gp.Value
'
'            arr2 = Split(nogn, ";")
'
'
'            For i = LBound(arr2) To UBound(arr2)
'                If Not dic4.Exists(arr2(i)) Then
'                    dic4(arr2(i)) = True
'                End If
'            Next i
'
'
'            i = 1
'            ReDim arr(1 To dic4.Count)
'            For Each Key In dic4.keys
'                arr(i) = Key
'                i = i + 1
'            Next Key
'            dic4.RemoveAll
'
'            For i = LBound(arr) To UBound(arr)
'               If arr(i) <> "" And InStr(nogn2, ";" & arr(i) & ";") = 0 And arr(i) <> "所属概念" Then
'                  If Not dic.Exists(arr(i)) Then
'                      dic(arr(i)) = 1
'                  Else
'                      dic(arr(i)) = dic(arr(i)) + 1
'                  End If
'
'               End If
'            Next i
'
'        End If
'
'    Next gp


    h = Sheet24.Range("a1").End(xlDown).Row
    For i = 2 To h
        Set ngp = Sheet24.Range("a" & i)
        Set rng = Range("表1[  代码]").Find(ngp, , , 1)

        If Not rng Is Nothing Then
         '   rng.Offset(0, 24) = "N20"
            ngp.Offset(0, 3) = rng.Offset(0, 4)
        End If
    Next


    For Each gp In Sheet26.Range("A:A")

        If gp <> "  代码" And gp <> "" Then
            Set rng = Range("表1[  代码]").Find(gp, , , 1)
            If rng Is Nothing Then
               Debug.Print "~~~" & gp

            End If

            If Not rng Is Nothing Then
               nogn = rng.Offset(0, 4).Value
                arr2 = Split(nogn, ";")
                For i = LBound(arr2) To UBound(arr2)
                    If Not dic4.Exists(arr2(i)) Then
                        dic4(arr2(i)) = True
                    End If
                Next i


                i = 1
                ReDim arr(1 To dic4.Count)
                For Each Key In dic4.keys
                    arr(i) = Key
                    i = i + 1
                Next Key
                dic4.RemoveAll

                For i = LBound(arr) To UBound(arr)
                   If arr(i) <> "" And InStr(nogn2, ";" & arr(i) & ";") = 0 And arr(i) <> "所属概念" Then
                      If Not dic.Exists(arr(i)) Then
                          dic(arr(i)) = 1
                      Else
                          dic(arr(i)) = dic(arr(i)) + 1
                      End If

                   End If
                Next i


            End If

        End If

    Next gp



    Sheet25.Range("a1") = "所属概念"
    Sheet25.Range("b1") = "数量"
    If dic.Count > 0 Then
        Sheet25.Range("a2").Resize(dic.Count) = Application.Transpose(dic.keys)
        Sheet25.Range("b2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
        Sheet25.Range("a:h").Sort "数量", 2, , , , , , 1
    End If

End Sub





"""

"""
返回 
概念1： 次数
概念2： 次数
"""


def zhuxian(data):
    data2 = data.items()
    xia_xian = code_config.CodeConfig().getCodeConfig()
    fd = xia_xian['fd']

    if fd == 1:
        suoshugainian = [item['suoshugainian'] for (code, item) in data2 if item['zhu_chuang_zhang_ting'] == 1 ]
    else:
        suoshugainian = [item['suoshugainian'] for (code, item) in data2 if (item['jingjiaweipipeijinetoday'] > 0 and item['yi_zi_ban'] == 1) or item['lianbantianshuyesterday'] > 0]

    # suoshugainian = [item['suoshugainian'] for (code, item) in data2 if item['zhu_xian_yuan'] == 1]

    suoshugainian = [it for item in suoshugainian for it in item]
    unique_array = list(set(suoshugainian))

    unique_array = [{
        'gn': it,
        'c': suoshugainian.count(it)
    } for it in unique_array]
    # data = sorted(data, key=lambda x: x['count'], reverse=True)
    unique_array = sorted(unique_array, key=lambda x: x['c'], reverse=True)
    return unique_array


def zhuxian2(data):
    data2 = data.items()
    suoshugainian = [item['suoshugainian'] for (code, item) in data2 if item['zhu_xian_yuan'] == 1]
    suoshugainian = [it for item in suoshugainian for it in item]
    unique_array = list(set(suoshugainian))

    unique_array = [{
        'gn': it,
        'c': suoshugainian.count(it)
    } for it in unique_array]
    # data = sorted(data, key=lambda x: x['count'], reverse=True)
    unique_array = sorted(unique_array, key=lambda x: x['c'], reverse=True)
    return unique_array