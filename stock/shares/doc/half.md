

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


SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
        
        SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_year  <2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_year  <2022 GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        )
        
        
SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
        
        SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        )
    
    
SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
        SELECT code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end > p_start GROUP BY code_id
        );

// 2022年以前 第一季涨幅 70%的股票，在2022年还是涨的股票的行业： 42个行业
SELECT mc_shares_join_industry.industry_code_id,mc_shares_name.name FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022  and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022   GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        left join mc_shares_join_industry on mc_shares_join_industry.code_id = c.code_id
        left join mc_shares_name on mc_shares_join_industry.industry_code_id = mc_shares_name.code
        where c.code_id in (
        SELECT code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end > p_start GROUP BY code_id
        )
        group by mc_shares_join_industry.industry_code_id 


// 2022年以前 第一季涨幅 70%的股票，在2022年还是涨的股票的行业： 42个行业中， 3月份涨的行业有32个,而3月份一共有71个行业处于上涨状态
SELECT mc_shares_join_industry.industry_code_id,mc_shares_name.name FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022  and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022   GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        left join mc_shares_join_industry on mc_shares_join_industry.code_id = c.code_id
        left join mc_shares_name on mc_shares_join_industry.industry_code_id = mc_shares_name.code
        where c.code_id in (
        SELECT code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end > p_start GROUP BY code_id
        )
        and mc_shares_join_industry.industry_code_id in (
            SELECT mc_shares_industry.code_id FROM `mc_shares_industry` 
            left join (select code_id,p_end from mc_shares_industry where  date_as = '2022-03-31') y on y.code_id = mc_shares_industry.code_id
            where  date_as = '2022-03-01'  and mc_shares_industry.p_start > y.p_end
        )
        group by mc_shares_join_industry.industry_code_id 
        
// 在 2022年以前 第一季涨幅 70%的股票，在 2022年涨的行业中，都有哪些股票： 共 133 行 个股票
SELECT c.code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1  and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        left join mc_shares_join_industry on mc_shares_join_industry.code_id = c.code_id
        where mc_shares_join_industry.industry_code_id in (
        
            SELECT mc_shares_join_industry.industry_code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
            from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022  and p_end > p_start GROUP BY code_id) t1
            LEFT JOIN 
                (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022   GROUP BY code_id) t2 
            on t1.code_id = t2.code_id
            where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
            HAVING rang > 0.7 and rang < 1   ) c
            left join mc_shares_join_industry on mc_shares_join_industry.code_id = c.code_id
            where c.code_id in (
            SELECT code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end > p_start GROUP BY code_id
            )
            group by mc_shares_join_industry.industry_code_id 
        )
        
        
// 在 2022年以前 第一季涨幅 70%的股票，在 2022年涨的行业中，共 133 行 个股票 哪些股票是下跌的
SELECT c.code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1  and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        left join mc_shares_join_industry on mc_shares_join_industry.code_id = c.code_id
        where mc_shares_join_industry.industry_code_id in (
            SELECT mc_shares_join_industry.industry_code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
            from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022  and p_end > p_start GROUP BY code_id) t1
            LEFT JOIN 
                (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  <2022   GROUP BY code_id) t2 
            on t1.code_id = t2.code_id
            where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
            HAVING rang > 0.7 and rang < 1   ) c
            left join mc_shares_join_industry on mc_shares_join_industry.code_id = c.code_id
            where c.code_id in (
            SELECT code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end > p_start GROUP BY code_id
            )
            group by mc_shares_join_industry.industry_code_id 
        )
        and c.code_id  in (
            SELECT code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end < p_start GROUP BY code_id
            )
   
// 查行业涨幅
SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
        
        SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_year  <2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_year  <2022 GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        )
        
        
SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
        
        SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        )
 
 
 // 2022年 以前， 历年都增长的行业
 SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_year !=2022  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
        HAVING rang > 0.7 and rang < 1 
   
 // 历年增长的行业中， 普遍增长的股票   
 select code_id from  mc_shares_join_industry where industry_code_id in (
     SELECT code_id from (
        SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
            from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
            LEFT JOIN 
                (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_year !=2022  GROUP BY code_id) t2 
            on t1.code_id = t2.code_id
            LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
            HAVING rang > 0.7 and rang < 1 
     )c
 )
 
 // 历年增长的行业中， 普遍增长的股票  并 历年 1季度普遍上涨的股票 69
 // 历年增长的行业中， 普遍增长的股票  并 历年 1季度普遍上涨的股票 且今年上涨的股票 48
 SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year !=2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year !=2022  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
            select code_id from  mc_shares_join_industry where industry_code_id in (
                 SELECT code_id from (
                    SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
                        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
                        LEFT JOIN 
                            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_year !=2022  GROUP BY code_id) t2 
                        on t1.code_id = t2.code_id
                        LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
                        HAVING rang > 0.7 and rang < 1 
                 )c
             )
        )
        and c.code_id  in (
            SELECT code_id FROM `mc_shares_season` where  p_season = 1 and p_year  =2022 and p_end < p_start GROUP BY code_id
        )


SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 2 and p_year !=2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 2 and p_year !=2022  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
            select code_id from  mc_shares_join_industry where industry_code_id in (
                 SELECT code_id from (
                    SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
                        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 2 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
                        LEFT JOIN 
                            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 2 and p_year !=2022  GROUP BY code_id) t2 
                        on t1.code_id = t2.code_id
                        LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
                        HAVING rang > 0.7 and rang < 1 
                 )c
             )
        )
        and code_id not in (SELECT code from mc_shares_name where name like "ST%"  )
        

1季度48只下跌股票所属行业
  家电行业		钢铁行业		化纤行业		装修建材		通用设备		航天航空		酿酒行业		纺织服装		
  造纸印刷		汽车零部件	玻璃玻纤		化学制品		工程建设
  
1季度21只上涨股票所属行业
                汽车零部件               装修建材       通用设备                             纺织服装
  造纸印刷                               化学制品      工程建设
                  水泥建材   	
select t.code_id,mc_shares_name.name from (SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year !=2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 1 and p_year !=2022  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
            select code_id from  mc_shares_join_industry where industry_code_id in (
                 SELECT code_id from (
                    SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
                        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season =1 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
                        LEFT JOIN 
                            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 1 and p_year !=2022  GROUP BY code_id) t2 
                        on t1.code_id = t2.code_id
                        LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
                        HAVING rang > 0.7 and rang < 1 
                 )c
             )
        )
        and code_id not in (SELECT code from mc_shares_name where name like "ST%"  )) t
LEFT JOIN mc_shares_join_industry on mc_shares_join_industry.code_id = t.code_id 
LEFT JOIN mc_shares_name on mc_shares_join_industry.industry_code_id = mc_shares_name.code
where t.code_id  in (
select code_id from  mc_shares_season where  p_season = 1 and p_year =2022 and p_end > p_start GROUP BY code_id
)  
ORDER BY `t`.`code_id` ASC



select t.code_id,mc_shares_name.name from (SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 2 and p_year !=2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = 2 and p_year !=2022  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
            select code_id from  mc_shares_join_industry where industry_code_id in (
                 SELECT code_id from (
                    SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
                        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season =2 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
                        LEFT JOIN 
                            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_season` where  p_season = 2 and p_year !=2022  GROUP BY code_id) t2 
                        on t1.code_id = t2.code_id
                        LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
                        HAVING rang > 0.6 and rang < 1 
                 )c
             )
        )
        and code_id not in (SELECT code from mc_shares_name where name like "ST%"  )) t
LEFT JOIN mc_shares_join_industry on mc_shares_join_industry.code_id = t.code_id 
LEFT JOIN mc_shares_name on mc_shares_join_industry.industry_code_id = mc_shares_name.code



// 查某个月行业的增长情况
SELECT code_id,name,rang from (
    SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_month` where  p_month =6 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_month` where  p_month = 6 and p_year !=2022  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
        HAVING rang > 0.6 and rang < 1 
 )c
 where code_id in (
    select m2.industry_code_id FROM mc_shares_name m1
    left join mc_shares_join_industry m2 on m1.code = m2.code_id
    LEFT JOIN mc_shares_name m3 on m2.industry_code_id = m3.code
    where m1.code in('601038','002312','600667','002828', '601908','601139','601678','600835')
 )
 
 
 select m2.industry_code_id,m3.name, m1.code FROM mc_shares_name m1
    left join mc_shares_join_industry m2 on m1.code = m2.code_id
    LEFT JOIN mc_shares_name m3 on m2.industry_code_id = m3.code
    where m1.code in('601038','002312','600667','002828', '601908','601139','601678','600835')

601139  快报发了，业绩一般
002828  未发财报
600667  业绩一般
601678  业绩好
002312  ``





