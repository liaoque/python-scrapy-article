Attribute VB_Name = "模块5"
Sub 主线()

    Dim t, t1, t0, t4
    Dim gp, ngp As Range
    Dim dic As Object
    
    Dim dic2, dic3, dic4 As Object
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
        If ngp = "" Then Exit For
        
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
        If ngp = "" Then Exit For
        Set rng = Range("表1[  代码]").Find(ngp, , , 1)
        
        If Not rng Is Nothing Then
         '   rng.Offset(0, 24) = "N20"
            ngp.Offset(0, 3) = rng.Offset(0, 4)
        End If
    Next
    
    t4 = 2
    
    If Sheet4.Range("h3") = "封单开" Then
        
        For Each gp In Sheet15.Range("A:A")
            If gp <> "  代码" And gp <> "" Then
                Set rng = Range("表1[  代码]").Find(gp, , , 1)
                nogn = rng.Offset(0, 4).Value
                Call UpdateDictionary(nogn, dic, rng.Value)
               Sheet26.Range("o" & t4) = rng
                    Sheet26.Range("p" & t4) = rng.Offset(0, 1)
                    Sheet26.Range("q" & t4) = rng.Offset(0, 2)
                    Sheet26.Range("r" & t4) = rng.Offset(0, 4)
                t4 = t4 + 1
            End If
        Next gp
        
        
    Else
    
        For Each gp In Sheet2.Range("A:A")
    'For Each gp In Sheet26.Range("A:A")
    
            If gp <> "  代码" And gp <> "" Then
                'Set rng = Range("表1[  代码]").Find(gp, , , 1)
                Set rng = gp
                'If Not rng Is Nothing Then
            '    Debug.Print rng.Offset(0, 15)
                
                If rng.Offset(0, 15) > 0 Or (rng.Offset(0, 21) > 0) Then
                   nogn = rng.Offset(0, 4).Value
                   Call UpdateDictionary(nogn, dic, rng.Value)
             
                   Sheet26.Range("o" & t4) = rng
                    Sheet26.Range("p" & t4) = rng.Offset(0, 1)
                    Sheet26.Range("q" & t4) = rng.Offset(0, 2)
                    Sheet26.Range("r" & t4) = rng.Offset(0, 4)
                   t4 = t4 + 1
                End If
                
            End If
        
        Next gp
    
    
    End If
            
    
    
    Sheet25.Range("a1") = "所属概念"
    Sheet25.Range("b1") = "数量"
    If dic.Count > 0 Then
        Sheet25.Range("a2").Resize(dic.Count) = Application.Transpose(dic.keys)
        Sheet25.Range("b2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
        Sheet25.Range("a:h").Sort "数量", 2, , , , , , 1
    End If
    
    dic.RemoveAll
    For Each gp In Sheet26.Range("A:A")
        If gp = "" Then Exit For
        If gp <> "  代码" Then
            Set rng = Range("表1[  代码]").Find(gp, , , 1)
            If Not rng Is Nothing Then
                nogn = rng.Offset(0, 4).Value
                Call UpdateDictionary(nogn, dic, rng.Value)
            End If
        End If
    Next gp

    Sheet25.Range("i1") = "主线源所属概念"
    Sheet25.Range("j1") = "主线源数量"
    If dic.Count > 0 Then
        Sheet25.Range("i2").Resize(dic.Count) = Application.Transpose(dic.keys)
        Sheet25.Range("j2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    End If
End Sub



Sub 概念替换()
    Dim gp, ngp As Range
    For i = 2 To 1000
        Set ngp = Sheet26.Range("a" & i)
        If ngp = "" Then Exit For
        Debug.Print ngp
        
        Set rng = Range("表1[  代码]").Find(ngp, , , 1)
        
        If Not rng Is Nothing Then
         '   rng.Offset(0, 24) = "N20"
            ngp.Offset(0, 3) = rng.Offset(0, 4)
        End If
    Next
    
    
End Sub




Sub UpdateDictionary(nogn As String, ByRef dic As Object, nogn4 As String)

    Dim dic4 As Object
    Set dic4 = CreateObject("Scripting.Dictionary")
    Dim arr2 As Variant
    Dim arr As Variant
    Dim i As Long
    Dim key As Variant
    
    ' 分割字符串并更新dic4
    arr2 = Split(nogn, ";")
    For i = LBound(arr2) To UBound(arr2)
        If Not dic4.Exists(arr2(i)) Then
            dic4(arr2(i)) = True
        End If
    Next i
    
    ' 将dic4的键转移到数组arr中
    i = 1
    ReDim arr(1 To dic4.Count)
 
    
    For Each key In dic4.keys
        arr(i) = key
        i = i + 1
    Next key
    dic4.RemoveAll
    
    ' 更新传入的dic
    Dim nogn2 As String
    nogn2 = Sheet4.Range("h39")
    
    
    
    For i = LBound(arr) To UBound(arr)
       If arr(i) <> "" And InStr(nogn2, ";" & arr(i) & ";") = 0 And arr(i) <> "所属概念" Then
          If Not dic.Exists(arr(i)) Then
              dic(arr(i)) = 1
          Else
              dic(arr(i)) = dic(arr(i)) + 1
          End If
          
        
       End If
    Next i

    
    
End Sub

