"""
Sub 匹配概念()
    Debug.Print Now & "匹配概念"
    Dim gp, rng, rng3, rng4, rng5, rng6, rng7 As Range
    Dim temp, qx As String
    Dim js, i, h As Integer
    Dim yz, imax1, imax2, imin1, imin2, ijjlb1, ijjlb2, ijzlb1, ijzlb2 As Double
    qx = Sheet4.Range("H6")
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
        For i = 2 To Sheet4.Range("aM1").Value
            If InStr(gp, ";" & Sheet4.Range("am" & i) & ";") > 0 Then
                'If Sheet4.Range("am" & i).Interior.Color = 13421823 Then gp.Offset(0, -2).Interior.Color = 13421823
                temp = temp & Sheet4.Range("am" & i) & ";"
                'js = js + 1
            End If
        Next
        If temp <> "" Then temp = Left(temp, Len(temp) - 1)
        'gp.Offset(0, -1).Value = js
        gp.Value = temp
    Next

    For Each gp In Range("T2_匹配[所属概念]")
        temp = ""
        js = 0
        For i = 2 To Sheet4.Range("aR1").Value
            If InStr(gp, ";" & Sheet4.Range("ar" & i) & ";") > 0 Then
                temp = temp & Sheet4.Range("ar" & i) & ";"
            End If
        Next
        If temp <> "" Then temp = Left(temp, Len(temp) - 1)
        'gp.Offset(0, -1).Value = js
        gp.Value = temp
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
        '比较阈值
        If gp.Offset(0, 3) >= yz And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
        '1：情绪好和差时 ，异动次数大于等于3或者监管类型有数据或者停牌非0或今昨量比大于700或者竞价量比大于等于100或自由流通市值大于80，其中任何一种情况发生，就名称绿
        If gp.Offset(0, 8) >= 3 Or gp.Offset(0, 9) <> "" Or gp.Offset(0, 5) > 700 Or gp.Offset(0, 4) >= 1 Or gp.Offset(0, 11) > 200 Then gp.Offset(0, -1).Interior.ColorIndex = 35

        If qx = "差" Then
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 2) < 0 Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Offset(0, 2).Interior.ColorIndex = 35
            End If
            If gp <> "" Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Interior.ColorIndex = 35
            End If
            If gp.Offset(0, 6) > 2 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            If gp.Column = 12 And gp.Offset(0, 3) > 0.2 Then gp.Offset(0, -1).Interior.ColorIndex = 35
        Else
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

    If qx = "好" Then

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
    For Each gp In Range("T1_匹配[    名称]")
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
            gp.Interior.ColorIndex = 36
            Exit For
        End If
    Next
    For Each gp In Range("T2_匹配[    名称]")
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
            gp.Interior.ColorIndex = 36
            Exit For
        End If
    Next

    Range("T1_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    For Each gp In Range("T1_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.3 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11) = "创百日新高" Then
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                 gp.Offset(0, -1).Interior.ColorIndex = 46
                Exit For
            End If
        End If
    Next

    For Each gp In Range("T2_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.3 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11) = "创百日新高" Then
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                 gp.Offset(0, -1).Interior.ColorIndex = 46
                Exit For
            End If
        End If
    Next
     For Each gp In Range("T1_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
             'gp.Offset(0, 2).Interior.ColorIndex = 29
            If rng5 = "" Then Set rng5 = gp.Offset(0, 2)
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                Set rng6 = gp.Offset(0, 2)
                Exit For
            End If
        End If
    Next

    If Not rng6 = "" Then
        rng6.Interior.ColorIndex = 29
    ElseIf Not rng5 = "" Then
        rng5.Interior.ColorIndex = 29
    End If


     For Each gp In Range("T2_匹配[    名称]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11).Interior.ColorIndex = 28 Then
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

    Range("T1_匹配").Sort "120日涨跌幅", 2, , , , , , 1
    Range("T2_匹配").Sort "120日涨跌幅", 2, , , , , , 1

End Sub
"""

def pi_pei_gai_nian(d):
    chuang_gn = d["chuang_gn"]
    zhu_gn = d["zhu_gn"]
    pass


