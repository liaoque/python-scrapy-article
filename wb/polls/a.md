b = {}; a.forEach(item=>{if(!b[item]){ b[item] =1 }else{ b[item]++ } })
d = []; for (c in b){if (e.indexOf(c) ==-1) { d.push({name: c, c: b[c]}) } }
d.sort(function(a, b) {
  return b.c - a.c;
});
