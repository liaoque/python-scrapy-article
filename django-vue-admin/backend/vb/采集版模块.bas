Attribute VB_Name = "�ɼ���ģ��"


Sub tonum()

    Dim c As Integer
    Dim r As Integer
    Dim arr
    
    For i = 1 To 14
        r = Worksheets(i).Range("a1").End(xlDown).Row
        c = Worksheets(i).Range("a1").End(xlToRight).Column
        arr = Worksheets(i).Cells(2, 1).Resize(r - 1, c)
        Worksheets(i).Cells(2, 1).Resize(r - 1, c) = arr
    Next
    
    'MsgBox "��תΪ����"

End Sub

Sub �������ɳ�����()
    Debug.Print Now & "�������ɳ�����"
    On Error Resume Next
    Sheet1.ListObjects("��").Unlist
    Sheet1.Cells.ClearFormats
    Sheet1.ListObjects.Add(xlSrcRange, Sheet1.Range("a1").CurrentRegion, , xlYes).Name = "��"
    Sheet2.ListObjects("��1").Unlist
    Sheet2.Cells.ClearFormats
    Sheet2.ListObjects.Add(xlSrcRange, Sheet2.Range("a1").CurrentRegion, , xlYes).Name = "��1"
    Sheet16.ListObjects("qs").Unlist
    Sheet16.Cells.ClearFormats
    Sheet16.ListObjects.Add(xlSrcRange, Sheet16.Range("a1").CurrentRegion, , xlYes).Name = "qs"
End Sub
Sub cc()
   ' Range("��1[����]") = ""
     Debug.Print Sheet27.UsedRange.Rows.Count
End Sub

Sub ����ǰ��ֺ�()
    'If Left(Sheet1.Range("E2"), 1) = ";" Then Exit Sub
    Debug.Print Now & "����ǰ��ֺ�"
    Dim rng As Range
    For Each rng In Sheet1.Range("��[��������]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
    Next
    Sheet2.Range("s1") = "����" '�Ȱ��������
    fd = 0 'Ĭ�ϷⵥΪ��
    If Sheet4.Range("h3") = "�ⵥ��" Then fd = 1 '����ⵥ�ǿ�����ô����fd=1
    Range("��1[����]") = ""
    For Each rng In Sheet2.Range("��1[��������]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
        
        'rng.Offset(0, 14) = "" '�Ȱ��������
        If fd = 0 Then '����ⵥ��
            If rng.Offset(0, 1) >= 0.05 Then rng.Offset(0, 14) = "��ͣ����"
            If rng.Offset(0, 1) < -0.095 Then rng.Offset(0, 14) = "��ͣ����"
        Else '���򣨷ⵥ����
            If rng.Offset(0, 2) > 0.095 Then rng.Offset(0, 14) = "��ͣ����"
            If rng.Offset(0, 2) < -0.095 Then rng.Offset(0, 14) = "��ͣ����"
            If rng.Offset(0, 4) <> 0 Then '��ֹ���̼�Ϊ0������������Ϊ0
                'If (rng.Offset(0, 4) - rng.Offset(0, 5)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = "��ͣ����" '(���̼�-��ͼ�)/���̼� > 0.095
                If rng.Offset(0, 14) = "" And (rng.Offset(0, 3) - rng.Offset(0, 4)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = "��ͣ����" '��߼�-���̼�)/���̼� > 0.095
            End If
        End If

'        If rng.Offset(0, 2) >= zf Then rng.Offset(0, 14) = "��ͣ����"
'        If rng.Offset(0, 14) = "" And rng.Offset(0, 6) <> 0 Then '�������̼�<>0
'            If (rng.Offset(0, 4) - rng.Offset(0, 5)) / rng.Offset(0, 4) > 0.095 Then rng.Offset(0, 14) = "��ͣ����"
'            'If (rng.Offset(0, 4) - rng.Offset(0, 6)) / rng.Offset(0, 6) > 0.095 Then rng.Offset(0, 14) = "��ͣ����" '(���̼�-�������̼�)/�������̼�
'        End If
'
'        If rng.Offset(0, 14) = "" And rng.Offset(0, 4) <> 0 Then
'            If (rng.Offset(0, 3) - rng.Offset(0, 4)) / rng.Offset(0, 4) > 0.095 Then
'                rng.Offset(0, 14) = "��ͣ����"
'            Else
'
'                If rng.Offset(0, 14) = "" And rng.Offset(0, 2) < -0.095 Then rng.Offset(0, 14) = "��ͣ����"
'            End If
'        End If
'        rng.Offset(0, 14) = qs
    Next
    'Range("��[��������]") = ";" & Range("��[��������]") & ";"
    Range("��[��������]").Replace ";;", ";", 2
    Range("��1[��������]").Replace ";;", ";", 2
    
    'ȥ����Ҫ�ĸ���
    'nogn = "��ʱ���ظ���;��ʱ���ظ����;���յ���˹A��;����ͨ;���ͨ;������ȯ;ת��ȯ���;��ת��Ȩ;��Ȩת��;��������;����;MSCI����;һ��������;ҵ������;�걨����;����;�������ĸ�;�ط�����ĸ�;����ĸ�;����������;���걨Ԥ��;ͬ��˳Ư��100"
    nogn = Sheet4.Range("h39")
    arr = Split(nogn, ";")
    For i = LBound(arr) To UBound(arr)
        If arr(i) <> "" Then
            Range("��[��������]").Replace ";" & arr(i) & ";", ";", 2
            Range("��1[��������]").Replace ";" & arr(i) & ";", ";", 2
        End If
    Next
    Range("��[��������]").Replace "����;", ";", 2
    Range("��1[��������]").Replace "����;", ";", 2
    
    '�ӽ�����ͣȡը��
    Sheet2.Range("t1") = "ը��"
    If Sheet13.Range("a2") <> "" Then
        h = Sheet13.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("��1[  ����]").Find(Sheet13.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 19) = "ը��"
            End If
        Next
    End If
    'ȡ�������µ�
    Sheet2.Range("u1") = "�������¸�"
    If Sheet14.Range("a2") <> "" Then
        h = Sheet14.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("��1[  ����]").Find(Sheet14.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 20) = "�������¸�"
            End If
        Next
    End If
    'ȡһ�ְ�
    Sheet2.Range("v1") = "һ�ְ�"
    If Sheet19.Range("a2") <> "" Then
        h = Sheet19.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("��1[  ����]").Find(Sheet19.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 21) = Sheet19.Range("e" & i)
                Sheet19.Range("h" & i) = rng.Offset(0, 15) + 1
            End If
        Next
    End If
    
        'ȡ�װ壨��������Ϊ1���Ĺ�Ʊ��ͣ�ⵥ��
    Sheet2.Range("x1") = "�װ�"
    If Sheet15.Range("a2") <> "" Then
        h = Sheet15.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Range("��1[  ����]").Find(Sheet15.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                If Sheet15.Range("g" & i) = 1 Then rng.Offset(0, 23) = Sheet15.Range("i" & i)
            End If
        Next
    End If
    
'    '������ͣ
'    Sheet2.Range("w1") = "��ͣ�ⵥ��"
'    If Sheet15.Range("a2") <> "" Then
'        h = Sheet15.Range("a1").End(xlDown).Row
'        For i = 2 To h
'            Set rng = Range("��1[  ����]").Find(Sheet15.Range("a" & i), , , 1)
'            If Not rng Is Nothing Then
'                rng.Offset(0, 22) = Sheet15.Range("i" & i)
'            End If
'        Next
'    End If
    Range("��[�ǵ���]").NumberFormatLocal = "0.00% "
    Range("��1[�ǵ���]").NumberFormatLocal = "0.00% "
    Range("��[�����Ƿ�]").NumberFormatLocal = "0.00% "
    Range("��1[�����Ƿ�]").NumberFormatLocal = "0.00% "
End Sub
Sub ������������()
    Debug.Print Now & "������������"
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng, gp As Range
    Dim dic As Object
    Dim gnstr As String
    Dim arr
    Dim i As Integer
    Dim js_cy, js_zb, a, cyset, zbset, lz, jj
    a = 0
    
    'ȡ����Ч����ϲ���һ�����ַ���
 '   cyset = Range("����ֵ[����ֵ]").Rows(1)
 '   zbset = Range("����ֵ[����ֵ]").Rows(2)
 '   For Each rng In Sheet1.Range("��[��������]")
 '       If Left(rng.Offset(0, -4), 5) = "SZ.30" Or Left(rng.Offset(0, -4), 6) = "SH.688" Or Left(rng.Offset(0, -4), 6) = "SH.689" Then '��ҵ
'            If rng.Offset(0, 5) > cyset Then gnstr = gnstr & rng
'        Else '����
'            If rng.Offset(0, 5) > zbset Then gnstr = gnstr & rng
'        End If
'    Next

    '���ڷⵥ�����������һ�ְ��ȡ
    ' �ⵥ�����������������ͣ��ȡ
    If Sheet4.Range("h3") = "�ⵥ��" Then
        For Each rng In Sheet15.Range("A2:A3000")
            If rng = "" Then Exit For
            
            Set gp = Sheet2.Range("A:A").Find(rng, , , 1)
            If Not gp Is Nothing Then
              gnstr = gnstr & gp.Offset(0, 4)
            End If
            
        Next
    Else
        For Each rng In Sheet19.Range("A2:A3000")
            If rng = "" Then Exit For
            If rng.Offset(0, 4) > 0 Then
                Set gp = Sheet2.Range("A:A").Find(rng, , , 1)
                If Not gp Is Nothing Then
                 gnstr = gnstr & gp.Offset(0, 4)
                End If
            End If
        Next
    End If



    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            'If InStr(nogn, ";" & arr(i) & ";") < 1 Then 'ȥ����Ҫ�ĸ���
                'If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
'                        js_cy = Evaluate("COUNTIFS(��[ [  ����] ],""SZ.30*"",��[��������],""*;" & arr(i) & ";*"")")
'                        js_zb = Evaluate("SUMPRODUCT(IF(ISERROR(FIND(""SZ.30"",��[  ����])),1,0),IF(ISERROR(FIND("";" & arr(i) & ";"",��[��������])),0,1))")
'                        dic(arr(i)) = Array(js_cy, js_zb)
                        dic(arr(i)) = 1 'Evaluate("COUNTIFS(��[��������],""*;" & arr(i) & ";*"")")
                    End If
                'End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    If Range("��ҵ�����[#data]").Rows.Count > 1 Then Range("��ҵ�����[#data]").Delete Shift:=xlShiftUp '���ԭ��
    Sheet4.Range("a2:g10000").Clear
    Range("��ҵ�����[ʵ����ͨ]").NumberFormatLocal = "0.00"
    Range("��ҵ�����[[#Headers],[��������]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    'Range("��ҵ�����[[#Headers],[����]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)

    Set dic = Nothing '�ر��ֵ�
    
    Range("��ҵ�����[��������]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("��ҵ�����[����]").Replace "1", "", 1 '1����ȫƥ��
    'Range("��ҵ�����[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp

    '������¸�����������
    Set rng = Sheet7.Range("a:a").Find("�������¸�")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                
                ' ����ͣԭ��Ĵ������¸ߣ��ϲ�����Ľ��
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 1) = lz & " | " & rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 1) = lz & " | 0"
                    'a.Offset(0, 1).Interior.ColorIndex = 35 '������Ϊ0����
                End If
                'If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35

        Next
    End If
       '������¸�����������
    Set rng = Sheet21.Range("a:a").Find("�������¸�")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
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
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        Next
    End If
    
    '�񾺷�����������
    Set rng = Sheet7.Range("a:a").Find("�񾺷�")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    Sheet4.Range("d1") = "�񾺷���"
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
                a.Offset(0, 3) = 0
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 3) = lz
                    a.Offset(0, 4) = rng.Offset(0, 1)
                Else
                    a.Offset(0, 4) = 0
                End If
                
                If a.Offset(0, 4) <= 0 And a.Offset(0, 3) > 0 Then a.Offset(0, 4).Interior.ColorIndex = 35    'С�ڵ���0�ı���
                
                'If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35

        Next
    End If
    '����
    Range("��ҵ�����").Sort "�񾺷���", 2, , , , , , 1
    
    '����ⵥ����D�и�Ϊ��ͣ����ԭ��
    If Sheet4.Range("h3") = "�ⵥ��" Then
        Sheet4.Range("d1") = "��ͣ������"
        For Each a In Range("��ҵ�����[��������]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(3).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - 4
                End If
                a.Offset(0, 3) = lz
                If lz < 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
            End If
        Next
    
        '����
        Range("��ҵ�����").Sort "��ͣ������", 2, , , , , , 1
    End If
    '�򾺷�����������
    Set rng = Sheet21.Range("a:a").Find("�񾺷�")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    If a.Offset(0, 3) > 0 And rng.Offset(0, 1) > a.Offset(0, 4) Then a.Offset(0, 4).Interior.ColorIndex = 35 '��Ƚ�����
                    a.Offset(0, 4) = a.Offset(0, 4) & " | " & rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 4) = a.Offset(0, 4) & " | 0"
                End If
                
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        Next
    End If
    
    '�¼�
    Set rng = Sheet21.Range("a:a").Find("��ͣ����")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
                
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    arr = Split(a.Offset(0, 4), " | ")
                    lz = Round(rng.Offset(0, 1) / 100000000, 2)
                    If a.Offset(0, 3) > 0 And lz > arr(0) * 1 Then a.Offset(0, 4).Interior.ColorIndex = 35  '��Ƚ�����
                    a.Offset(0, 4) = a.Offset(0, 4) & " | " & lz
                    
                Else
                    a.Offset(0, 4) = a.Offset(0, 4) & " | 0"
                End If
                
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        Next
    End If
    
   '   For Each a In Range("��ҵ�����[��������]")
    '
     '       If a.Offset(0, 1) = "0 | 0 | 0" Then
      '          a.Offset(0, 1).Interior.ColorIndex = xlNone
       '     End If
        '
       '     If a.Offset(0, 4) = "0 | 0 | 0" Then
        '        a.Offset(0, 4).Interior.ColorIndex = xlNone
       '     End If
   '
    '    Next
    
        '�������зⵥ�ܺ�
    If Sheet4.Range("h3") = "�ⵥ��" Then
        If Sheet5.Range("a2") <> "" Then
            h = Sheet5.Range("a1").End(xlDown).Row
            Debug.Print "����=" & h
            For Each a In Range("��ҵ�����[��������]")
                'If a.Offset(0, 3) = 0 Then Exit For
                'If a.Offset(0, 3) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 Then
                    a.Offset(0, 5) = Evaluate("round(SUMIFS(���ǹ�Ʊ!E2:E" & h & ",���ǹ�Ʊ!F2:F" & h & ",""*;" & a & ";*"")/100000000,2)")
                    If a.Offset(0, 5) < (Left(a.Offset(0, 4), InStr(a.Offset(0, 4), " ") - 1)) * 1 Then a.Offset(0, 5).Interior.ColorIndex = 35
                    If a.Offset(0, 5) > 0 And a.Offset(0, 5) > (Left(a.Offset(0, 4), InStr(a.Offset(0, 4), " ") - 1)) * 1 Then a.Offset(0, 4).Interior.Pattern = xlNone
                'End If
            Next
        End If
    End If
        '�����ͣ�ⵥ�ܺ�
    
    If Sheet5.Range("a2") <> "" Then
        h = Sheet5.Range("i1").End(xlDown).Row
        Debug.Print "����=" & h
        
        If Sheet4.Range("h3") = "�ⵥ��" Then
             Sheet4.Range("g1") = "��ͣ�ⵥ��"
            For Each a In Range("��ҵ�����[��������]")
               
                a.Offset(0, 6) = Evaluate("round(SUMIFS(���ǹ�Ʊ!M2:M" & h & ",���ǹ�Ʊ!N2:N" & h & ",""*;" & a & ";*"")/100000000,2)")
                If a.Offset(0, 6) > a.Offset(0, 5) Then a.Offset(0, 6).Interior.ColorIndex = 35
            Next
        Else
            Sheet4.Range("g1") = "��ͣδƥ��"
            For Each a In Range("��ҵ�����[��������]")
                
                jj = Evaluate("SUMIFS(���ǹ�Ʊ!L2:L" & h & ",���ǹ�Ʊ!N2:N" & h & ",""*;" & a & ";*"")")
                If jj > 0 Then jj = 0
                If jj < 0 Then jj = Abs(jj)
                a.Offset(0, 6) = jj
                arr = Split(a.Offset(0, 4), " | ")
                 '��ͣδƥ�� > �񾺷� ����
                If a.Offset(0, 6) > arr(0) * 1 Then a.Offset(0, 6).Interior.ColorIndex = 35
                
                ' ��ͣδƥ�� ����ɫ�� �ҽ񾺷����� 0�� ��ͣδƥ�� ��ԭ�� ��ɫ
                If a.Offset(0, 6).Interior.ColorIndex = 35 And a.Offset(0, 3) = 0 Then a.Offset(0, 6).Interior.Pattern = xlNone
                ' a.Offset(0, 6).Interior.ColorIndex = 35
            Next
        End If
        
    End If
    
    
 '   '���㴴ҵ��ʵ����ͨ
 '   For Each a In Range("��ҵ�����[��������]")
 '       If a.Offset(0, 1).Interior.ColorIndex <> 35 Or a.Offset(0, 4).Interior.ColorIndex <> 35 Then
 '          'a.Offset(0, 2) = Evaluate("round(AVERAGEIFS(��[�����Ƿ�],��[��������],""*;" & a & ";*""),4)")
 '           a.Offset(0, 2) = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & a & ";*"")/100000000,2)")
 '           'If a.Offset(0, 2) < 9000 Then a.Offset(0, 3).Interior.ColorIndex = 35
 '       'Else
 '           'a.Offset(0, 2) = "-"
 '       End If
 '   Next
 
End Sub
Sub sssa()
    arr = Split([b3], " | ")
    MsgBox "ֵΪ:" & arr(1)
End Sub
Sub �������������()
    Debug.Print Now & "������������"
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim gnstr As String
    Dim arr
    Dim i As Integer
    Dim js_cy, js_zb, a, cyset, zbset, lz

    
    'ȡ����Ч����ϲ���һ�����ַ���
    cyset = Range("����ֵ[����ֵ]").Rows(1)
    zbset = Range("����ֵ[����ֵ]").Rows(2)
    For Each rng In Sheet1.Range("��[��������]")
        If Left(rng.Offset(0, -4), 5) = "SZ.30" Or Left(rng.Offset(0, -4), 6) = "SH.688" Or Left(rng.Offset(0, -4), 6) = "SH.689" Then '��ҵ
            If rng.Offset(0, 5) > cyset Then gnstr = gnstr & rng
        Else '����
            If rng.Offset(0, 5) > zbset Then gnstr = gnstr & rng
        End If
    Next
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            'If InStr(nogn, ";" & arr(i) & ";") < 1 Then 'ȥ����Ҫ�ĸ���
                'If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
'                        js_cy = Evaluate("COUNTIFS(��[ [  ����] ],""SZ.30*"",��[��������],""*;" & arr(i) & ";*"")")
'                        js_zb = Evaluate("SUMPRODUCT(IF(ISERROR(FIND(""SZ.30"",��[  ����])),1,0),IF(ISERROR(FIND("";" & arr(i) & ";"",��[��������])),0,1))")
'                        dic(arr(i)) = Array(js_cy, js_zb)
                        dic(arr(i)) = Evaluate("COUNTIFS(��[��������],""*;" & arr(i) & ";*"")")
                    End If
                'End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    If Range("��ҵ�����[#data]").Rows.Count > 1 Then Range("��ҵ�����[#data]").Delete Shift:=xlShiftUp '���ԭ��
    Range("��ҵ�����[ʵ����ͨ]").NumberFormatLocal = "0.00"
    Range("��ҵ�����[[#Headers],[��������]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    Range("��ҵ�����[[#Headers],[����]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)

    Set dic = Nothing '�ر��ֵ�
    
    Range("��ҵ�����[��������]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("��ҵ�����[����]").Replace "1", "", 1 '1����ȫƥ��
    Range("��ҵ�����[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    
    
    'Range("��1").Sort "��������", 2, , , , , , 1

    
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
    Debug.Print Now & "������������--������ͣ��ͣ"
    '��ͣ����ԭ��С��2����
    For Each a In Range("��ҵ�����[��������]")
        If a.Offset(0, 1) > 0 Then
            lz = 0
            'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
            Set rng = Sheet7.Rows(3).Find(a, , , 1)
            If Not rng Is Nothing Then
                lz = rng.End(xlDown).Row - 4
            End If
            a.Offset(0, 3) = lz
            If lz < 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
        End If
    Next
    '��ͣ����ԭ�����1����
    Set rng = Sheet7.Range("a:a").Find("��ͣ����")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    lz = rng.End(xlDown).Row - h - 1
                End If
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
            End If
        Next
    End If
    
    
    '�񾺷�����������
    Set rng = Sheet7.Range("a:a").Find("��ͣ����")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                Set rng = Sheet7.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 4) = rng.Offset(0, 1)
                    
                Else
                    a.Offset(0, 4) = 0
                End If
                If a.Offset(0, 4) <= 0 Then a.Offset(0, 4).Interior.ColorIndex = 35
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35

            End If
        Next
    End If
    
    '�򾺷�����������
    Set rng = Sheet21.Range("a:a").Find("��ͣ����")
    h = 0
    If Not rng Is Nothing Then
        h = rng.Row + 1
    End If
    If h > 0 Then
        For Each a In Range("��ҵ�����[��������]")
            If a.Offset(0, 1) > 0 Then
                lz = 0
                'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
                Set rng = Sheet21.Rows(h).Find(a, , , 1)
                If Not rng Is Nothing Then
                    'lz = rng.End(xlDown).Row - h - 1
                    a.Offset(0, 5) = rng.Offset(0, 1)
                    If a.Offset(0, 5) > a.Offset(0, 4) Then a.Offset(0, 5).Interior.ColorIndex = 35
                End If
                'a.Offset(0, 4) = lz '�ѹ�Ʊ��������������ĵ�����
                'If lz > 1 Then a.Offset(0, 3).Interior.ColorIndex = 35
            End If
        Next
    End If
    
'    '��ͣ����С��2����
'    For Each a In Range("��ҵ�����[��������]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            'a.Offset(0, 2) = Evaluate("Maxifs(��1[��������],��1[��������],""*;" & a & ";*"")")
'            Set rng = Sheet6.Range("a:a").Find(a)
'            If Not rng Is Nothing Then
'                lz = rng.Offset(0, 1)
'            End If
'            a.Offset(0, 3) = lz
'            If lz < 2 Then a.Offset(0, 3).Interior.ColorIndex = 35
'        End If
'    Next
'
'    '��ͣ�������2����
'    For Each a In Range("��ҵ�����[��������]")
'        If a.Offset(0, 1) > 0 Then
'            lz = 0
'            Set rng = Sheet6.Range("d:d").Find(a)
'            If Not rng Is Nothing Then
'                lz = rng.Offset(0, 1)
'            End If
'            a.Offset(0, 4) = lz
'            If lz >= 2 Then a.Offset(0, 4).Interior.ColorIndex = 35
'        End If
'    Next

    '����
    Range("��ҵ�����").Sort "��ͣ����", 2, , , , , , 1
    
'    For Each a In Range("��ҵ�����[��������]")
'        'If a.Offset(0, 3) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 Then
'            a.Offset(0, 6) = Evaluate("round(SUMIFS(��1[��ͣ�ⵥ��],��1[��������],""*;" & a & ";*"")/100000000,4)")
'            If a.Offset(0, 5) <> "" And a.Offset(0, 6) > a.Offset(0, 5) Then a.Offset(0, 5).Interior.ColorIndex = 0
'            If a.Offset(0, 6) > a.Offset(0, 4) Then a.Offset(0, 4).Interior.ColorIndex = 0
'        'End If
'    Next
    '�������зⵥ�ܺ�
    If Sheet4.Range("h3") = "�ⵥ��" Then
        If Sheet5.Range("a2") <> "" Then
            h = Sheet5.Range("a1").End(xlDown).Row
            Debug.Print "����=" & h
            For Each a In Range("��ҵ�����[��������]")
                If a.Offset(0, 3) = 0 Then Exit For
                'If a.Offset(0, 3) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 Then
                    a.Offset(0, 6) = Evaluate("round(SUMIFS(���ǹ�Ʊ!E2:E" & h & ",���ǹ�Ʊ!F2:F" & h & ",""*;" & a & ";*"")/100000000,2)")
                    If a.Offset(0, 5) <> "" And a.Offset(0, 6) > a.Offset(0, 5) Then a.Offset(0, 5).Interior.ColorIndex = 0
                    If a.Offset(0, 6) <= a.Offset(0, 4) Then
                        a.Offset(0, 4).Interior.ColorIndex = 35
                        a.Offset(0, 5).Interior.ColorIndex = 35
                    Else
                        a.Offset(0, 4).Interior.ColorIndex = 0
                        a.Offset(0, 5).Interior.ColorIndex = 0
                    End If
                'End If
            Next
        End If
    End If
    Debug.Print Now & "������������--����ʵ����ͨ"
    '���㴴ҵ��ʵ����ͨ
    For Each a In Range("��ҵ�����[��������]")
        If a.Offset(0, 1) > 0 And a.Offset(0, 3).Interior.ColorIndex <> 35 And a.Offset(0, 4).Interior.ColorIndex <> 35 And a.Offset(0, 5).Interior.ColorIndex <> 35 Then
            'a.Offset(0, 2) = Evaluate("round(AVERAGEIFS(��[�����Ƿ�],��[��������],""*;" & a & ";*""),4)")
            a.Offset(0, 2) = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & a & ";*"")/100000000,2)")
            'If a.Offset(0, 2) < 9000 Then a.Offset(0, 3).Interior.ColorIndex = 35
        'Else
            'a.Offset(0, 2) = "-"
        End If
    Next
End Sub

Sub tjtest()
    a = "���ز�"
    Debug.Print Evaluate("round(SUMIFS(���ǹ�Ʊ!E2:E214,���ǹ�Ʊ!F2:F214,""*;" & a & ";*"")/100000000,4)")
End Sub

Sub �ºϲ�����()
    Dim i, j, dm
    Dim arr
    Dim rng As Range
    Dim Wb As Workbook
    If Sheet4.Range("H100") = Evaluate("round(sum(��1[��߼�]),2)") Then
        If MsgBox("��⵽�Ѿ��ϲ��������ˣ�ȷ��Ҫ�ظ��ϲ���", 1) <> vbOK Then Exit Sub
    Else
        If MsgBox("��⵽���ݸ��º�û�кϲ������ȷ��Ҫ�ϲ���?", 1) <> vbOK Then Exit Sub
    End If
    
    Application.ScreenUpdating = False
    �������ɳ�����
    '����ȥ������
'    Range("��[��������]").Replace "��", ";", 2
'    Range("��1[��������]").Replace "��", ";", 2
'    Range("��2[��������]").Replace "��", ";", 2
'    Range("��[��������]").Replace "��", ";", 2
'    Range("��1[��������]").Replace "��", ";", 2
'    Range("��2[��������]").Replace "��", ";", 2
'    Sheet2.Range("k1") = "��������"
'    Sheet3.Range("k1") = "��������"
    'Open ThisWorkbook.Path & "\����.txt" For Input As #1
    Set Wb = GetObject(ThisWorkbook.Path & "\data.xlsx")
    i = 2
    With Wb.Sheets("table3")
        'Do While Not EOF(1)
        Do While .Range("a" & i) <> ""
            'Line Input #1, j
            j = .Range("c" & i)
            'arr = Split(j, "|")
            
            Set rng = Range("��[  ����]").Find(.Range("a" & i), LookAt:=xlPart)  'ģ�����ң���Ԫ��ƥ��ģʽ
            If Not rng Is Nothing Then
                dm = Replace(.Range("c" & i), ",", ";") & ";" & rng.Offset(0, 2)
                'dm = ";" & dm & "��"
                'dm = Left(rng.Offset(0, 4).Value, Len(rng.Offset(0, 4).Value) - 1) & ";" & dm
                rng.Offset(0, 4).Value = rng.Offset(0, 4).Value & ";" & dm & ";"
                'rng.Offset(0, 4).Value = ";" & dm & ";"
            End If
            
            Set rng = Range("��1[  ����]").Find(.Range("a" & i), LookAt:=xlPart) 'ģ�����ң���Ԫ��ƥ��ģʽ
            'If rng Is Nothing Then Set rng = Range("��2[  ����]").Find(.Range("a" & i), LookAt:=xlPart)
            If Not rng Is Nothing Then
                dm = Replace(.Range("c" & i), ",", ";") & ";" & rng.Offset(0, 2)
                'dm = ";" & dm & "��"
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
    
    For Each rng In Sheet1.Range("��[��������]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
    Next
    For Each rng In Sheet2.Range("��1[��������]")
        If Left(rng, 1) <> ";" Then rng.Value = ";" & rng
        If Right(rng, 1) <> ";" Then rng.Value = rng & ";"
    Next
    
    '����ȥ�ظ��ֺ�
    Range("��[��������]").Replace ";;", ";", 2
    Range("��1[��������]").Replace ";;", ";", 2

    '����ȥ�ո�
    Range("��[��������]").Replace " ", "", 2
    Range("��1[��������]").Replace " ", "", 2
    'Range("��2[��������]").Replace " ", "", 2
    '����ȥ�ո����
    '�����豸�����
    Range("��[��������]").Replace ";�����豸;", ";����;", 2
    Range("��1[��������]").Replace ";�����豸;", ";����;", 2
     Range("��[��������]").Replace ";����������;", ";����;", 2
    Range("��1[��������]").Replace ";����������;", ";����;", 2
    'Range("��2[��������]").Replace ";�����豸;", ";����;", 2
    
    Range("��[��������]").Replace ";������;", ";����;", 2
    Range("��1[��������]").Replace ";������;", ";����;", 2

    Range("��[��������]").Replace ";���;", ";����;", 2
    Range("��1[��������]").Replace ";���;", ";����;", 2
    'Range("��2[��������]").Replace ";���;", ";����;", 2

    Range("��[��������]").Replace ";������ʸĸ�;", ";����ĸ�;", 2
    Range("��1[��������]").Replace ";������ʸĸ�;", ";����ĸ�;", 2
    Range("��[��������]").Replace ";�ط����ʸĸ�;", ";����ĸ�;", 2
    Range("��1[��������]").Replace ";�ط����ʸĸ�;", ";����ĸ�;", 2
    'Range("��2[��������]").Replace ";�������ĸ�;", ";����ĸ�;", 2

    Range("��[��������]").Replace ";�������;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";�������;", ";�¹�����¹�;", 2
    Range("��[��������]").Replace ";���¹�;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";���¹�;", ";�¹�����¹�;", 2
    Range("��[��������]").Replace ";��׼�ƴ��¹�;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";��׼�ƴ��¹�;", ";�¹�����¹�;", 2
    Range("��[��������]").Replace ";ע���ƴ��¹�;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";ע���ƴ��¹�;", ";�¹�����¹�;", 2
    
'    Range("��[��������]").Replace What:=";??���ʸĸ�;", Replacement:=";", LookAt:=xlPart, _
'        MatchCase:=False, SearchFormat:=False, ReplaceFormat:=False
'    Range("��1[��������]").Replace What:=";??���ʸĸ�;", Replacement:=";", LookAt:=xlPart, _
'        MatchCase:=False, SearchFormat:=False, ReplaceFormat:=False
    
    Sheet4.Range("H100") = Evaluate("round(sum(��1[��߼�]),2)")
    Application.ScreenUpdating = True
    re
    MsgBox "����ϲ����!"
End Sub
Sub test()
   ' Range("��1[#ALL]").AdvancedFilter 2, Sheet4.Range("an1:ap2"), Sheet4.Range("j1:s1")
   ' Range("��1[#ALL]").AdvancedFilter 2, Sheet4.Range("as1:au2"), Sheet4.Range("x1:ag1")
    Debug.Print Sheet26.Cells(1, 2)
    Range("��1").Sort "4���ǵ���", 2, , , , , , 1
    Range("��1").Sort "��������", 2, , , , , , 1
    Dim CurrentDate As Date
    CurrentDate = Date
    Dim cybgd As String '��ҵ��߶�
    Dim lastRow As Long
    With Sheet15
        lastRow = .Cells(.Rows.Count, 1).End(xlUp).Row - 1
    End With

    
    For i = 2 To 200 Step 1
        If InStr(Sheet2.Range("a" & i), ".300") > 0 Or InStr(Sheet2.Range("a" & i), ".301") > 0 Then
            cybgd = Sheet2.Range("z" & i)
            Exit For
        End If
        
    Next
    
    For i = 2 To 200 Step 1
        If Sheet27.Cells(i, 1) = "" Then
            
            Sheet27.Cells(i, 1) = CurrentDate
            Sheet27.Cells(i, 1).Offset(0, 1) = lastRow
            
            Sheet27.Cells(i, 1).Offset(0, 2) = Evaluate("COUNTIFS(��1[ [��ͣ�ⵥ��] ],"">0"")")
            Sheet27.Cells(i, 1).Offset(0, 3) = Evaluate("COUNTIFS(��1[ [��������] ],""1"")")
            Sheet27.Cells(i, 1).Offset(0, 4) = Evaluate("COUNTIFS(��1[ [��������] ],"">1"")")
            Sheet27.Cells(i, 1).Offset(0, 5) = Sheet2.Range("z2") ' �ܸ߶�
        Sheet27.Cells(i, 1).Offset(0, 6) = Sheet4.Range("H25") ' ��ͷ
        
        
'            If Not rng Is Nothing Then lz = rng.Offset(0, 3)
        Set rng = Sheet5.Range("B:B").Find(Sheet27.Cells(i, 1).Offset(0, 6))  ' ��ͷ ��ͣԭ��
        If Not rng Is Nothing Then
            Sheet27.Cells(i, 1).Offset(0, 7) = rng.Offset(0, 4) ' ��ͷ
            Debug.Print "SUMIFS(���Ǵ����[��ͣ�ⵥ��],���Ǵ����[��ͣ����ԭ��],""*" & rng.Offset(0, 4) & "*"")"
            
            Sheet27.Cells(i, 1).Offset(0, 8) = Evaluate("SUMIFS(���Ǵ����[��ͣ�ⵥ��],���Ǵ����[��ͣ����ԭ��],""*" & rng.Offset(0, 4) & "*"")")  ' ��ͷ
            Sheet27.Cells(i, 1).Offset(0, 9) = Evaluate("SUMIFS(�װ��[��ͣ�ⵥ��],�װ��[�װ�ԭ��],""*" & rng.Offset(0, 4) & "*"")")  ' ��ͷ
        End If
    
        
            
            Sheet27.Cells(i, 1).Offset(0, 10) = cybgd '��ҵ��߶�
            
            
            Sheet27.Cells(i, 1).Offset(0, 11) = Sheet25.Range("e2")
            Sheet27.Cells(i, 1).Offset(0, 12) = Sheet25.Range("e3")
            Sheet27.Cells(i, 1).Offset(0, 13) = Sheet25.Range("d2")
            Sheet27.Cells(i, 1).Offset(0, 14) = Sheet25.Range("d3")
            
            'Sheet27.Cells(i, 1).Offset(0, 12) = Sheet2.Range("b2")
            Sheet27.Cells(i, 1).Offset(0, 15) = Sheet4.Range("H6")
            Sheet27.Cells(i, 1).Offset(0, 15).Interior.ColorIndex = Sheet4.Range("H6").Interior.ColorIndex
            
            Sheet27.Cells(i, 1).Offset(0, 16) = Evaluate("COUNTIFS(��1[ [�ǵ���] ],"">0"")")
            Sheet27.Cells(i, 1).Offset(0, 17) = Sheet27.Cells(i, 1).Offset(0, 16) / lastRow
            Range("��1").Sort "120���ǵ���", 2, , , , , , 1
            For j = 1 To 1000 Step 1
                If Sheet2.Cells(1 + j, 15) / 10000 / 10000 > 100 Then
                    Sheet27.Cells(i, 1).Offset(0, 18) = Sheet2.Cells(1 + j, 2)
                    Exit For
                End If
            Next
            Exit For
        End If
    Next
    
End Sub
Sub re()
        '����ȥ�ظ��ֺ�
    Range("��[��������]").Replace ";;", ";", 2
    Range("��1[��������]").Replace ";;", ";", 2
    
    '����ȥ�ո�
    Range("��[��������]").Replace " ", "", 2
    Range("��1[��������]").Replace " ", "", 2
    'Range("��2[��������]").Replace " ", "", 2
    '����ȥ�ո����
    '�����豸�����
    Range("��[��������]").Replace ";�����豸;", ";����;", 2
    Range("��1[��������]").Replace ";�����豸;", ";����;", 2
    Range("��[��������]").Replace ";����������;", ";����;", 2
    Range("��1[��������]").Replace ";����������;", ";����;", 2
    'Range("��2[��������]").Replace ";�����豸;", ";����;", 2
    
    Range("��[��������]").Replace ";���;", ";����;", 2
    Range("��1[��������]").Replace ";���;", ";����;", 2
    'Range("��2[��������]").Replace ";���;", ";����;", 2
    
    'Range("��[��������]").Replace ";??����ĸ�;", ";", 2
    'Range("��1[��������]").Replace ";??����ĸ�;", ";", 2
    'Range("��2[��������]").Replace ";�������ĸ�;", ";����ĸ�;", 2
    
    Range("��[��������]").Replace ";�������;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";�������;", ";�¹�����¹�;", 2
    Range("��[��������]").Replace ";���¹�;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";���¹�;", ";�¹�����¹�;", 2
    Range("��[��������]").Replace ";��׼�ƴ��¹�;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";��׼�ƴ��¹�;", ";�¹�����¹�;", 2
    Range("��[��������]").Replace ";ע���ƴ��¹�;", ";�¹�����¹�;", 2
    Range("��1[��������]").Replace ";ע���ƴ��¹�;", ";�¹�����¹�;", 2
End Sub

Sub ������ͣԭ��()
    Dim Wb As Workbook
    myPath = Left(ThisWorkbook.Path, Len(ThisWorkbook.Path) - 6) & "\template.xlsm"
    Debug.Print myPath
    Range("��1").Sort "4���ǵ���", 2, , , , , , 1
    Range("��1").Sort "��������", 2, , , , , , 1
    
    
    Set rng = Sheet21.Range("a:a").Find("�װ�")
    sb = 0 '�װ��к�
    If Not rng Is Nothing Then sb = rng.Row
     For j = 1 To 256 Step 1
        If Sheet21.Cells(sb + j, 1) = "" Then Exit For

    Next
    
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Debug.Print Sheet27.UsedRange.Rows.Count
    
    
    Dim lastRow As Long
    With Sheet15
        lastRow = .Cells(.Rows.Count, 1).End(xlUp).Row - 1
    End With

    Dim CurrentDate As Date
    CurrentDate = Date
    Dim cybgd As String '��ҵ��߶�
    
    For i = 2 To 200 Step 1
        If InStr(Sheet2.Range("a" & i), ".300") > 0 Or InStr(Sheet2.Range("a" & i), ".301") > 0 Then
            cybgd = Sheet2.Range("z" & i)
            Exit For
        End If
        
    Next
    
    i = Sheet27.UsedRange.Rows.Count + 1
   
    If Sheet27.Cells(i, 1) = "" Then
       
        Sheet27.Cells(i, 1) = CurrentDate
        Sheet27.Cells(i, 1).Offset(0, 1) = lastRow
        
        Sheet27.Cells(i, 1).Offset(0, 2) = Evaluate("COUNTIFS(��1[ [��ͣ�ⵥ��] ],"">0"")")
        Sheet27.Cells(i, 1).Offset(0, 3) = Evaluate("COUNTIFS(��1[ [��������] ],""1"")")
        Sheet27.Cells(i, 1).Offset(0, 4) = Evaluate("COUNTIFS(��1[ [��������] ],"">1"")")
        Sheet27.Cells(i, 1).Offset(0, 5) = Sheet2.Range("z2") ' �ܸ߶�
        Sheet27.Cells(i, 1).Offset(0, 6) = Sheet4.Range("H25") ' ��ͷ
        
        
'            If Not rng Is Nothing Then lz = rng.Offset(0, 3)
        Set rng = Sheet5.Range("B:B").Find(Sheet27.Cells(i, 1).Offset(0, 6))  ' ��ͷ ��ͣԭ��
        If Not rng Is Nothing Then
            Sheet27.Cells(i, 1).Offset(0, 7) = rng.Offset(0, 4) ' ��ͷ
            Debug.Print "SUMIFS(���Ǵ����[��ͣ�ⵥ��],���Ǵ����[��ͣ����ԭ��],""*" & rng.Offset(0, 4) & "*"")"
            
            Sheet27.Cells(i, 1).Offset(0, 8) = Evaluate("SUMIFS(���Ǵ����[��ͣ�ⵥ��],���Ǵ����[��ͣ����ԭ��],""*" & rng.Offset(0, 4) & "*"")")  ' ��ͷ
            Sheet27.Cells(i, 1).Offset(0, 9) = Evaluate("SUMIFS(�װ��[��ͣ�ⵥ��],�װ��[�װ�ԭ��],""*" & rng.Offset(0, 4) & "*"")")  ' ��ͷ
        End If
    
        
        Sheet27.Cells(i, 1).Offset(0, 10) = cybgd '��ҵ��߶�
        
        
        Sheet27.Cells(i, 1).Offset(0, 11) = Sheet25.Range("e2")
        Sheet27.Cells(i, 1).Offset(0, 12) = Sheet25.Range("e3")
        Sheet27.Cells(i, 1).Offset(0, 13) = Sheet25.Range("d2")
        Sheet27.Cells(i, 1).Offset(0, 14) = Sheet25.Range("d3")
        
        'Sheet27.Cells(i, 1).Offset(0, 12) = Sheet2.Range("b2")
        Sheet27.Cells(i, 1).Offset(0, 15) = Sheet4.Range("H6")
        Sheet27.Cells(i, 1).Offset(0, 15).Interior.ColorIndex = Sheet4.Range("H6").Interior.ColorIndex
        
        Sheet27.Cells(i, 1).Offset(0, 16) = Evaluate("COUNTIFS(��1[ [�ǵ���] ],"">0"")")
        Sheet27.Cells(i, 1).Offset(0, 17) = Sheet27.Cells(i, 1).Offset(0, 16) / lastRow
        
        Range("��1").Sort "120���ǵ���", 2, , , , , , 1
        For j2 = 1 To 1000 Step 1
             If Sheet2.Cells(1 + j2, 15) / 10000 / 10000 > 50 Then
                 Sheet27.Cells(i, 1).Offset(0, 18) = Sheet2.Cells(1 + j2, 2)
                 Exit For
             End If
         Next
    End If
    
    
    
    
    
    Set Wb = Workbooks.Open(myPath)
    Sheet7.Cells.Copy
    'Wb.Sheet21.Range("a1").PasteSpecial
    Wb.Sheets("��ԭ��").Range("a1").PasteSpecial
    

    Sheet21.Rows(sb & ":" & (sb + j)).Copy

        
    Wb.Sheets("��ԭ��").Range("a" & ����).PasteSpecial
    
    Wb.Sheets("��ԭ��").Range("a" & ����) = "���װ�"
    
    
    ' ���� ����ɫ����
 '   Range("��1").Sort "4���ǵ���", 2, , , , , , 1
    
    
    
    ���� = Sheet27.UsedRange.Rows.Count + 1
    
    Sheet27.Rows("1:" & (����)).Copy
    Wb.Sheets("��������ͼ").Range("a1").PasteSpecial
    

    
    Wb.Save
    Wb.Close
    Set Wb = Nothing
End Sub
Sub ɾ������()
    'On Error Resume Next
    Range("��[  ����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    Range("��1[  ����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    'Range("��2[  ����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
End Sub


Sub ������ͼ()
    Dim ChartSheet As Chart
    Dim RangeToChart As Range
    Debug.Print "A2:B" & Sheet26.UsedRange.Rows.Count
    
    ' ����Ҫ��ͼ�����ݷ�Χ
    Set RangeToChart = Sheet26.Range("A1:C3")

    ' ����ͼ��
    Set ChartSheet = Charts.Add
    ChartSheet.SetSourceData Source:=RangeToChart
    ChartSheet.ChartType = xlLine

    ' ��ѡ����ʽ��ͼ�����⡢�����Ƶȣ�
    With ChartSheet
        .HasTitle = True
        .ChartTitle.Text = "ʱ�����۶�"
        .Axes(xlCategory, xlPrimary).HasTitle = True
        .Axes(xlCategory, xlPrimary).AxisTitle.Text = "����"
        .Axes(xlValue, xlPrimary).HasTitle = True
        .Axes(xlValue, xlPrimary).AxisTitle.Text = "����"
    End With
End Sub


