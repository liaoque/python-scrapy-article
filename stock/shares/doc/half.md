

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
 