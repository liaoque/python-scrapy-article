b = {}; a.forEach(item=>{if(!b[item]){ b[item] =1 }else{ b[item]++ } })
d = []; for (c in b){if (e.indexOf(c) ==-1) { d.push({name: c, c: b[c]}) } }
d.sort(function(a, b) {
  return b.c - a.c;
});


Sub 主线()
'
' 宏3 宏

    Dim gp, ngp As Range
    Dim dic, dic2 As Object
    Set dic = CreateObject("scripting.dictionary")
    Set dic2 = CreateObject("scripting.dictionary")
    Dim nogn As String
    Dim arr() As String
    
    nogn2 = Sheet4.Range("h39")
    
    Sheet25.Cells.Clear
    
    
    For Each gp In Sheet2.Range("A:A")
        dic2(gp.Value) = gp.Offset(0, 4).Value
    Next gp
    
    For Each gp In Sheet23.Range("A:A")
        If gp <> "  代码" Then
             nogn = dic2(gp.Value)
             arr = Split(nogn, ";")
             
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
        
    Next gp
    
    For Each gp In Sheet24.Range("A:A")
        
        If gp <> "  代码" Then
             nogn = dic2(gp.Value)
             arr = Split(nogn, ";")
             
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
    

    Next gp
        
    Sheet25.Range("a1") = "所属概念"
    Sheet25.Range("b1") = "数量"
    Sheet25.Range("a2").Resize(dic.Count) = Application.Transpose(dic.keys)
    Sheet25.Range("b2").Resize(dic.Count, 1) = Application.Transpose(dic.items)
    Sheet25.Range("a:h").Sort "数量", 2, , , , , , 1
    
    
End Sub
