Attribute VB_Name = "��ģ��"
Option Explicit
Sub ȫ������()
    Application.ScreenUpdating = False
    'Application.DisplayAlerts = False
    'Application.Calculation = xlCalculationManual
    Dim t, t1, t0
    �������ɳ�����
    If Sheet4.Range("H100") <> Evaluate("round(sum(��1[��߼�]),2)") Then �ºϲ�����

    t = Timer
 '   Sheet4.Range("r1") = "������������"
'    Sheet4.Range("af1") = "������������"
    'tonum
    '�������ɳ�����
    ����ǰ��ֺ�
    ����
    
    �����㷨
    
    ������������
    'ɾ������
    'ȥ����������
    
'    ȡ���ǹ�Ʊ
'    �������Ǹ���
'    ȡ��ͣԭ��
'    ������ͣԭ��
    
    '�������������
    '��������
        t1 = Timer - t
        Debug.Print Round(t1, 2)
        
    �������ɫ
    '��������
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    ����
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    ��ɸѡ
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    '������������
    ƥ�����
        t1 = Timer - t
           Debug.Print Round(t1, 2)
    ������ʽ
    '���ɲ�ѯ
    '����ֱ�2
    t1 = Timer - t
    
 '   If Sheet4.Range("h3") = "�ⵥ��" Then
  '      Sheet4.Range("r1") = "��������"
  '      Sheet4.Range("af1") = "��������"
  '  End If
    'Application.ScreenUpdating = True
    'Application.Calculation = xlCalculationAutomatic
    Debug.Print Now & "���"
    MsgBox "��ɣ���ʱ��" & Round(t1, 2) & " ��"
End Sub

Sub ȥ����������()
        '�滻�������ǰ������
    Range("��[��������]").Replace "��", ";", 2
    Range("��[��������]").Replace "��", ";", 2
    Range("��1[��������]").Replace "��", ";", 2
    Range("��1[��������]").Replace "��", ";", 2
End Sub

Sub �������������()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Dim i As Integer
    Dim js_cy, js_zb, a, cyset, zbset, lz
    nogn = ";��ʱ���ظ���;��ʱ���ظ����;���յ���˹A��;����ͨ;���ͨ;������ȯ;ת��ȯ���;��ת��Ȩ;��Ȩת��;��������;����;MSCI����;һ��������;ҵ������;�걨����;����;"
    'ȡ����Ч����ϲ���һ�����ַ���
    cyset = Range("����ֵ[����ֵ]").Rows(1)
    zbset = Range("����ֵ[����ֵ]").Rows(2)
    For Each rng In Range("��[��������]")
        If Left(rng.Offset(0, -4), 5) = "SZ.30" Then '��ҵ
            If rng.Offset(0, 1) > cyset Then gnstr = gnstr & rng
        Else '����
            If rng.Offset(0, 1) > zbset Then gnstr = gnstr & rng
        End If
    Next
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            If InStr(nogn, ";" & arr(i) & ";") < 1 Then 'ȥ����Ҫ�ĸ���
                'If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
'                        js_cy = Evaluate("COUNTIFS(��[ [  ����] ],""SZ.30*"",��[��������],""*;" & arr(i) & ";*"")")
'                        js_zb = Evaluate("SUMPRODUCT(IF(ISERROR(FIND(""SZ.30"",��[  ����])),1,0),IF(ISERROR(FIND("";" & arr(i) & ";"",��[��������])),0,1))")
'                        dic(arr(i)) = Array(js_cy, js_zb)
                        dic(arr(i)) = Evaluate("COUNTIFS(��[��������],""*;" & arr(i) & ";*"")")
                    End If
                'End If
            End If
        Next
    End If
    

    '���ֵ�����������
    If Range("��ҵ�����[#data]").Rows.Count > 1 Then Range("��ҵ�����[#data]").Delete Shift:=xlShiftUp '���ԭ��
    Range("��ҵ�����[ʵ����ͨ]").NumberFormatLocal = "0.0000_ "
    Range("��ҵ�����[[#Headers],[��������]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    Range("��ҵ�����[[#Headers],[����]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)

    Set dic = Nothing '�ر��ֵ�
    
    Range("��ҵ�����[��������]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("��ҵ�����[����]").Replace "1", "", 1 '1����ȫƥ��
    Range("��ҵ�����[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    
    '����
    Range("��ҵ�����").Sort "����", 2, , , , , , 1
    Range("��1").Sort "��������", 2, , , , , , 1
    Range("��2").Sort "��������", 2, , , , , , 1
    
    '���㴴ҵ��ʵ����ͨ
    For Each a In Range("��ҵ�����[��������]")
        If a.Offset(0, 1) > 0 Then
            'a.Offset(0, 2) = Evaluate("round(AVERAGEIFS(��[�����Ƿ�],��[��������],""*;" & a & ";*""),4)")
            a.Offset(0, 2) = Evaluate("round(SUMIFS(��[�����Ƿ�],��[��������],""*;" & a & ";*""),4)")
        End If
    Next
    
    '������������=ma
'    For Each a In Range("��ҵ�����[��������]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
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


'    For Each a In Range("��ҵ�����[��������]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
'            Set rng = Sheet7.Rows(2).Find(a)
'            If Not rng Is Nothing Then
'                lz = rng.End(xlDown).Row - 3
'            End If
'            a.Offset(0, 3) = lz
'            If lz < 2 Then a.Offset(0, 3).Interior.ColorIndex = 35
'        End If
'    Next



End Sub
Sub �������ɫ()
    Debug.Print Now & "�������ɫ"
    Dim rng1 As Range
    Dim rng2 As Range
    Dim rng3 As Range
    Dim rng As Range
    Dim imax As Integer
    Dim isred As Integer
    Dim firstAddress
    Dim arr
   '��ȥ����ǰ����ɫ
    Range("��ҵ�����[ʵ����ͨ]").Interior.Pattern = xlNone
    On Error GoTo line1
    Range("����ɸѡ[����ɸѡ]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
line1:
     '   For Each rng1 In Range("����ɸѡ[����ɸѡ]")
      '      If rng1 <> "" Then
       '         Set rng2 = Range("��ҵ�����[��������]").Find(rng1.Value, , , 1) '��ȷ
       '         If Not rng2 Is Nothing Then
       '             rng2.Offset(0, 2).Interior.ColorIndex = 36
       '         End If
       '     End If
       ' Next
    
    'ȡ��ҵ�����������������ʵ����ͨ
    '��Ϊ��ҵ������������Ķ�Ҫ
    'imax = Evaluate("MAXIFS(��ҵ�����[ʵ����ͨ],��ҵ�����[����],MAX(��ҵ�����[����]))")
'    imax = Evaluate("MAX(��ҵ�����[����])")
'        Set rng1 = Range("��ҵ�����[����]")
'        Set rng = rng1.Find(imax)
'        If Not rng Is Nothing Then
'            firstAddress = rng.Address
'            Do
'                 rng.Offset(0, 1).Interior.Color = 13421823
'                 Set rng = rng1.FindNext(rng)
'            Loop While Not rng Is Nothing And rng.Address <> firstAddress
'        End If
    'imax = Evaluate("MAX(��ҵ�����[����])")
    isred = 0
    For Each rng In Range("��ҵ�����[��������]")
        If isred = 0 Then imax = rng.Offset(0, 3).Value
        'If rng.Offset(0, -3).Interior.ColorIndex <> 35 And rng.Interior.ColorIndex <> 35 And rng.Offset(0, 1).Interior.ColorIndex <> 35 And rng.Offset(0, 2).Interior.ColorIndex <> 35 And rng = imax Then
        ' ���򾺷�  ���зⵥ�ܺ� ��ͣ�ⵥ��  ����
        If rng.Offset(0, 4).Interior.ColorIndex <> 35 And rng.Offset(0, 5).Interior.ColorIndex <> 35 And rng.Offset(0, 6).Interior.ColorIndex <> 35 And rng.Offset(0, 3) = imax Then
            rng.Offset(0, 3).Interior.Color = 13421823
            'If rng.Offset(0, -3) <> "����ĸ�" Then isred = isred + 1
            isred = isred + 1
        End If
    Next
    imax = 0
    For Each rng In Range("��ҵ�����[��������¸�]")
        If rng.Interior.ColorIndex <> 35 Then
            arr = Split(rng, " | ")
            If arr(0) * 1 > imax Then imax = arr(0)
        End If
    Next
    For Each rng In Range("��ҵ�����[��������¸�]")
        If rng.Interior.ColorIndex <> 35 Then
            arr = Split(rng, " | ")
            If arr(0) * 1 = imax Then
                rng.Offset(0, -1).Interior.Color = 13421823
                'If rng.Offset(0, -3) <> "����ĸ�" Then isred = isred + 1
            End If
        End If
    Next

    'Range("��ҵ�����[ʵ����ͨ]").NumberFormatLocal = "0.00%"
    
End Sub

Sub ��������()
    
    Dim tj As Range
    Dim rng As Range
    Dim gn As Range
    Dim iscyb, iszb, i As Integer
    Dim t As String
    Dim �������
    
'    On Error GoTo line2
'    Range("����[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'    Range("��������[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'    Range("����[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'    Range("���Ʊ���[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
'line2:

'    Range("����[    ����]").Interior.Pattern = xlNone
'    Range("����[�����Ƿ�]").Interior.Pattern = xlNone
    Sheet8.Range("A:V").Interior.Pattern = xlNone
'��ԭʼ���ݱ���ȡ�Լ�����Ĺ�Ʊ�����ݵ����ù�Ʊ
    For Each tj In Range("����[����]")
        Set rng = Range("��1[    ����]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("��2[    ����]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
                
        End If
    Next
    For Each tj In Range("��������[����]")
        Set rng = Range("��1[    ����]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("��2[    ����]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
        End If
    Next
    For Each tj In Range("����[����]")
        Set rng = Range("��1[    ����]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("��2[    ����]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
        End If
    Next
    For Each tj In Range("���Ʊ���[����]")
        Set rng = Range("��1[    ����]").Find(tj)
        'If rng Is Nothing Then Set rng = Range("��2[    ����]").Find(tj)
        If Not rng Is Nothing Then
                tj.Offset(0, -1) = rng.Offset(0, -1)
                tj.Offset(0, 1) = rng.Offset(0, 3)
                tj.Offset(0, 2) = rng.Offset(0, 4)
                If tj.Offset(0, 2) <= -5 Then tj.Offset(0, 2).Interior.ColorIndex = 35
        End If
    Next


    '��ȥ����ǰ����ɫ
    Range("��ҵ�����[��������]").Interior.Pattern = xlNone
    
    '�����С��-5%�Ĺ�Ʊ�Ͱѱ��ù�Ʊ��ӵ�������
    

    ������� = 0
    If Evaluate("MAX(����[�����Ƿ�])") <= -5 Then
        ������� = 1
        For Each tj In Range("��������[����]")
            Set rng = Range("����[����]").Find(tj)
            'If rng Is Nothing Then Range("����").ListObject.ListRows.Add.Range = Array("", tj, "", "", tj.Offset(0, 3))
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
'        For Each tj In Range("����[����]")
'            Set rng = Range("��1[    ����]").Find(tj)
'            If Not rng Is Nothing Then
'                tj.Interior.ColorIndex = 15
'            Else
'                Set rng = Range("��2[    ����]").Find(tj)
'            End If
'            If Not rng Is Nothing Then
'                    tj.Offset(0, -1) = rng.Offset(0, -1)
'                    tj.Offset(0, 1) = rng.Offset(0, 3)
'                    tj.Offset(0, 2) = rng.Offset(0, 4)
'            End If
'        Next
    End If
    

'    If Evaluate("MAX(����[�����Ƿ�])") <= -0.05 Then
'        For Each tj In Range("���ù�Ʊ2[���ù�Ʊ2]")
'            Set rng = Range("����[    ����]").Find(tj)
'            If rng Is Nothing Then Range("����").ListObject.ListRows.Add.Range = Array("", tj, "", "", tj.Offset(0, 3))
'        Next
'        For Each tj In Range("����[    ����]")
'            Set rng = Range("��1[    ����]").Find(tj)
'            If Not rng Is Nothing Then
'                tj.Interior.ColorIndex = 15
'            Else
'                Set rng = Range("��2[    ����]").Find(tj)
'            End If
'            If Not rng Is Nothing Then
'                    tj.Offset(0, -1) = rng.Offset(0, -1)
'                    tj.Offset(0, 1) = rng.Offset(0, 3)
'                    tj.Offset(0, 2) = rng.Offset(0, 4)
'            End If
'        Next
'    End If


    

    
    '������ƥ������,������ɫ
    For Each tj In Range("����[��������]")
        If tj.Offset(0, 1) > -5 Then
            For Each gn In Range("��ҵ�����[��������]")
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
    '������ƥ������,�������ɫ
    For Each tj In Range("����[��������]")
        If tj.Offset(0, 1) <= -5 Then
            tj.Offset(0, 1).Interior.ColorIndex = 35
            For Each gn In Range("��ҵ�����[��������]")
                If InStr(tj, ";" & gn & ";") > 0 Then gn.Interior.ColorIndex = 35
            Next
        End If
    Next
    '��������˱��ù�Ʊ��������ƥ������,������ɫ����
    If ������� Then
        For Each tj In Range("����[��������]")
            If tj.Offset(0, 1) > -5 Then
                For Each gn In Range("��ҵ�����[��������]")
                    If InStr(tj, ";" & gn & ";") > 0 And gn.Interior.ColorIndex = 35 Then gn.Interior.ColorIndex = 36
                Next
            End If
        Next
    End If
    
    
    ������� = 0
    If Evaluate("MAX(����[�����Ƿ�])") <= -5 Then
        ������� = 1
        For Each tj In Range("���Ʊ���[����]")
            Set rng = Range("����[����]").Find(tj)
            'If rng Is Nothing Then Range("����").ListObject.ListRows.Add.Range = Array("", tj, "", "", tj.Offset(0, 3))
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
'        For Each tj In Range("����[����]")
'            Set rng = Range("��1[    ����]").Find(tj)
'            If Not rng Is Nothing Then
'                tj.Interior.ColorIndex = 15
'            Else
'                Set rng = Range("��2[    ����]").Find(tj)
'            End If
'            If Not rng Is Nothing Then
'                    tj.Offset(0, -1) = rng.Offset(0, -1)
'                    tj.Offset(0, 1) = rng.Offset(0, 3)
'                    tj.Offset(0, 2) = rng.Offset(0, 4)
'            End If
'        Next
    End If

    
    '������ƥ������,������ɫ
    For Each tj In Range("����[��������]")
        If tj.Offset(0, 1) > -5 Then
            For Each gn In Range("��ҵ�����[��������]")
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
    '������ƥ������,�������ɫ
    For Each tj In Range("����[��������]")
        If tj.Offset(0, 1) <= -5 Then
            tj.Offset(0, 1).Interior.ColorIndex = 35
            For Each gn In Range("��ҵ�����[��������]")
                If InStr(tj, ";" & gn & ";") > 0 Then gn.Interior.ColorIndex = 35
            Next
        End If
    Next
    '��������˱��ù�Ʊ��������ƥ������,������ɫ����
    If ������� Then
        For Each tj In Range("����[��������]")
            If tj.Offset(0, 1) > -5 Then
                For Each gn In Range("��ҵ�����[��������]")
                    If InStr(tj, ";" & gn & ";") > 0 And gn.Interior.ColorIndex = 35 Then gn.Interior.ColorIndex = 36
                Next
            End If
        Next
    End If
    '���ù�Ʊ��ƥ������,�������ɫ
'    For Each tj In Range("���ù�Ʊ[��������]")
'        If tj.Offset(0, 1) <= -0.05 Then
'            tj.Offset(0, 1).Interior.ColorIndex = 35
'            For Each gn In Range("��ҵ�����[��������]")
'                If InStr(tj, ";" & gn & ";") > 0 Then gn.Interior.ColorIndex = 35
'            Next
'        End If
'    Next
    
'    Range("����[�����Ƿ�]").NumberFormatLocal = "0.00%"
'    Range("��������[�����Ƿ�]").NumberFormatLocal = "0.00%"
'    Range("����[�����Ƿ�]").NumberFormatLocal = "0.00%"
'    Range("���Ʊ���[�����Ƿ�]").NumberFormatLocal = "0.00%"
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
Sub ��ɸѡ()
    Debug.Print Now & "��ɸѡ"
    Dim h1, h2, yd, i As Integer
    Dim a As Range
    Dim arr
    Dim firstAddress
  '  On Error Resume Next
'    ActiveWorkbook.Names("Criteria").Delete
'    ActiveWorkbook.Names("Extract").Delete

    ActiveSheet.ListObjects("T1_ƥ��").Unlist
    ActiveSheet.ListObjects("T2_ƥ��").Unlist
    Dim rng As Range
    Dim rng1 As Range
    Dim rng2 As Range
    Dim allgn As String
    'Sheet4.Range("af2:az1048576").Clear
    Sheet4.Range("i2:bh1048576").Clear
    h1 = 1
    allgn = ""
    For Each a In Range("��ҵ�����[��������]")
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
    '���Ǹ���
    
    arr = Split(Sheet4.Range("h9"), ";")
    For i = LBound(arr) To UBound(arr)
        If arr(i) <> "" Then
            
            
            Set a = Range("��ҵ�����[��������]").Find(arr(i), , , 1)
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
    ' ����ȡǰ3
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
        Sheet25.Range("i:j").Sort "����Դ����", 2, , , , , , 1
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
         ActiveSheet.ListObjects.Add(xlSrcRange, Range("j1").CurrentRegion, , xlYes).Name = "T1_ƥ��"
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("x1").CurrentRegion, , xlYes).Name = "T2_ƥ��"
       Exit Sub
    End If
    
    
    Dim t, t1, t0
    t = Timer
    
    If h1 > 1 Then
        Range("��1[#ALL]").AdvancedFilter 2, Sheet4.Range("ax1:ay" & h1), Sheet4.Range("j1:s1")
        Range("��1[#ALL]").AdvancedFilter 2, Sheet4.Range("bb1:bd" & h1), Sheet4.Range("x1:ag1")
    End If
            t1 = Timer - t
      '  Debug.Print Round(t1, 2) & "----"
        
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("j1").CurrentRegion, , xlYes).Name = "T1_ƥ��"
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("x1").CurrentRegion, , xlYes).Name = "T2_ƥ��"

    ��ɸѡ2
End Sub


Sub ��ɸѡ2()
    Debug.Print Now & "��ɸѡ2"
    Dim h1, h2, yd, i As Integer
    Dim a As Range
    Dim arr
    Dim firstAddress

    Dim rng As Range
    Dim rng1 As Range
    Dim ngs As Range
    Dim allgn As String

   ' If Sheet4.Range("h3") = "�ⵥ��" Then
   '     For Each rng In Range("T1_ƥ��[  ����]")
   '         Set rng1 = Sheet2.Range("A:A").Find(rng)
   '         rng.Offset(0, 4) = rng1.Offset(0, 5)
   '     Next
   '      For Each rng In Range("T2_ƥ��[  ����]")
   '         Set rng1 = Sheet2.Range("A:A").Find(rng)
   '         rng.Offset(0, 4) = rng1.Offset(0, 5)
   '     Next
   ' End If
    
    ' �ⵥ�� ��ͣԭ����������������Ҫȡtable1�������������
 '   If Sheet4.Range("h3") = "�ⵥ��" Then
 '       For Each rng In Range("T1_ƥ��[  ����]")
 '           Set rng1 = Sheet2.Range("A:A").Find(rng)
 '           rng.Offset(0, 8) = rng1.Offset(0, 25)
 '       Next
 '        For Each rng In Range("T2_ƥ��[  ����]")
 '           Set rng1 = Sheet2.Range("A:A").Find(rng)
 '           rng.Offset(0, 8) = rng1.Offset(0, 25)
 '       Next
 '   End If
    
        
    Range("T1_ƥ��").Sort "4���ǵ���", 2, , , , , , 1
    Range("T2_ƥ��").Sort "4���ǵ���", 2, , , , , , 1
    yd = Sheet18.Range("a1").End(xlDown).Row '�춯������
    For Each rng In Range("T1_ƥ��[  ����]")
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
        rng.Offset(0, 10) = Evaluate("COUNTIFS(�춯!A:A,""" & rng & """,�춯!J:J,""����*"")")
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
        If Not rng1 Is Nothing Then rng.Offset(0, 12) = "�������¸�"
        
        Set rng1 = Sheet24.Range("A:A").Find(rng.Value)
        
         If Not rng1 Is Nothing Then
            rng.Offset(0, 12).Interior.ColorIndex = 37
            If rng1.Offset(0, 7) > 0 Then rng.Offset(0, 8).Interior.ColorIndex = 38
            If rng1.Offset(0, 5) > 0 Then rng.Offset(0, 8).Interior.ColorIndex = 38
            If rng1.Offset(0, 6) = "��ͣ" And rng.Offset(0, 8) = 0 Then
                rng.Offset(0, 8).Interior.ColorIndex = 38
                'rng.Offset(0, 12) = rng.Offset(0, 12) & ";" & "����"
            End If
        End If
    Next
    
    For Each rng In Range("T2_ƥ��[  ����]")
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
        rng.Offset(0, 10) = Evaluate("COUNTIFS(�춯!A:A,""" & rng & """,�춯!J:J,""����*"")")
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
        If Not rng1 Is Nothing Then rng.Offset(0, 12) = "�������¸�"
        
        Set rng1 = Sheet23.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then
            If rng1.Offset(0, 10) > 0 Then rng.Offset(0, 8).Interior.ColorIndex = 38
            rng.Offset(0, 12).Interior.ColorIndex = 37
            If rng1.Offset(0, 6) = "����ͣ" Then rng.Offset(0, 8).Interior.ColorIndex = 38
            If rng1.Offset(0, 7) = "��ͣ" And rng.Offset(0, 8) = 0 Then
                rng.Offset(0, 8).Interior.ColorIndex = 38
                'rng.Offset(0, 12) = rng.Offset(0, 12) & ";" & "����"
            End If
        End If
        
    Next

    
    'ȥ��25����ͣ������0�Ĺ�Ʊ
    On Error GoTo line
     Range("T2_ƥ��[25����ͣ����]").Replace "0", "", 1
     Range("T2_ƥ��[25����ͣ����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp

line:

    
    'ȡ��ͣ��ʱ��
    For Each rng In Range("T2_ƥ��[  ����]")
        Set rng1 = Sheet2.Range("A:A").Find(rng.Value)
        If Not rng1 Is Nothing Then
            rng.Offset(0, 13) = Round(rng1.Offset(0, 14) / 100000000, 2)
        End If
    Next
    
    Range("T1_ƥ��[�ǵ���]").NumberFormatLocal = "0.00% "
    Range("T1_ƥ��[��������]").NumberFormatLocal = "0.00% "
    Range("T1_ƥ��[��������]").NumberFormatLocal = "0.00_ "
    Range("T1_ƥ��[4���ǵ���]").NumberFormatLocal = "0.00% "
    Range("T1_ƥ��[120���ǵ���]").NumberFormatLocal = "0.00% "
    Range("T2_ƥ��[�ǵ���]").NumberFormatLocal = "0.00% "
    Range("T2_ƥ��[��������]").NumberFormatLocal = "0.00% "
    Range("T2_ƥ��[��������]").NumberFormatLocal = "0.00_ "
    Range("T2_ƥ��[4���ǵ���]").NumberFormatLocal = "0.00% "
    Range("T2_ƥ��[120���ǵ���]").NumberFormatLocal = "0.00% "
    Range("��1").AutoFilter

End Sub










Sub �����ѯ()
    Debug.Print Now & "�����ѯ"
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

    ActiveSheet.ListObjects("T1_ƥ��").Unlist
    ActiveSheet.ListObjects("T2_ƥ��").Unlist
    Dim rng As Range
    Dim rng1 As Range
    'Sheet4.Range("af2:az1048576").Clear
    Sheet4.Range("i2:bd1048576").Clear
    gncs = Sheet4.Range("h19")
    arr = Split(Left(gncs, Len(gncs) - 1), ";")
    h1 = 1
    For i = LBound(arr) To UBound(arr)
        If a <> "" Then
         '   Set a = Range("��ҵ�����[��������]").Find(arr(i), , , 1)
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
        Range("��1[#ALL]").AdvancedFilter 2, Sheet4.Range("ax1:ay" & h1), Sheet4.Range("j1:s1")
        Range("��1[#ALL]").AdvancedFilter 2, Sheet4.Range("bb1:bd" & h1), Sheet4.Range("x1:ag1")
    End If
    
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("j1").CurrentRegion, , xlYes).Name = "T1_ƥ��"
    ActiveSheet.ListObjects.Add(xlSrcRange, Range("x1").CurrentRegion, , xlYes).Name = "T2_ƥ��"
    
    
    ��ɸѡ2
    ƥ�����
    Application.ScreenUpdating = True
    
 
End Sub
Sub �װ����()
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
    '��������ת�ֵ�ȥ��
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

Sub ���װ�()
    Dim rng As Range
    Dim h, i As Integer
    Dim gnstr As String
    Set rng = Sheet21.Range("a:a").Find("�װ�")
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


Sub ������������()
    Dim tj, rng, r As Range
    For Each tj In Range("����[����]")
        Set rng = Range("T1_ƥ��[    ����]").Find(tj)
        If rng Is Nothing Then Set rng = Range("T2_ƥ��[    ����]").Find(tj)
        If Not rng Is Nothing Then rng.Offset(0, 6) = tj.Offset(0, 3)
    Next
    For Each tj In Range("����[����]")
        Set rng = Range("T1_ƥ��[    ����]").Find(tj)
        If rng Is Nothing Then Set rng = Range("T2_ƥ��[    ����]").Find(tj)
        If Not rng Is Nothing Then rng.Offset(0, 6) = tj.Offset(0, 3)
    Next
    Range("T1_ƥ��").Sort "�����Ƿ�", 2, , , , , , 1
    Range("T2_ƥ��").Sort "��������", 2, "�����Ƿ�", , 2, , , 1
'    Range("T1_ƥ��[��ʱ����]").Replace "sam", "", 2
'    Range("T2_ƥ��[��ʱ����]").Replace "sam", "", 2
'    Range("��1").Sort "��������", 2, , , , , , 1
'    Range("��2").Sort "��������", 2, , , , , , 1

End Sub
Sub te()
    Debug.Print Len(Sheet4.Range("L2"))
'Range("T1_ƥ��[��ʱ����]").Replace "sam", "", 2
End Sub
Sub ƥ�����()
    Debug.Print Now & "ƥ�����"
    Dim gp, rng, rng3, rng4, rng5, rng6, rng7 As Range
    Dim temp, qx As String
    Dim js, i, h As Integer
    Dim yz, imax1, imax2, imin1, imin2, ijjlb1, ijjlb2, ijzlb1, ijzlb2 As Double
    qx = Sheet4.Range("H6")
    
    
    If Sheet4.Range("aw1") = 1 Then
        Exit Sub
    End If
    
    Range("T1_ƥ��[������ҵ]") = ""
    Range("T2_ƥ��[������ҵ]") = ""
    
    
    If Sheet19.Range("a2") <> "" Then
        h = Sheet19.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("T1_ƥ��[  ����]").Find(Sheet19.Range("a" & i), , , 1)
            If rng Is Nothing Then Set rng = Range("T2_ƥ��[  ����]").Find(Sheet19.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 2) = Round(Sheet19.Range("e" & i) / 100000000, 2)
            End If
        Next
    End If
    For Each gp In Range("T1_ƥ��[��������]")
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
'        '��
'        If gp.Offset(0, 5) > 1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 1 And gp.Offset(0, 2) >= 0.2 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 0 And gp.Offset(0, 2) >= 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 2) < 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        '��
'        If gp.Offset(0, 7) > 2 Or gp.Offset(0, 8) <> "" Or gp.Offset(0, 9) > 0 Then gp.Offset(0, -2).Interior.ColorIndex = 35
'        If gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 Then gp.Offset(0, 4).Interior.Color = 13551615
'        If gp.Offset(0, 4) > 1000 Then gp.Offset(0, 4).Interior.ColorIndex = 35
    Next
    
    For Each gp In Range("T2_ƥ��[��������]")
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
'        '��
'        If gp.Offset(0, 5) > 1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 1 And gp.Offset(0, 2) >= 0.2 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 5) = 0 And gp.Offset(0, 2) >= 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        If gp.Offset(0, 2) < 0.1 And gp.Offset(0, 3) >= 0.08 And gp.Offset(0, 4) <= 1000 And gp.Offset(0, 7) > 3 And gp.Offset(0, 8) <> "" And gp.Offset(0, 9) > 1 Then gp.Offset(0, -2).Interior.Color = 13551615
'        '��
'        If gp.Offset(0, 7) > 2 Or gp.Offset(0, 8) <> "" Or gp.Offset(0, 9) > 0 Then gp.Offset(0, -2).Interior.ColorIndex = 35
'        If gp.Offset(0, 4) >= 100 And gp.Offset(0, 4) <= 1000 Then gp.Offset(0, 4).Interior.Color = 13551615
'        If gp.Offset(0, 4) > 1000 Then gp.Offset(0, 4).Interior.ColorIndex = 35
'        If gp.Offset(0, 5) = 0 And gp.Offset(0, 2) >= 0.1 Then
'            If Not (gp.Offset(0, 4) >= 100 And gp.Offset(0, 3) >= 0.08) Then gp.Offset(0, -2).Interior.ColorIndex = 35
'        End If
    Next
    
'-2  ����
'-1    ����
'0 ����δƥ��
'1 ��������
'2 �ǵ���
'3 5���ǵ���
'4 ��������
'5 ��������
'6 ������������
'7 25����ͣ����
'8 �춯����
'9 ���
'10 ͣ��

    '=====================��߱���============
    If Sheet4.Range("h26").Interior.ColorIndex = 35 Then
        Set rng = Union(Range("T1_ƥ��[    ����]"), Range("T2_ƥ��[    ����]")).Find(Sheet4.Range("h25"), , , 1)
        If Not rng Is Nothing Then rng.Interior.ColorIndex = 35
    End If
    If Sheet4.Range("h28").Interior.ColorIndex = 35 Then
        Set rng = Union(Range("T1_ƥ��[    ����]"), Range("T2_ƥ��[    ����]")).Find(Sheet4.Range("h27"), , , 1)
        If Not rng Is Nothing Then rng.Interior.ColorIndex = 35
    End If

    '����
    yz = Sheet4.Range("H12") '��ֵ
    For Each gp In Union(Range("T1_ƥ��[������ҵ]"), Range("T2_ƥ��[������ҵ]"))
        '�Ƚ���ֵ, �����ȴ��ڵ���8%
     '   If gp.Offset(0, 3) >= yz And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
        '1�������úͲ�ʱ ���춯�������ڵ���3���߼������������ ���춯�ǿ��������
        If (gp.Offset(0, 8) >= 4 And Sheet4.Range("H90") = "�춯��" And gp.Offset(0, 10) = "") Then gp.Offset(0, -1).Interior.ColorIndex = 35
       
        
        If qx = "��" Then
          ' ����ͣ�Ʒ�0��������ȴ���700���߾������ȴ��ڵ���100�� (������ͨ��ֵ����80�Ҳ���������˹���� H13)�������κ�һ�������������������
          '�������ȴ��ڵ���50
            If gp.Offset(0, 9) <> "" Or gp.Offset(0, 5) > 700 Or gp.Offset(0, 4) >= 0.5 Or (gp.Offset(0, 11) > 100 And gp.Offset(0, -1) <> Sheet4.Range("H13")) Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
            End If
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 2) < 0 And Sheet4.Range("H11") <> gp.Offset(0, -1) Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Offset(0, 2).Interior.ColorIndex = 35
            End If
            'If gp.Offset(0, 6) = 2 And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            '���������δƥ�����0�Ļ��� ����δƥ���к���������������벻Ҫ��
            If gp <> "" Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
                gp.Interior.ColorIndex = 35
            End If
            
            '���ⳬ��2 ����
            If gp.Offset(0, 6) > 2 Then
                If gp.Column <> 12 And (gp.Offset(0, 6) < Sheet4.Range("H10") Or gp.Offset(0, -1) <> Sheet4.Range("H11")) Then gp.Offset(0, -1).Interior.ColorIndex = 35
                If gp.Column = 12 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            End If
            
            ' ����=2 �����ȴ��ڵ���8%  ����
            'If gp.Offset(0, 6) = 2 And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            '��ҵ��������ԭ����4���ǵ�������20%���̸ĳ�4���ǵ�������100%
            If gp.Column = 12 And gp.Offset(0, 3) > 1 Then gp.Offset(0, -1).Interior.ColorIndex = 35
            
            '������ֺ����� ��������������������������ֵ���ֺ�������һ���ģ�����δƥ�����ȥ��
            If gp.Offset(0, -1) = Sheet4.Range("H11") And gp.Offset(0, 6) = Sheet4.Range("H10") And gp <> "" Then
                gp.Interior.Color = xlNone
                gp.Offset(0, -1).Interior.Color = xlNone
            End If
        Else
             ' ����ͣ�Ʒ�0��������ȴ���700���߾������ȴ��ڵ���100�� (������ͨ��ֵ����80�Ҳ���������˹���� H13)�������κ�һ�������������������
            If gp.Offset(0, 9) <> "" Or gp.Offset(0, 5) > 700 Or gp.Offset(0, 4) >= 1 Or (gp.Offset(0, 11) > 100 And gp.Offset(0, -1) <> Sheet4.Range("H13")) Then
                gp.Offset(0, -1).Interior.ColorIndex = 35
            End If
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then gp.Offset(0, 4).Interior.Color = 13551615
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then gp.Offset(0, 5).Interior.Color = 13551615
           
        End If
        
    Next
    
    '���
    imax1 = 0
    imax2 = 0
    imin1 = 0
    imin2 = 0
    ijjlb1 = 0
    ijjlb2 = 0
    ijzlb1 = 0
    ijzlb2 = 0
    For Each gp In Range("T1_ƥ��[������ҵ]")
        If qx = "��" Then
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then gp.Offset(0, 4).Interior.Color = 13551615
            If imin1 = 0 Then
                If gp < 0 And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    imin1 = 1
                    gp.Offset(0, -1).Interior.Color = 13551615
                End If
            End If
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then gp.Offset(0, 5).Interior.Color = 13551615
        Else '������ʱ
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
    For Each gp In Range("T2_ƥ��[������ҵ]")
        If qx = "��" Then
            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) < 1 Then gp.Offset(0, 4).Interior.Color = 13551615
            If imin1 = 0 Then
                If gp < 0 And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    imin2 = 1
                    gp.Offset(0, -1).Interior.Color = 13551615
                End If
            End If
            If gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 700 Then gp.Offset(0, 5).Interior.Color = 13551615
        Else '������ʱ
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
'    For Each gp In Union(Range("T1_ƥ��[������ҵ]"), Range("T2_ƥ��[������ҵ]"))
'        If qx = "��" Then
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
'        Else '������ʱ
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
    If qx = "��" Then
'        Set rng = Sheet4.Range("P:P").Find(ijjlb1, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'            rng.Offset(0, -5).Interior.Color = 13551615
'        End If
'        Set rng = Range("T2_ƥ��[��������]").Find(ijjlb2, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'            rng.Offset(0, -5).Interior.Color = 13551615
'        End If
'
'        Set rng = Range("T1_ƥ��[��������]").Find(ijzlb1, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'        End If
'        Set rng = Range("T2_ƥ��[��������]").Find(ijzlb2, , , 1)
'        If Not rng Is Nothing Then
'            rng.Interior.ColorIndex = 3
'        End If
        If imin1 = 0 Then
            For Each gp In Range("T1_ƥ��[������ҵ]")
                If gp = "" And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    gp.Offset(0, -1).Interior.Color = 13551615
                    Exit For
                End If
            Next
        End If
        If imin2 = 0 Then
            For Each gp In Range("T2_ƥ��[������ҵ]")
                If gp = "" And gp.Offset(0, -1).Interior.ColorIndex <> 35 And gp.Offset(0, 4) >= 0.08 Then
                    gp.Offset(0, -1).Interior.Color = 13551615
                    Exit For
                End If
            Next
        End If
    Else '������ʱ
        For Each gp In Range("T1_ƥ��[��������]")
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
        For Each gp In Range("T2_ƥ��[��������]")
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
    
    
    '���
'    imax1 = 0
'    imax2 = 0
'    For Each gp In Union(Range("T1_ƥ��[    ����]"), Range("T2_ƥ��[    ����]"))
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

   ' For Each gp In Range("T1_ƥ��[    ����]")
    '    If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
     '       gp.Interior.ColorIndex = 36
      '      Exit For
    '    End If
  '  Next
  '  For Each gp In Range("T2_ƥ��[    ����]")
  '      If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 5).Interior.Color <> 13551615 And gp.Offset(0, 5).Interior.ColorIndex <> 3 Then
  '          gp.Interior.ColorIndex = 36
   '         Exit For
   '     End If
   ' Next
    
    Range("T1_ƥ��").Sort "120���ǵ���", 2, , , , , , 1
    Range("T2_ƥ��").Sort "120���ǵ���", 2, , , , , , 1
    For Each gp In Range("T1_ƥ��[    ����]")
        If gp.Offset(0, 3) > 0 Then
            Set rng = Sheet2.Range("b:b").Find(gp, , , 1)
            If rng.Offset(0, 23) < 0 Then
                gp.Interior.ColorIndex = 36
                Exit For
            End If
        End If
    Next
    For Each gp In Range("T2_ƥ��[    ����]")
       If gp.Offset(0, 3) > 0 Then
            Set rng = Sheet2.Range("b:b").Find(gp, , , 1)
            If rng.Offset(0, 23) < 0 Then
                gp.Interior.ColorIndex = 36
                Exit For
            End If
        End If
    Next
    
    
'    For Each gp In Union(Range("T1_ƥ��[������ҵ]"), Range("T2_ƥ��[������ҵ]"))
'        '�Ƚ���ֵ
'        If gp.Offset(0, 3) >= yz Then gp.Offset(0, -1).Interior.ColorIndex = 35
'
'        If qx = "��" Then
'            If gp <> "" Then gp.Offset(0, -1).Interior.ColorIndex = 35 '����δƥ�䲻Ϊ�յ�
'            If gp.Offset(0, 8) < 3 And gp.Offset(0, 9) = "" And gp.Offset(0, 10) < 1 Then '�춯����С��3���������û�����ݣ�ͣ����0
'                '1������ʱ������������������1�ģ�ֻҪ�������ȴ��ڵ���8%����С��100%, ��������С�ڵ���500���춯����С��3���������û�����ݣ�ͣ����0 �Ϳ��Ժ�
'                'If gp.Offset(0, 6) > 1 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 6) < 1 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'
'                If gp.Offset(0, 2) > 0 Then
'                    '2��������������1�� ���5���ǵ���С��20%���������ȴ��ڵ���8%����������С�ڵ���500���춯����С��3���������û�����ݣ�ͣ����0�Ϳ��Ժ�
'                    '���5���ǵ������ڵ���20% �������ȴ��ڵ���8%���ҽ������ȴ��ڵ���100��С�ڵ���500���춯����С��3���������û���ݣ�ͣ����0�Ϳ��Ժ죬
'                    If gp.Offset(0, 6) = 1 And gp.Offset(0, 3) < 0.2 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'                    If gp.Offset(0, 6) = 1 And gp.Offset(0, 3) >= 0.2 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 5) >= 100 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'                End If
'
'                '3��������������0�ģ����5���ǵ���С��10%,�������ȴ��ڵ���8%,��������С�ڵ���500���춯����С��3���������û�����ݣ�ͣ����0�Ϳ��Ժ�
'                If gp.Offset(0, 6) = 0 And gp.Offset(0, 3) < 0.1 And gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 5) <= 500 Then gp.Offset(0, -1).Interior.Color = 13421823
'            End If
'        Else
'            '1�������ȴ��ڵ���8%����С��100%, ��������С�ڵ���500���춯����С��3���������û�����ݣ�ͣ����0 �Ϳ��Ժ�
'            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 4) <= 1 And gp.Offset(0, 5) <= 500 And gp.Offset(0, 8) < 3 And gp.Offset(0, 9) = "" And gp.Offset(0, 10) < 1 Then gp.Offset(0, -1).Interior.Color = 13421823
'        End If
'
'
'        If gp.Column = 12 Then '����ڵ�12�У�Ҳ���Ǵ�ҵ��
'            'ֻҪ�������ȴ��ڵ���8%���춯����С��3���������û���ݣ�ͣ����0�����ƺ졣
'            If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 8) < 3 And gp.Offset(0, 9) = "" And gp.Offset(0, 10) < 1 Then gp.Offset(0, -1).Interior.Color = 13421823
'            'ֻҪ�ƶ��������ڵ���3���߼�����������ݻ���ͣ�Ʒ�0��������
'            If gp.Offset(0, 8) >= 3 Or gp.Offset(0, 9) <> "" Or gp.Offset(0, 10) > 0 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'        Else
'            If qx = "��" Then
'                '��������ֻҪ�������ȴ��ڵ���8%�����ǵ���С��0%�͹�Ʊ�����̡�
'                If gp.Offset(0, 4) >= 0.08 And gp.Offset(0, 2) < 0 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'                '�������������������������1�����Ҿ������ȴ��ڵ���8%���͹�Ʊ�����̡�
'                If gp.Offset(0, 6) > 1 And gp.Offset(0, 4) >= 0.08 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'                '��������ֻҪ����δƥ������ֵ�������ƺ;���δƥ�����ж���;
'                If gp <> "" Then
'                    gp.Offset(0, -1).Interior.ColorIndex = 35
'                    gp.Interior.ColorIndex = 35
'                End If
'                '�������������������������2�ľ͹�Ʊ�����̡�
'                If gp.Offset(0, 6) > 2 Then gp.Offset(0, -1).Interior.ColorIndex = 35
'            End If
'        End If
'    Next
    Range("T1_ƥ��").Sort "120���ǵ���", 2, , , , , , 1
    Range("T2_ƥ��").Sort "120���ǵ���", 2, , , , , , 1
    For Each gp In Range("T1_ƥ��[    ����]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        ' ������ɫ�� ����δƥ��<=0 �� 120�� > 0.25 �� < 0.8 ������ >0 �� �����Ƿ�ɫ
       ' If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.25 And gp.Offset(0, 8) < 0.8 Then
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 Then
           '' If InStr(gp.Offset(0, 11), "�������¸�") > 0 Or InStr(gp.Offset(0, 11), "����") > 0 Then
             If InStr(gp.Offset(0, 11), "�������¸�") > 0 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
               ' If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                     gp.Offset(0, -1).Interior.ColorIndex = 46
                    Exit For
                'End If
            End If
        End If
    Next
   
    For Each gp In Range("T2_ƥ��[    ����]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        'If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.25 And gp.Offset(0, 8) < 0.8 Then
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) > 0.25 Then

            If InStr(gp.Offset(0, 11), "�������¸�") > 0 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
                'If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                     gp.Offset(0, -1).Interior.ColorIndex = 46
                    Exit For
               ' End If
            End If
        End If
    Next
    
    Range("T1_ƥ��").Sort "4���ǵ���", 2, , , , , , 1
    Range("T2_ƥ��").Sort "4���ǵ���", 2, , , , , , 1
    Range("T1_ƥ��").Sort "������������", 2, , , , , , 1
    Range("T2_ƥ��").Sort "������������", 2, , , , , , 1
    
    ' С�ڵ���5����ɫ����Ҫ����δƥ��С�ڵ���1�ģ� �����Ȧ�����ִ��ڵ���5����ɫ����Ҫ��Ҫ����δƥ��С�ڵ���1
    ' ��ɫ����δƥ�� ���� 1000 ���ǲ���Ҫ��Ҫ����δƥ��С�ڵ���1
    Dim zsjjwpp As Integer
    zsjjwpp = 1000
    If Sheet4.Range("H10") <= 5 And qx = "��" Then
        zsjjwpp = 1
    End If
    For Each gp In Range("T1_ƥ��[    ����]")
        'If gp.Offset(0, 8) <= 0.5 Then Exit For
        'If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= 0 And gp.Offset(0, 8) < 0.8 And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
        ' ���̣�����<=0,�������¸���ɫ = 37
        
        If gp.Interior.ColorIndex <> 35 And gp.Offset(0, 1) <= zsjjwpp And gp.Offset(0, 11).Interior.ColorIndex = 37 Then
             'gp.Offset(0, 2).Interior.ColorIndex = 29
            If rng5 = "" Then Set rng5 = gp.Offset(0, 2)
            If (gp.Offset(0, 7).Interior.ColorIndex = 38 Or gp.Offset(0, 7) > 0) Then
                Set rng6 = gp.Offset(0, 2)
                Exit For
            End If
        End If
    Next
    
    '�������������������ж��������������һ�����ȡ�⼸����������������4���ǵ�������,Ҫ���̵�
    If Not rng6 = "" Then
        rng6.Interior.ColorIndex = 29
    ElseIf Not rng5 = "" Then
        rng5.Interior.ColorIndex = 29
    End If
    
    
     For Each gp In Range("T2_ƥ��[    ����]")
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
    
   ' Range("T1_ƥ��").Sort "4���ǵ���", 2, , , , , , 1
   ' Range("T2_ƥ��").Sort "4���ǵ���", 2, , , , , , 1
    

    
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


Sub ����()
    Dim rng, lbts, ztlbts As Range
    Dim sb, zsb, jsb, h, i, imax, lbtsss, lbtssszd As Integer
    Dim fd, fd2 As Double
    Dim arr
    Dim gn, outgn, maxgn, fdgn, str, yzgp, gnstrstr, str2 As String
    Dim firstAddress
    gnstrstr = ""
    
    ' ����Դͷ��һ����ͣԭ�����װ�
    Set rng = Sheet7.Range("a:a").Find("�װ�")
    jsb = 0 '�װ��к�
    If Not rng Is Nothing Then jsb = rng.Row + 1
    
    If jsb > 0 Then
        For i = 1 To 256 Step 3
            If Sheet7.Cells(jsb, i) = "" Then Exit For
            gnstrstr = gnstrstr & ";" & Sheet7.Cells(jsb, i)
        Next
    End If
    
    
    '1����"��ԭ��"����������װ���װ�����ͬ�������ͣ�ⵥ��Աȣ�ֻҪ���װ���ͣ�ⵥ������װ���ͣ�ⵥ������װ�����ϱ��̡�
    Set rng = Sheet21.Range("a:a").Find("�װ�")
    sb = 0 '�װ��к�
    If Not rng Is Nothing Then sb = rng.Row + 1
    
    Set rng = Sheet21.Range("a:a").Find("���װ�")
    zsb = 0 '���װ��к�
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
            '��ʼ�Ա�
           ' Set rng = Sheet21.Rows(zsb).Find(Sheet21.Cells(sb, i), , , 1)
           ' If Not rng Is Nothing Then
            '    If rng.Offset(0, 1) > Sheet21.Cells(sb, i + 1) Then
                   ' Sheet21.Cells(sb, i).Interior.ColorIndex = 35
             '   End If

           ' End If
            '4.�ҳ�""��ԭ��"���װ�����̵�����Ʊ�����ĸ���������Ʊ�����ĸ����ж��ȡ��ͣ�ⵥ�����ĸ���������ͣ�ⵥ��ĸ����������Ĳ����
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
'         ' �����¹�����¹ɺ͹���ĸ� ���ҵڶ��ݶӵĸ���
'        If maxgn = "�¹�����¹�" Or maxgn = "����ĸ�" Then
'
'
'            secondName = sortedKeys(0)
'
'            If secondName = "�¹�����¹�" Or secondName = "����ĸ�" Then
'                secondName = sortedKeys(1)
'
'            End If
'            maxgn = maxgn & ";" & secondName
'        End If
'
'        '��ͬ����������ĸ���
'        For i = LBound(sortedKeys) + 1 To UBound(sortedKeys)
'            If dict2(sortedKeys(i)) = imax Then
'                 maxgn = maxgn & ";" & sortedKeys(i)
'            End If
'        Next i
        
        Set dict2 = Nothing '�ر��ֵ�
    End If
    maxgn = gnstrstr

    
    '2����"��ԭ��"���ҵ����壬��ҵ�壬�ƴ�����5���ǵ������Ĺ�Ʊ������������װ�����̵ĸ���ȶԣ��ҳ���ͬ�ĸ��
    
    gn = ""
    outgn = ";"
    yzgp = "" '��ֵ��Ʊ��
    Set rng = Sheet21.Range("a:a").Find("����")
    If Not rng Is Nothing Then
        gn = rng.Offset(2, 2)
        fd = rng.Offset(2, 3)
        yzgp = rng.Offset(2, 1)
    End If
    Set rng = Sheet21.Range("a:a").Find("��ҵ��")
    If Not rng Is Nothing Then
        If fd < rng.Offset(2, 3) Then
            gn = rng.Offset(2, 2)
            fd = rng.Offset(2, 3)
            yzgp = rng.Offset(2, 1)
        End If
    End If
    Set rng = Sheet21.Range("a:a").Find("�ƴ���")
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
    
    'ȡ����ֵ��Ʊ��5���Ƿ�
    Sheet4.Range("H11:H12") = ""
    Sheet4.Range("H11").Interior.ColorIndex = xlNone
    
    Range("������ͣ").Sort "��������", 2, , , , , , 1
    ' �������������Ʊ
    lbts = Sheet15.Range("B2")
    '�����������
    lbtsss = Sheet15.Range("G2").Value
    '�������������Ʊ4���ǵ���
    lbtssszd = 0
    Set rng = Sheet2.Range("b:b").Find(Sheet15.Range("B2"))
    ' ������ͣ4���ǵ���
    If Not rng Is Nothing Then lbtssszd = rng.Offset(0, 9).Value
    '
    
    Range("��1").Sort "4���ǵ���", 2, , , , , , 1
     Range("��1").Sort "��������", 2, , , , , , 1
    Sheet4.Range("h25") = Sheet2.Range("B2")
    Sheet4.Range("h24") = Sheet2.Range("Z2")
    If InStr(Sheet4.Range("H33"), ";" & Sheet2.Range("B2") & ";") Then
        Sheet4.Range("h25") = Sheet2.Range("B3")
        Sheet4.Range("h24") = Sheet2.Range("z3")
    End If
    
    
    Range("��1").Sort "4���ǵ���", 2, , , , , , 1
    Range("��1").Sort "������������", 2, , , , , , 1
    Set ztlbts = Sheet2.Range("B2")
   ' Set rng = Sheet2.Range("b:b").Find(Sheet4.Range("H33"))
    
    
    
  '  If Sheet4.Range("h3") = "�ⵥ��" Then
    
   '     Range("��1").Sort "��������", 2, , , , , , 1
   '     Set rng = Sheet2.Range("b:b").Find(Sheet4.Range("H33"))
   '     '�ĳ��ֶ��������Ʊ����

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
        ' �������������� = table1 ������������
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
    
    ' ������ͣ�������� = table1��������
  '  If lbtsss = Sheet2.Range("P2").Value Then
        ' table1 4���ǵ��� <=  ������ͣ4���ǵ���
     '   If Sheet2.Range("k2") <= lbtssszd Then
      '      Debug.Print "H11--������ͣ---" & lbts
     '       Sheet4.Range("H11") = lbts
     '   Else
     '       Debug.Print "H11--Table1---" & ztlbts
     '       Sheet4.Range("H11") = ztlbts
     '   End If
      '  Sheet4.Range("H11") = Sheet2.Range("B2")
   ' Else
   '     If Sheet4.Range("h3") = "�ⵥ��" Then
   '         Sheet4.Range("H11") = lbts
   '     Else
    '        Sheet4.Range("H11") = ztlbts
    '    End If
   ' End If
    
    Set rng = Sheet2.Range("b:b").Find(Sheet4.Range("H11"))
    If Not rng Is Nothing Then
        If Sheet4.Range("h3") = "�ⵥ��" Then
            If rng.Offset(0, 5) < -0.04 Then Sheet4.Range("H11").Interior.ColorIndex = 35
        Else
            If rng.Offset(0, 4) < -0.04 Then Sheet4.Range("H11").Interior.ColorIndex = 35
        End If
    End If
    
    Range("��1").Sort "120���ǵ���", 2, , , , , , 1
    Sheet4.Range("H12") = Sheet2.Range("B2")
    If Sheet2.Range("k2").Value <= -0.2 Then
        Sheet4.Range("H12").Interior.ColorIndex = 35
    End If
    
    ' ����˹ģʽ ����table1����120���ǵ������������������ͨ��ֵ����100�ڲ���table1��5���ǵ�������0
    For Each rng In Range("��1[  ����]")
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
    
    '3����"table1"���ҵ�5���ǵ������Ĺ�Ʊ�������������̫�Ƽ����������Ʊ����������ȶ���ԭ�������װ�ķ��̵ĸ����ҳ���ͬ�ĸ��
    Set rng = Sheet2.Range("N:N").Find(Evaluate("max(Table1!N:N)"))
    If Not rng Is Nothing Then
        gn = gn & rng.Offset(0, -9)
        '������
        'ɾ�����
       ' If Left(rng.Offset(0, -13), 5) = "SH.68" Then
       '     Sheet4.Range("H35") = "�ƴ���"
       ' ElseIf Left(rng.Offset(0, -13), 5) = "SZ.30" Then
       '     Sheet4.Range("H35") = "��ҵ��"
       ' Else
       '     Sheet4.Range("H35") = "����"
       ' End If
    End If
  '  Debug.Print gn
    If sb > 0 Then
        For i = 1 To 256 Step 3
            If Sheet21.Cells(sb, i) = "" Then Exit For
            '��ʼ�Ա�
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
      
    '�������һ�ְ� ���ǿյģ�����ԭ�����װ�����и�������̵ĸ������ �����Ĳ��ǿ�
   ' If Sheet19.Range("a2") = "" Then
        For i = 1 To 256 Step 3
            If Sheet21.Cells(sb, i) = "" Then Exit For
            '��ʼ�Ա�
            If Sheet21.Cells(sb, i).Interior.ColorIndex <> 35 Then
                If InStr(str2, ";" & Sheet21.Cells(sb, i) & ";") = 0 Then
                    str2 = str2 & Sheet21.Cells(sb, i) & ";"
                End If
            End If
        Next
   ' End If
    
    '���в��Ǹ���
    fd = 0 'Ĭ�ϷⵥΪ��
    If Sheet4.Range("h3") = "�ⵥ��" Then fd = 1 '����ⵥ�ǿ�����ô����fd=1
    str = ";"
    arr = Split(outgn & maxgn & ";" & fdgn & ";" & str2 & ";", ";")
    For i = LBound(arr) To UBound(arr)
        If arr(i) <> "" Then
            If InStr(str, ";" & arr(i) & ";") = 0 Then
                ' ��ҵ����� �Ҳ����ĸ���ֱ�Ӽ���
                Set gn = Range("��ҵ�����[��������]").Find(arr(i), , , 1)
                If gn Is Nothing Then
                  '  str = str & arr(i) & ";"
                Else
                    If fd = 1 Then
                        ' �ⵥ���� ���ж������̵�
                        If gn.Offset(0, 4).Interior.ColorIndex <> 35 And gn.Offset(0, 5).Interior.ColorIndex <> 35 And gn.Offset(0, 6).Interior.ColorIndex <> 35 Then
                            str = str & arr(i) & ";"
                        End If
                    Else
                         ' �ⵥ�أ� ���򾺷�, ��ͣ�ⵥ�� �����̵�
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
    '����
End Sub
Sub ystest()
    MsgBox Sheet21.Range("a2").Interior.ColorIndex
End Sub

Sub ����()
    Dim rng As Range
    Sheet4.Range("h25:h30") = ""
    Sheet4.Range("h25:h30").Interior.Pattern = xlNone
    
    Set rng = Sheet21.Range("a:a").Find("����")
    If Not rng Is Nothing Then
        Sheet4.Range("h25") = rng.Offset(2, 1)
        Sheet4.Range("h26") = rng.Offset(2, 3)
    End If
    Set rng = Sheet21.Range("a:a").Find("��ҵ��")
    If Not rng Is Nothing Then
        Sheet4.Range("h27") = rng.Offset(2, 1)
        Sheet4.Range("h28") = rng.Offset(2, 3)
    End If
    Set rng = Sheet21.Range("a:a").Find("�ƴ���")
    If Not rng Is Nothing Then
        Sheet4.Range("h29") = rng.Offset(2, 1)
        Sheet4.Range("h30") = rng.Offset(2, 3)
    End If
    If Sheet4.Range("h26") > Sheet4.Range("h85") Then Sheet4.Range("h26").Interior.ColorIndex = 35
    If Sheet4.Range("h28") > Sheet4.Range("h87") Then Sheet4.Range("h28").Interior.ColorIndex = 35
End Sub

Sub ������װ�()
    Dim a As Range
    Dim sb, i As Integer
    Dim gn As String
 
    gn = ";"
    For Each a In Range("��ҵ�����[��������]")
        If a.Interior.Color = 13421823 Or a.Offset(0, 3).Interior.Color = 13421823 Then
            gn = gn & a & ";"
        End If
    Next
    
    Set a = Sheet21.Range("a:a").Find("�װ�")
    sb = 0 '�װ��к�
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

Sub ������ʽ()
    
'    Range("T1_ƥ��").FormatConditions.Delete
'    Range("T2_ƥ��").FormatConditions.Delete
    
'    With Union(Range("T1_ƥ��[��������]"), Range("T2_ƥ��[��������]")).FormatConditions _
'        .Add(Type:=xlCellValue, Operator:=xlGreater, Formula1:="=0.08")
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
    
'    With Union(Range("T1_ƥ��[��������]"), Range("T2_ƥ��[��������]")).FormatConditions _
'        .Add(Type:=xlCellValue, Operator:=xlGreaterEqual, Formula1:="=100")
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Union(Range("T1_ƥ��[25����ͣ����]"), Range("T2_ƥ��[25����ͣ����]")).FormatConditions _
'        .Add(Type:=xlCellValue, Operator:=xlLess, Formula1:="=1")
'        .Interior.ColorIndex = 35
'        .Font.ColorIndex = 14
'    End With
    
    
'    With Union(Range("T1_ƥ��[��ҵ����]"), Range("T2_ƥ��[��ҵ����]")).FormatConditions _
'        .Add(Type:=xlTextString, String:="����", TextOperator:=xlContains)
'        .Font.Color = -16383844
'    End With
    
'    Range("T1_ƥ��").AutoFilter Field:=10, Criteria1:="<>*����*"
'    On Error GoTo line1
'    Range("T1_ƥ��[��ҵ����]").SpecialCells(12).ClearContents
'line1:
'    Range("T1_ƥ��").AutoFilter Field:=10
'
'    Range("T2_ƥ��").AutoFilter Field:=10, Criteria1:="<>*����*"
'    On Error GoTo line2
'    Range("T2_ƥ��[��ҵ����]").SpecialCells(12).ClearContents
'line2:
'    Range("T2_ƥ��").AutoFilter Field:=10
'
'===============================================
'    With Range("T1_ƥ��[25����ͣ����]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T1_ƥ��[������������]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T1_ƥ��[��������]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T2_ƥ��[��ͣ��ʱ��]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T2_ƥ��[25����ͣ����]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'    With Range("T2_ƥ��[������������]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.Color = 13551615
'        .Font.Color = -16383844
'    End With
'==========================================
'    With Range("T1_ƥ��[��ʱ����]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.ColorIndex = 45
'    End With
'    With Range("T2_ƥ��[��ʱ����]").FormatConditions.AddTop10
'        .Rank = 1
'        .Interior.ColorIndex = 45
'    End With
    'Debug.Print Range("R8").font.colorindex
    
    
'==============================================
'    Dim a As Range
'    For Each a In Range("T1_ƥ��[��������]")
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
'    For Each a In Range("T2_ƥ��[��������]")
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


Sub ����ֱ�2()
    Dim a As Range '���������Ԫ��
    Dim b As Range '��������ƥ�䵥Ԫ��
    Dim ������, c, r As Integer
    
    '����ϴν��
    Sheet5.Cells.Clear
    Sheet7.Cells.Clear
'    Range("T1_ƥ��").Sort Header:=xlYes, key1:=Range("T1_ƥ��[�����Ƿ�]"), Order1:=xlDescending
'    Range("T2_ƥ��").Sort Header:=xlYes, key1:=Range("T2_ƥ��[�����Ƿ�]"), Order1:=xlDescending
    ������ = -1
    For Each a In Range("��ҵ�����[ʵ����ͨ]") '���������б�ĸ���
        If a.Interior.Color <> 16777215 Then '�������û�е�ɫ��
            ������ = ������ + 1
            c = ������ * 4 + 1
            
            '��ҵ��
            r = 3
            Sheet5.Cells(1, c) = a.Offset(0, -2)  'д��������
            Sheet5.Cells(2, c) = "����"
            Sheet5.Cells(2, c + 1) = "����"
            Sheet5.Cells(2, c + 2) = "�����Ƿ�"
            For Each b In Range("��[��������]")
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
            '����
    ������ = -1
    For Each a In Range("�������[ʵ����ͨ]") '���������б�ĸ���
        If a.Interior.Color <> 16777215 Then '�������û�е�ɫ��
            ������ = ������ + 1
            c = ������ * 4 + 1
            
            '��ҵ��
            r = 3
            Sheet7.Cells(1, c) = a.Offset(0, -2)  'д��������
            Sheet7.Cells(2, c) = "����"
            Sheet7.Cells(2, c + 1) = "����"
            Sheet7.Cells(2, c + 2) = "�����Ƿ�"
            For Each b In Range("��[��������]")
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

    
    'MsgBox "����ֱ����!"
End Sub

Sub ���ɲ�ѯ()
    Dim tj, gn1 As String
    Dim rng, gn As Range
    Application.ScreenUpdating = False
    '��ȥ����ǰ����ɫ
    Range("��ҵ�����[����]").Interior.Pattern = xlNone
    'Range("�������[����]").Interior.Pattern = xlNone
    Sheet4.Range("H30").Interior.Pattern = xlNone
    'tj = InputBox("�������Ʊ����")
    tj = Sheet4.Range("H30")
    If tj = "" Then Exit Sub
    '��ѯ�����Ʊ�ĸ���
    gn1 = ""
    Set rng = Range("��1[    ����]").Find(tj)
    If rng Is Nothing Then Set rng = Range("��2[    ����]").Find(tj)
    If Not rng Is Nothing Then
        gn1 = rng.Offset(0, 3)
        If rng.Offset(0, 5) < 1 Then Sheet4.Range("H30").Interior.ColorIndex = 35
    End If
    If Sheet4.Range("H30").Interior.ColorIndex <> 35 Then
        Set rng = Range("T1_ƥ��[    ����]").Find(tj)
        If rng Is Nothing Then Set rng = Range("T2_ƥ��[    ����]").Find(tj)
        If rng Is Nothing Then Sheet4.Range("H30").Interior.ColorIndex = 35
    End If
    
    'ƥ����Щ����
    For Each gn In Range("��ҵ�����[��������]")
        If InStr(gn1, ";" & gn & ";") > 0 Then gn.Offset(0, 1).Interior.ColorIndex = 22
    Next
'    For Each gn In Range("�������[��������]")
'        If InStr(gn1, ";" & gn & ";") > 0 Then gn.Offset(0, 1).Interior.ColorIndex = 22
'    Next
    Application.ScreenUpdating = True
End Sub

