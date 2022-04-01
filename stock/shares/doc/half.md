

```
SELECT t1.code_id, t1.c, t2.c, t1.c / t2.c as rang 
from (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_end > p_start GROUP BY code_id) t1
LEFT JOIN 
    (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 GROUP BY code_id) t2 
on t1.code_id = t2.code_id
where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%" )
HAVING rang > 0.7 and rang < 1;
```
查询上半年 涨的概率大于70的股票