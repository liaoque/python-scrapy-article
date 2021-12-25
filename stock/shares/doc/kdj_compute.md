交点做买点
```
# 处于交叉点， 第4天是涨的股票
select sa.code_id, (sc.p_end - sb.p_end)/sb.p_end*100 from (
              select a.code_id from (
                  select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                    where date_as in ('工作日1', '工作日2', '工作日3') group by code_id
              ) a
              left join  (select k, d,code_id,j from mc_shares_kdj where date_as = '工作日2') b on a.code_id = b.code_id
              where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                    and b.k <=b.j and b.d <= b.j
    				and b.j < 30
) sa
  left join  (select p_end,code_id from mc_shares where date_as = '工作日1') sb on sa.code_id = sb.code_id
  left join  (select p_end,code_id from mc_shares where date_as = '工作日4') sc on sa.code_id = sc.code_id
 where sb.p_end < sc.p_end


select sa.code_id, (sc.p_end - sb.p_end)/sb.p_end*100 from (
              select a.code_id from (
                  select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                    where date_as in ('工作日1', '工作日2', '工作日3') group by code_id
              ) a
              left join  (select k, d,code_id,j from mc_shares_kdj where date_as = '工作日2') b on a.code_id = b.code_id
              where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                    and b.k <=b.j and b.d <= b.j
    				and b.j < 30
) sa
  left join  (select p_end,code_id from mc_shares where date_as = '工作日1') sb on sa.code_id = sb.code_id
  left join  (select p_end,code_id from mc_shares where date_as = '工作日3') sc on sa.code_id = sc.code_id
 where sb.p_end < sc.p_end
```

id date_as 交点前一天买数量， 交点买数量， 总符合条件数，拐弯买点数量， 符合条件数
id date_as 交点前一天， 买点, 2天后价值
id date_as 交点， 买点, 2天后价值
id date_as 拐点，买点, 2天后价值


// 拐弯的股票,做买点
```
select sa.code_id, (sc.p_end - sb.p_end)/sb.p_end*100 from (
  select a.code_id,a.j from (select code_id,j from mc_shares_kdj where date_as = '工作日1' and j <10) a
          left join  (select  k, d,code_id,j from mc_shares_kdj where date_as = '工作日2') b on a.code_id = b.code_id
          left join  (select code_id,j from mc_shares_kdj where date_as = '工作日3') c on a.code_id = c.code_id
  where (a.j > b.j and b.j < c.j)
) sa
  left join  (select p_end,code_id from mc_shares where date_as = '工作日3') sb on sa.code_id = sb.code_id
  left join  (select p_end,code_id from mc_shares where date_as = '工作日5') sc on sa.code_id = sc.code_id
where sb.p_end < sc.p_end


select sa.code_id, (sc.p_end - sb.p_end)/sb.p_end*100 from (
  select a.code_id,a.j from (select code_id,j from mc_shares_kdj where date_as = '2021-12-20' and j <10) a
          left join  (select code_id,j from mc_shares_kdj where date_as = '2021-12-21' ) b on a.code_id = b.code_id
          left join  (select code_id,j from mc_shares_kdj where date_as = '2021-12-22' ) c on a.code_id = c.code_id
  where (a.j > b.j and b.j < c.j)
) sa
  left join  (select p_end,code_id from mc_shares where date_as = '2021-12-22') sb on sa.code_id = sb.code_id
  left join  (select p_end,code_id from mc_shares where date_as = '2021-12-24') sc on sa.code_id = sc.code_id
where sb.p_end < sc.p_end
```