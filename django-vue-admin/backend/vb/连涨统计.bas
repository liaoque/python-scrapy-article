Attribute VB_Name = "����ͳ��"
Sub �����㷨()
    'Application.ScreenUpdating = False
    't = Timer
    Debug.Print Now & "�����㷨"
    Debug.Print Now & "ȡ���ǹ�Ʊ"
    ȡ���ǹ�Ʊ
    Debug.Print Now & "ȡ��ͣ��Ʊ"
    ȡ��ͣ��Ʊ
    Debug.Print Now & "ȡը���Ʊ"
    ȡը���Ʊ
    Debug.Print Now & "ȡ�������¸߹�Ʊ"
    ȡ�������¸߹�Ʊ
    Debug.Print Now & "ȡһ�ְ��Ʊ"
    ȡһ�ְ��Ʊ
    Debug.Print Now & "ȡ�װ��Ʊ"
    ȡ�װ��Ʊ
    
    Debug.Print Now & "�������Ǹ���"
    �������Ǹ���
    Debug.Print Now & "���ɵ�ͣ����"
    ���ɵ�ͣ����
    Debug.Print Now & "����ը�����"
    ����ը�����
    Debug.Print Now & "���ɴ������¸߸���"
    ���ɴ������¸߸���
    Debug.Print Now & "����һ�ְ����"
    ����һ�ְ����
    Debug.Print Now & "�����װ����"
    �����װ����
    
    Debug.Print Now & "ȡ��ͣԭ��"
    ȡ��ͣԭ��
    Debug.Print Now & "ȡ��ͣԭ��"
    ȡ��ͣԭ��
    Debug.Print Now & "ȡը��ԭ��"
    ȡը��ԭ��
    Debug.Print Now & "ȡ�������¸�ԭ��"
    ȡ�������¸�ԭ��
    Debug.Print Now & "ȡһ�ְ�ԭ��"
    ȡһ�ְ�ԭ��
    Debug.Print Now & "ȡ�װ�ԭ��"
    ȡ�װ�ԭ��
    
    Debug.Print Now & "������ͣԭ��"
    ������ͣԭ��
    Debug.Print Now & "���е�ͣԭ��"
    ���е�ͣԭ��
    Debug.Print Now & "����ը��ԭ��"
    ����ը��ԭ��
    Debug.Print Now & "���д������¸�ԭ��"
    ���д������¸�ԭ��
    Debug.Print Now & "����һ�ְ�ԭ��"
    ����һ�ְ�ԭ��
    Debug.Print Now & "�����װ�ԭ��"
    �����װ�ԭ��
    
    ���о���ͣ����ͣ
    ����5���ǵ���
    '���Ǽ�¼
    'Application.ScreenUpdating = True
    'MsgBox "��ʱ��" & Round(Timer - t, 2) & "��"
End Sub
Sub ȡ���ǹ�Ʊ()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    Range("��1").Sort "����", 2, , , , , , 1
    'Range("��2").Sort "��������", 2, , , , , , 1
    Sheet5.Range("a2:h99999").Clear
    'nogn = ";��ʱ���ظ���;��ʱ���ظ����;���յ���˹A��;����ͨ;���ͨ;������ȯ;ת��ȯ���;��ת��Ȩ;��Ȩת��;��������;����;MSCI����;һ��������;ҵ������;�걨����;����;"
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("��1[  ����]")
        If rng.Offset(0, 18) = "��ͣ����" Then
            Sheet5.Range("a" & h) = rng
            Sheet5.Range("b" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            'Set dic = CreateObject("scripting.dictionary")
            For i = LBound(arr) To UBound(arr)
                'If InStr(nogn, ";" & arr(i) & ";") < 1 Then 'ȥ����Ҫ�ĸ���
                    If arr(i) <> "" Then
                        If Not dic.Exists(arr(i)) Then
                            dic(arr(i)) = 1
                        End If
                    End If
                'End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            'Set dic = Nothing '�ر��ֵ�
            Sheet5.Range("c" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("d" & h) = rng.Offset(0, 16)
            Sheet5.Range("h" & h) = Round(rng.Offset(0, 21) / 100000000, 2) 'δƥ����
            'Sheet5.Range("e" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next
    '������ͣ
    If Sheet15.Range("a2") <> "" Then
        h = Sheet15.Range("a1").End(xlDown).Row
        For i = 2 To h
            Set rng = Sheet5.Range("a:a").Find(Sheet15.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 4) = Sheet15.Range("i" & i)
            End If
            Set rng = Sheet2.Range("a:a").Find(Sheet15.Range("a" & i), , , 1)
            If Not rng Is Nothing Then
                rng.Offset(0, 25) = Sheet15.Range("g" & i)
            End If
        Next
    End If
'    For Each rng In Range("��2[  ����]")
'        If rng.Offset(0, 7) < 1 Then Exit For
'        Sheet5.Range("a" & h) = rng
'        Sheet5.Range("b" & h) = rng.Offset(0, 1)
'        arr = Split(rng.Offset(0, 4), ";")
'        'Set dic = CreateObject("scripting.dictionary")
'        For i = LBound(arr) To UBound(arr)
'            If InStr(nogn, ";" & arr(i) & ";") < 1 Then 'ȥ����Ҫ�ĸ���
'                If arr(i) <> "" Then
'                    If Not dic.exists(arr(i)) Then
'                        dic(arr(i)) = 1
'                    End If
'                End If
'            End If
'        Next
'        arr1 = dic.keys()
'        dic.RemoveAll
'        'Set dic = Nothing '�ر��ֵ�
'        Sheet5.Range("c" & h) = ";" & Join(arr1, ";") & ";"
'        Sheet5.Range("d" & h) = rng.Offset(0, 7)
'        Sheet5.Range("e" & h) = rng.Offset(0, 11)
'        h = h + 1
'    Next
    Set dic = Nothing '�ر��ֵ�
    
End Sub

Sub ȡ��ͣ��Ʊ()
    Dim rng, rng2 As Range
    Dim dic As Object
    Dim arr, arr1
    Range("��1").Sort "����", 2, , , , , , 1
    Sheet5.Range("i2:o99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("��1[  ����]")
        'If rng.Offset(0, 18) = "" Then Exit For
        If rng.Offset(0, 18) = "��ͣ����" Then
            Sheet5.Range("i" & h) = rng
            Sheet5.Range("j" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("k" & h) = ";" & Join(arr1, ";") & ";"
            
            'Sheet5.Range("l" & h) = Round(rng.Offset(0, 21) / 100000000, 2) 'δƥ����
            Set rng2 = Sheet22.Range("a:a").Find(rng, , , 1) '��ȷ
            If Not rng2 Is Nothing Then
                Sheet5.Range("l" & h) = Round(rng2.Offset(0, 4) / 100000000, 2) 'δƥ����
            Else
                Sheet5.Range("l" & h) = 0
            End If
            Sheet5.Range("m" & h) = rng.Offset(0, 3)
            h = h + 1
        End If
    Next

    Set dic = Nothing '�ر��ֵ�
    
End Sub
Sub ȡը���Ʊ()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("��1").Sort "����", 2, , , , , , 1
    Sheet5.Range("q2:w99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("��1[  ����]")
        If rng.Offset(0, 19) = "ը��" Then
            Sheet5.Range("q" & h) = rng
            Sheet5.Range("r" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("s" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("t" & h) = rng.Offset(0, 6) '�ǵ���
            Sheet5.Range("u" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '�ر��ֵ�
    
End Sub
Sub ȡ�������¸߹�Ʊ()
    Dim rng, rng2 As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("��1").Sort "����", 2, , , , , , 1
    Sheet5.Range("y2:ae99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    i = 2
    For Each rng In Range("��1[  ����]")
     
        If rng.Offset(0, 20) = "�������¸�" Then
            Sheet5.Range("y" & h) = rng
            Sheet5.Range("z" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("aa" & h) = ";" & Join(arr1, ";") & ";"
            'Sheet5.Range("ab" & h) = rng.Offset(0, 6) '�ǵ���
            Sheet5.Range("ab" & h) = Round(rng.Offset(0, 21) / 100000000, 2) 'δƥ����
            Sheet5.Range("ac" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            '   Set rng2 = Sheet15.Range("a:a").Find(rng, , , 1)
            '  If Not rng2 Is Nothing Then
            '    Sheet5.Range("ab" & h) = rng2.Offset(0, 8)
            '  End If
            h = h + 1
        End If
        
        
    Next

    Set dic = Nothing '�ر��ֵ�
    
End Sub
Sub ȡһ�ְ��Ʊ()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("��1").Sort "����", 2, , , , , , 1
    Sheet5.Range("ag2:am99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("��1[  ����]")
        If rng.Offset(0, 21) <> "" Then
            Sheet5.Range("ag" & h) = rng
            Sheet5.Range("ah" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("ai" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("aj" & h) = Round(rng.Offset(0, 21) / 100000000, 2) 'δƥ����
            Sheet5.Range("ak" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '�ر��ֵ�
    
End Sub
Sub ȡ�װ��Ʊ()
    Dim rng As Range
    Dim dic As Object
    Dim arr, arr1
    'Range("��1").Sort "����", 2, , , , , , 1
    Sheet5.Range("ao2:au99999").Clear
    Set dic = CreateObject("scripting.dictionary")
    h = 2
    For Each rng In Range("��1[  ����]")
        If rng.Offset(0, 23) <> "" Then
            Sheet5.Range("ao" & h) = rng
            Sheet5.Range("ap" & h) = rng.Offset(0, 1)
            arr = Split(rng.Offset(0, 4), ";")
            For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    End If
                End If
            Next
            arr1 = dic.keys()
            dic.RemoveAll
            Sheet5.Range("aq" & h) = ";" & Join(arr1, ";") & ";"
            Sheet5.Range("ar" & h) = Round(rng.Offset(0, 23) / 100000000, 2) '��ͣ�ⵥ��
            Sheet5.Range("as" & h) = Round(rng.Offset(0, 14) / 100000000, 2)
            h = h + 1
        End If
    Next

    Set dic = Nothing '�ر��ֵ�
    
End Sub

Sub �������Ǹ���()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr

    'nogn = ";��ʱ���ظ���;��ʱ���ظ����;���յ���˹A��;����ͨ;���ͨ;������ȯ;ת��ȯ���;��ת��Ȩ;��Ȩת��;��������;����;MSCI����;һ��������;ҵ������;�걨����;����;"
    'ȡ����Ч����ϲ���һ�����ַ���
    Sheet6.Range("a2:b99999").Clear
    If Sheet5.Range("a2") = "" Then Exit Sub
    hs = Sheet5.Range("a1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("c" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
            'If InStr(nogn, ";" & arr(i) & ";") < 1 Then 'ȥ����Ҫ�ĸ���
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        'dic(arr(i)) = Evaluate("COUNTIFS(���ǹ�Ʊ!C:C,""*;" & arr(i) & ";*"")")
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    'If Range("��ҵ�����[#data]").Rows.Count > 1 Then Range("��ҵ�����[#data]").Delete Shift:=xlShiftUp '���ԭ��
    'Range("��ҵ�����[ʵ����ͨ]").NumberFormatLocal = "0.0000_ "
    'Range("��ҵ�����[[#Headers],[��������]]").Offset(1, 0).Resize(dic.Count) = Application.Transpose(dic.keys)
    'Range("��ҵ�����[[#Headers],[����]]").Offset(1, 0).Resize(dic.Count, 1) = Application.Transpose(dic.items)
    
    Sheet6.Range("a2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("b2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '�ر��ֵ�
    'Sheet6.Range("a:b").Sort "���ǹ�Ʊ��", 2, , , , , , 1
End Sub

Sub ���ɵ�ͣ����()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("d2:e99999").Clear
    If Sheet5.Range("i2") = "" Then Exit Sub
    'ȡ����Ч����ϲ���һ�����ַ���
    hs = Sheet5.Range("i1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("k" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    
    Sheet6.Range("d2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("e2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '�ر��ֵ�
    'Sheet6.Range("a:b").Sort "���ǹ�Ʊ��", 2, , , , , , 1
End Sub
Sub ����ը�����()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("g2:h99999").Clear
    If Sheet5.Range("s2") = "" Then Exit Sub
    'ȡ����Ч����ϲ���һ�����ַ���
    hs = Sheet5.Range("s1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("s" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    
    Sheet6.Range("g2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("h2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '�ر��ֵ�
    'Sheet6.Range("a:b").Sort "���ǹ�Ʊ��", 2, , , , , , 1
End Sub
Sub ���ɴ������¸߸���()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("j2:k99999").Clear
    If Sheet5.Range("aa2") = "" Then Exit Sub
    'ȡ����Ч����ϲ���һ�����ַ���
    hs = Sheet5.Range("aa1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("aa" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    
    Sheet6.Range("j2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("k2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '�ر��ֵ�
    'Sheet6.Range("a:b").Sort "���ǹ�Ʊ��", 2, , , , , , 1
End Sub
Sub ����һ�ְ����()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("m2:n99999").Clear
    If Sheet5.Range("ai2") = "" Then Exit Sub
    'ȡ����Ч����ϲ���һ�����ַ���
    hs = Sheet5.Range("ai1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("ai" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    
    Sheet6.Range("m2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("n2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '�ر��ֵ�
    'Sheet6.Range("a:b").Sort "���ǹ�Ʊ��", 2, , , , , , 1
End Sub
Sub �����װ����()
    On Error Resume Next
'    Application.ScreenUpdating = False
'    t = Timer
    Dim rng As Range
    Dim dic As Object
    Dim nogn, gnstr As String
    Dim arr
    Sheet6.Range("p2:q99999").Clear
    If Sheet5.Range("aq2") = "" Then Exit Sub
    'ȡ����Ч����ϲ���һ�����ַ���
    hs = Sheet5.Range("aq1").End(xlDown).Row
    For i = 2 To hs
        gnstr = gnstr & Sheet5.Range("aq" & i)
    Next
    gnstr = Replace(gnstr, ";;", ";")
    'Debug.Print str_cy
    '����ַ�����ֳ�����
    If gnstr <> "" Then arr = Split(Left(gnstr, Len(gnstr) - 1), ";")
    
    '��������ת�ֵ�ȥ��
    Set dic = CreateObject("scripting.dictionary")
    If gnstr <> "" Then
        For i = LBound(arr) To UBound(arr)
                If arr(i) <> "" Then
                    If Not dic.Exists(arr(i)) Then
                        dic(arr(i)) = 1
                    Else
                        dic(arr(i)) = dic(arr(i)) + 1
                    End If
                End If
            'End If
        Next
    End If
    

    '���ֵ�����������
    
    Sheet6.Range("p2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet6.Range("q2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Set dic = Nothing '�ر��ֵ�
    'Sheet6.Range("a:b").Sort "���ǹ�Ʊ��", 2, , , , , , 1
End Sub

Sub ȡ��ͣԭ��()
    Dim rng As Range
    If Sheet5.Range("a2") = "" Then Exit Sub
    hs = Sheet5.Range("a1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("c" & i), ";")
        ���� = ""
        ���� = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("a:a").Find(a, , , 1) '��ȷ
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ���� & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("f" & i) = ����
        Sheet5.Range("g" & i) = ����
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(��1[ʵ����ͨ],��1[��������],""*;" & ���� & ";*"")") + Evaluate("SUMIFS(��2[ʵ����ͨ],��2[��������],""*;" & ���� & ";*"")")
    Next
    '����ԭ�����
'    For i = 2 To hs
'
'    Next
    ' ���Ǵ����
    Range("���Ǵ����").Sort "��ͣ������", 2, , , , , , 1
   ' Sheet5.Range("a:h").Sort "��ͣ������", 2, , , , , , 1
End Sub

Sub ȡ��ͣԭ��()
    Dim rng As Range
    If Sheet5.Range("i2") = "" Then Exit Sub
    hs = Sheet5.Range("i1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("k" & i), ";")
        ���� = ""
        ���� = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("d:d").Find(a, , , 1) '��ȷ
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ���� & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("n" & i) = ����
        Sheet5.Range("o" & i) = ����
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(��1[ʵ����ͨ],��1[��������],""*;" & ���� & ";*"")") + Evaluate("SUMIFS(��2[ʵ����ͨ],��2[��������],""*;" & ���� & ";*"")")
    Next
    Range("��ͣ�����").Sort "��ͣ������", 2, , , , , , 1
   ' Sheet5.Range("i:o").Sort "��ͣ������", 2, , , , , , 1
End Sub
Sub ȡը��ԭ��()
    Dim rng As Range
    If Sheet5.Range("q2") = "" Then Exit Sub
    hs = Sheet5.Range("q1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("s" & i), ";")
        ���� = ""
        ���� = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("g:g").Find(a, , , 1) '��ȷ
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ���� & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("v" & i) = ����
        Sheet5.Range("w" & i) = ����
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(��1[ʵ����ͨ],��1[��������],""*;" & ���� & ";*"")") + Evaluate("SUMIFS(��2[ʵ����ͨ],��2[��������],""*;" & ���� & ";*"")")
    Next
      Range("ը���").Sort "ը����", 2, , , , , , 1
   ' Sheet5.Range("q:w").Sort "ը����", 2, , , , , , 1
End Sub
Sub ȡ�������¸�ԭ��()
    Dim rng As Range
    If Sheet5.Range("y2") = "" Then Exit Sub
    hs = Sheet5.Range("y1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("aa" & i), ";")
        ���� = ""
        ���� = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("j:j").Find(a, , , 1) '��ȷ
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ���� & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("ad" & i) = ����
        Sheet5.Range("ae" & i) = ����
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(��1[ʵ����ͨ],��1[��������],""*;" & ���� & ";*"")") + Evaluate("SUMIFS(��2[ʵ����ͨ],��2[��������],""*;" & ���� & ";*"")")
    Next
   ' Sheet5.Range("y:ae").Sort "�������¸���", 2, , , , , , 1
     Range("�����¸߹�").Sort "�������¸���", 2, , , , , , 1
End Sub

Sub ȡһ�ְ�ԭ��()
    Dim rng As Range
    If Sheet5.Range("ag2") = "" Then Exit Sub
    hs = Sheet5.Range("ag1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("ai" & i), ";")
        ���� = ""
        ���� = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("m:m").Find(a, , , 1) '��ȷ
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ���� & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("al" & i) = ����
        Sheet5.Range("am" & i) = ����
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(��1[ʵ����ͨ],��1[��������],""*;" & ���� & ";*"")") + Evaluate("SUMIFS(��2[ʵ����ͨ],��2[��������],""*;" & ���� & ";*"")")
    Next
    'Sheet5.Range("ag:am").Sort "�񾺷���", 2, , , , , , 1
      Range("һ�ְ��").Sort "�񾺷���", 2, , , , , , 1
End Sub

Sub ȡ�װ�ԭ��()
    Dim rng As Range
    If Sheet5.Range("ao2") = "" Then Exit Sub
    hs = Sheet5.Range("ao1").End(xlDown).Row
    For i = 2 To hs
        arr = Split(Sheet5.Range("aq" & i), ";")
        ���� = ""
        ���� = 0
        For Each a In arr
            If a <> "" Then
                Set rng = Sheet6.Range("p:p").Find(a, , , 1) '��ȷ
                If Not rng Is Nothing Then
                    If rng.Offset(0, 1) = ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ���� & ";" & a & ";"
                    End If
                    If rng.Offset(0, 1) > ���� Then
                        ���� = rng.Offset(0, 1)
                        ���� = ";" & a & ";"
                    End If
                End If
            End If
        Next
        Sheet5.Range("at" & i) = ����
        Sheet5.Range("au" & i) = ����
        'Sheet5.Range("h" & i) = Evaluate("SUMIFS(��1[ʵ����ͨ],��1[��������],""*;" & ���� & ";*"")") + Evaluate("SUMIFS(��2[ʵ����ͨ],��2[��������],""*;" & ���� & ";*"")")
    Next
   ' Sheet5.Range("ao:au").Sort "�װ���", 2, , , , , , 1
     Range("�װ��").Sort "�װ���", 2, , , , , , 1
End Sub

Sub ������ͣԭ��()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    Sheet7.Cells.Clear
    If Sheet5.Range("a2") = "" Then Exit Sub
    ������� = 0
    hs = Sheet5.Range("a1").End(xlDown).Row
    Sheet7.Cells(1, 1) = "����"
    Sheet7.Cells(1, 2) = Date
    Sheet7.Cells(2, 1) = "��ͣ����"
    Sheet7.Cells(2, 1).Interior.ColorIndex = 36
    For i = 2 To hs
        arr = Split(Sheet5.Range("f" & i), ";")
        '���� = Sheet5.Range("f" & i)
        For Each ���� In arr
            If ���� <> "" Then
                If Not dic.Exists(����) Then
                    dic(����) = 1
                    Sheet7.Cells(3, ������� * 3 + 1) = ����
                    '���� = Sheet5.Range("h" & i)
                    '���� = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & ���� & ";*"")/100000000,2)") ' + Evaluate("SUMIFS(��2[ʵ����ͨ],��2[��������],""*;" & ���� & ";*"")")
                    Sheet7.Cells(3, ������� * 3 + 2) = ����
                    'If ���� < 9000 Then Sheet7.Cells(3, ������� * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(4, ������� * 3 + 1) = "����"
                    Sheet7.Cells(4, ������� * 3 + 2) = "����δƥ��"
                    Set rng = Sheet5.Range("f:f").Find(";" & ���� & ";", , , 2) 'ģ��
                    h = 4
                    If Not rng Is Nothing Then
                        δƥ����� = 0
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            h = h + 1
                            Sheet7.Cells(h, ������� * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, ������� * 3 + 2) = rng.Offset(0, -1) 'δƥ����
                            δƥ����� = δƥ����� + Sheet7.Cells(h, ������� * 3 + 2)
                            Set rng = Sheet5.Range("f:f").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                        
                       ' For g = 5 To h
                        '    code = Sheet7.Range("a" & g)
                         '   Set rng = Sheet2.Range("b:b").Find(code, , , 1) '
                          '  Sheet7.Cells(g, ������� * 3 + 2) = rng.Offset(0, 16) 'δƥ����
                         '   δƥ����� = δƥ����� + rng.Offset(0, 16)
                       ' Next
                        
                    End If
                    Sheet7.Cells(3, ������� * 3 + 2) = δƥ�����
                    ������� = ������� + 1
                    
                End If
            End If
        Next
    Next
End Sub

Sub ���е�ͣԭ��()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("i2") = "" Then Exit Sub
    ������� = 0
    hs = Sheet5.Range("i1").End(xlDown).Row
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "��ͣ����"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ���� = ���� + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("n" & i), ";")
        '���� = Sheet5.Range("f" & i)
        For Each ���� In arr
            If ���� <> "" Then
                If Not dic.Exists(����) Then
                    dic(����) = 1
                    Sheet7.Cells(����, ������� * 3 + 1) = ����
                    '���� = Sheet5.Range("h" & i)
                    '���� = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & ���� & ";*"")/100000000,2)")
                    'Sheet7.Cells(����, ������� * 3 + 2) = ����
                    'If ���� < 9000 Then Sheet7.Cells(����, ������� * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(���� + 1, ������� * 3 + 1) = "����"
                    Sheet7.Cells(���� + 1, ������� * 3 + 2) = "����δƥ��"
                    Set rng = Sheet5.Range("n:n").Find(";" & ���� & ";", , , 2) 'ģ��
                    If Not rng Is Nothing Then
                        h = ���� + 2
                        δƥ����� = 0
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, ������� * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, ������� * 3 + 2) = rng.Offset(0, -2)
                            δƥ����� = δƥ����� + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("n:n").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(����, ������� * 3 + 2) = δƥ�����
                    ������� = ������� + 1
                End If
            End If
        Next
    Next
End Sub
Sub ����ը��ԭ��()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("q2") = "" Then Exit Sub
    ������� = 0
    hs = Sheet5.Range("q1").End(xlDown).Row
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "ը��"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ���� = ���� + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("v" & i), ";")
        '���� = Sheet5.Range("f" & i)
        For Each ���� In arr
            If ���� <> "" Then
                If Not dic.Exists(����) Then
                    dic(����) = 1
                    Sheet7.Cells(����, ������� * 3 + 1) = ����
                    '���� = Sheet5.Range("h" & i)
                    '���� = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & ���� & ";*"")/100000000,2)")
                    'Sheet7.Cells(����, ������� * 3 + 2) = ����
                    'If ���� < 9000 Then Sheet7.Cells(����, ������� * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(���� + 1, ������� * 3 + 1) = "����"
                    Sheet7.Cells(���� + 1, ������� * 3 + 2) = "�ǵ���"
                    Set rng = Sheet5.Range("v:v").Find(";" & ���� & ";", , , 2) 'ģ��
                    If Not rng Is Nothing Then
                        h = ���� + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, ������� * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, ������� * 3 + 2) = rng.Offset(0, -2)
                            Sheet7.Cells(h, ������� * 3 + 2).NumberFormatLocal = "0.00%"
                            h = h + 1
                             Set rng = Sheet5.Range("v:v").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    
                    ������� = ������� + 1
                End If
            End If
        Next
    Next
End Sub

Sub ���д������¸�ԭ��()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("y2") = "" Then Exit Sub
    ������� = 0
    hs = Sheet5.Range("y1").End(xlDown).Row
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "�������¸�"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ���� = ���� + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("ad" & i), ";")
        '���� = Sheet5.Range("f" & i)
        For Each ���� In arr
            If ���� <> "" Then
                If Not dic.Exists(����) Then
                    dic(����) = 1
                    Sheet7.Cells(����, ������� * 3 + 1) = ����
                    '���� = Sheet5.Range("h" & i)
                    '���� = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & ���� & ";*"")/100000000,2)")
                    'Sheet7.Cells(����, ������� * 3 + 2) = ����
                    'If ���� < 9000 Then Sheet7.Cells(����, ������� * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(���� + 1, ������� * 3 + 1) = "����"
                    Sheet7.Cells(���� + 1, ������� * 3 + 2) = "����δƥ��"
                    δƥ����� = 0
                    Set rng = Sheet5.Range("ad:ad").Find(";" & ���� & ";", , , 2) 'ģ��
                    If Not rng Is Nothing Then
                        h = ���� + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, ������� * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, ������� * 3 + 2) = rng.Offset(0, -2) '����δƥ��
                            δƥ����� = δƥ����� + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("ad:ad").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(����, ������� * 3 + 2) = δƥ�����
                    ������� = ������� + 1
                End If
            End If
        Next
    Next
End Sub
Sub ����һ�ְ�ԭ��()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("ag2") = "" Then Exit Sub
    ������� = 0
    hs = Sheet5.Range("ag1").End(xlDown).Row
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "�񾺷�"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ���� = ���� + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("al" & i), ";")
        '���� = Sheet5.Range("f" & i)
        For Each ���� In arr
            If ���� <> "" Then
                If Not dic.Exists(����) Then
                    dic(����) = 1
                    Sheet7.Cells(����, ������� * 3 + 1) = ����
                    '���� = Sheet5.Range("h" & i)
                    '���� = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & ���� & ";*"")/100000000,2)")
                    'Sheet7.Cells(����, ������� * 3 + 2) = ����
                    'If ���� < 9000 Then Sheet7.Cells(����, ������� * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(���� + 1, ������� * 3 + 1) = "����"
                    Sheet7.Cells(���� + 1, ������� * 3 + 2) = "����δƥ��"
                    δƥ����� = 0
                    Set rng = Sheet5.Range("al:al").Find(";" & ���� & ";", , , 2) 'ģ��
                    If Not rng Is Nothing Then
                        h = ���� + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, ������� * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, ������� * 3 + 2) = rng.Offset(0, -2)
                            δƥ����� = δƥ����� + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("al:al").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(����, ������� * 3 + 2) = δƥ�����
                    ������� = ������� + 1
                End If
            End If
        Next
    Next
End Sub

Sub �����װ�ԭ��()
    Dim dic As Object
    Dim rng As Range
    Dim arr
    Set dic = CreateObject("scripting.dictionary")
    'Sheet7.Cells.Clear
    If Sheet5.Range("ao2") = "" Then Exit Sub
    ������� = 0
    hs = Sheet5.Range("ao1").End(xlDown).Row
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "�װ�"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ���� = ���� + 1
    For i = 2 To hs
        arr = Split(Sheet5.Range("at" & i), ";")
        '���� = Sheet5.Range("f" & i)
        For Each ���� In arr
            If ���� <> "" Then
                If Not dic.Exists(����) Then
                    dic(����) = 1
                    Sheet7.Cells(����, ������� * 3 + 1) = ����
                    '���� = Sheet5.Range("h" & i)
                    '���� = Evaluate("round(SUMIFS(��1[����������ͨ��ֵ],��1[��������],""*;" & ���� & ";*"")/100000000,2)")
                    'Sheet7.Cells(����, ������� * 3 + 2) = ����
                    'If ���� < 9000 Then Sheet7.Cells(����, ������� * 3 + 2).Interior.ColorIndex = 35
                    Sheet7.Cells(���� + 1, ������� * 3 + 1) = "����"
                    Sheet7.Cells(���� + 1, ������� * 3 + 2) = "��ͣ�ⵥ��"
                    δƥ����� = 0
                    Set rng = Sheet5.Range("at:at").Find(";" & ���� & ";", , , 2) 'ģ��
                    If Not rng Is Nothing Then
                        h = ���� + 2
                        firstAddress = rng.Address
                        Do
                            'If rng.Offset(0, 1) < 2 Then Exit Do
                            Sheet7.Cells(h, ������� * 3 + 1) = rng.Offset(0, -4)
                            Sheet7.Cells(h, ������� * 3 + 2) = rng.Offset(0, -2)
                            δƥ����� = δƥ����� + rng.Offset(0, -2)
                            h = h + 1
                             Set rng = Sheet5.Range("at:at").FindNext(rng)
                        Loop While Not rng Is Nothing And rng.Address <> firstAddress
                    End If
                    Sheet7.Cells(����, ������� * 3 + 2) = δƥ�����
                    ������� = ������� + 1
                End If
            End If
        Next
    Next
End Sub

Sub ���о���ͣ����ͣ()
    Dim dic As Object
    Dim rng As Range

    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "����ͣ"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ����ͣ = Evaluate("round(SUM(һ�ְ�!E:E)/100000000,1)")
    Sheet7.Cells(���� + 1, 1) = ����ͣ
    Sheet7.Cells(���� + 3, 1) = "����ͣ"
    Sheet7.Cells(���� + 3, 1).Interior.ColorIndex = 36
    ����ͣ = Evaluate("round(SUM(һ�ֵ�ͣ!E:E)/100000000,1)")
    Sheet7.Cells(���� + 4, 1) = ����ͣ
    
     ' ��������������û��ǲ������һ��������������Ǵ���4000�ң���ǿ�Ƹĳɲ�
   ' If Evaluate("COUNTIFS(��1[ [�ǵ���] ],"">0"")") > 4000 Then Sheet4.Range("H6") = "��"
    Sheet7.Cells(����, 7) = "��������"
    Sheet7.Cells(���� + 1, 7) = Evaluate("COUNTIFS(��1[ [�ǵ���] ],"">0"")")
    Sheet7.Cells(����, 7).Interior.ColorIndex = 36
    Set rng = Sheet21.Range("A:A").Find("����ͣ")
    If Not rng Is Nothing Then
      Sheet7.Cells(���� + 4, 2) = ����ͣ - rng.Offset(1, 0)
      '  If ����ͣ > rng.Offset(1, 0) Then
      '      Sheet4.Range("H6") = "��"
      '      Sheet4.Range("H6").Interior.Color = 13421823
      '      Exit Sub
      '  End If
      '  If ����ͣ < rng.Offset(1, 0) Then
      '      Sheet4.Range("H6") = "��"
      '      Sheet4.Range("H6").Interior.ColorIndex = 35
      '      Exit Sub
      '  End If
    End If
    Set rng = Sheet21.Range("A:A").Find("����ͣ")
    If Not rng Is Nothing Then
        Sheet7.Cells(���� + 1, 2) = ����ͣ - rng.Offset(1, 0)
       ' If ����ͣ > rng.Offset(1, 0) Then
       '     Sheet4.Range("H6") = "��"
       '     Sheet4.Range("H6").Interior.Color = 13421823
       '     Exit Sub
       ' End If
       ' If ����ͣ < rng.Offset(1, 0) Then
       '     Sheet4.Range("H6") = "��"
       '     Sheet4.Range("H6").Interior.ColorIndex = 35
       '     Exit Sub
       ' End If
    End If
    '�ȿ���ͣԭ�����ľ���ͣ���� ��ԭ���ľ���ͣ��� ������ݱ��� ��Ȼ����ͣԭ�����ľ���ͣ��ȥ��ԭ���ľ���ͣ ������ֱ���
    'Ȼ��ѵ�һ����������ּ�ȥ�ڶ�����������֣����������ã�����������
    Sheet7.Cells(���� + 4, 3) = Sheet7.Cells(���� + 4, 2) + Sheet7.Cells(���� + 1, 2)
    If Sheet7.Cells(���� + 4, 3) > 0 Then
        Sheet4.Range("H6") = "��"
        Sheet4.Range("H6").Interior.Color = 13421823
    ElseIf Sheet7.Cells(���� + 4, 3) < 0 Then
        Sheet4.Range("H6") = "��"
        Sheet4.Range("H6").Interior.ColorIndex = 35
    Else
        Sheet4.Range("H6") = "ƽ"
        Sheet4.Range("H6").Interior.Color = RGB(255, 255, 255)
    End If
    
    
    ' ��������������û��ǲ������һ��������������Ǵ���4000�ң���ǿ�Ƹĳɲ�
    Set rng = Sheet21.Range("G:G").Find("��������")
    If Not rng Is Nothing Then
        If rng.Offset(1, 0) > 4000 Then
            Sheet4.Range("H6") = "��"
            Sheet4.Range("H6").Interior.ColorIndex = 34
        End If
    End If
    
   
        
   
End Sub

Sub ����5���ǵ���()
    '����
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "����"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ��� = Evaluate("MAXIFS(��1[5���ǵ���],��1[ [  ����] ],""<>SH.68*"",��1[ [  ����] ],""<>SZ.30*"")")
    Sheet7.Cells(���� + 1, 1) = "����"
    Sheet7.Cells(���� + 1, 2) = "����"
    Sheet7.Cells(���� + 1, 3) = "��������"
    Sheet7.Cells(���� + 1, 4) = "5���ǵ���"
    Set rng = Range("��1[5���ǵ���]").Find(���)
    If Not rng Is Nothing Then
        h = ���� + 2
'        firstAddress = rng.Address
'        Do
            Sheet7.Cells(h, 1) = rng.Offset(0, -13)
            Sheet7.Cells(h, 2) = rng.Offset(0, -12)
            Sheet7.Cells(h, 3) = rng.Offset(0, -9)
            Sheet7.Cells(h, 4) = Format(rng, "0.00%")
'            h = h + 1
'             Set rng = Range("��1[5���ǵ���]").FindNext(rng)
'        Loop While Not rng Is Nothing And rng.Address <> firstAddress
    End If
    
    '��ҵ��
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "��ҵ��"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ��� = Evaluate("MAXIFS(��1[5���ǵ���],��1[ [  ����] ],""=SZ.30*"")")
    Sheet7.Cells(���� + 1, 1) = "����"
    Sheet7.Cells(���� + 1, 2) = "����"
    Sheet7.Cells(���� + 1, 3) = "��������"
    Sheet7.Cells(���� + 1, 4) = "5���ǵ���"
    Set rng = Range("��1[5���ǵ���]").Find(���)
    If Not rng Is Nothing Then
        h = ���� + 2
'        firstAddress = rng.Address
'        Do
            Sheet7.Cells(h, 1) = rng.Offset(0, -13)
            Sheet7.Cells(h, 2) = rng.Offset(0, -12)
            Sheet7.Cells(h, 3) = rng.Offset(0, -9)
            Sheet7.Cells(h, 4) = Format(rng, "0.00%")
'            h = h + 1
'             Set rng = Range("��1[5���ǵ���]").FindNext(rng)
'        Loop While Not rng Is Nothing And rng.Address <> firstAddress
    End If
    
    '�ƴ���
    ���� = Sheet7.UsedRange.Rows.Count + 2
    Sheet7.Cells(����, 1) = "�ƴ���"
    Sheet7.Cells(����, 1).Interior.ColorIndex = 36
    ��� = Evaluate("MAXIFS(��1[5���ǵ���],��1[ [  ����] ],""=SH.68*"")")
    Sheet7.Cells(���� + 1, 1) = "����"
    Sheet7.Cells(���� + 1, 2) = "����"
    Sheet7.Cells(���� + 1, 3) = "��������"
    Sheet7.Cells(���� + 1, 4) = "5���ǵ���"
    Set rng = Range("��1[5���ǵ���]").Find(���)
    If Not rng Is Nothing Then
        h = ���� + 2
'        firstAddress = rng.Address
'        Do
            Sheet7.Cells(h, 1) = rng.Offset(0, -13)
            Sheet7.Cells(h, 2) = rng.Offset(0, -12)
            Sheet7.Cells(h, 3) = rng.Offset(0, -9)
            Sheet7.Cells(h, 4) = Format(rng, "0.00%")
'            h = h + 1
'             Set rng = Range("��1[5���ǵ���]").FindNext(rng)
'        Loop While Not rng Is Nothing And rng.Address <> firstAddress
    End If
End Sub



Sub ���Ǽ�¼()
    On Error Resume Next
    Range("ͼ��[����]").Replace Date, "", 1
    Range("ͼ��[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    ���� = Date
    ��ͣ = Sheet5.Range("a1").End(xlDown).Row - 1
    ���� = Evaluate("COUNTIF(���ǹ�Ʊ!D2:D" & ��ͣ + 1 & ","">1"")")
    ������� = Evaluate("MAX(��2[��������])")
    ����θ� = Evaluate("LARGE(��2[��������],2)")
    ��ҵ��� = Evaluate("MAX(��1[��������])")
    �������� = ""
    For i = 2 To ��ͣ + 1
        If Left(Sheet5.Range("a" & i), 5) <> "SZ.30" And Sheet5.Range("d" & i) = ������� Then
            If �������� = "" Then
                �������� = Sheet5.Range("b" & i) & vbLf & Sheet5.Range("f" & i)
            Else
                �������� = �������� & vbLf & Sheet5.Range("b" & i) & vbLf & Sheet5.Range("f" & i)
            End If
        End If
    Next
    Range("ͼ��").ListObject.ListRows.Add.Range = Array(����, ����, ��ͣ, "", �������, ����θ�, ��ҵ���, ��������)
    Dim Wb As Workbook
    'Application.DisplayAlerts = False
    Set Wb = Workbooks.Open(ThisWorkbook.Path & "\���̼�¼.xlsx")
    'Wb.Range("ͼ��").ListObject.ListRows.Add.Range = Array(����, ����, ��ͣ, "", �������, ����θ�, ��ҵ���, ��������)
    Wb.Sheets("Sheet2").Range("ͼ��[����]").Replace Date, "", 1
    Wb.Sheets("Sheet2").Range("ͼ��[����]").SpecialCells(4).Rows.Delete Shift:=xlShiftUp
    Wb.Sheets("Sheet2").Range("ͼ��").ListObject.ListRows.Add.Range = Array(����, ����, ��ͣ, "", �������, ����θ�, ��ҵ���, ��������)
    ���� = Wb.Sheets("sheet1").UsedRange.Rows.Count
    Sheet7.UsedRange.Rows.Copy Wb.Sheets("sheet1").Range("a" & ���� + 1)
    Wb.Close True
    MsgBox "�ѵ���"
End Sub

Sub sss()
    Sheet5.Range("a:g").Sort "��ͣ������", 2, , , , , , 1
End Sub
