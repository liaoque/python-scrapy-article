


// 4月  增长的行业中，增长的股票
select t.code_id,mc_shares_name.name from (SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_month` where  p_month = 4 and p_year !=2022 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_month` where  p_month = 4 and p_year !=2022  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        HAVING rang > 0.7 and rang < 1   ) c
        where code_id in (
            select code_id from  mc_shares_join_industry where industry_code_id in (
                 SELECT code_id from (
                    SELECT t1.code_id,  t1.c / t2.c as rang, mc_shares_name.name
                        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_month` where  p_month =4 and p_year  !=2022 and p_end > p_start GROUP BY code_id) t1
                        LEFT JOIN 
                            (SELECT COUNT(1) as c, code_id FROM `mc_shares_industry_month` where  p_month = 4 and p_year !=2022  GROUP BY code_id) t2 
                        on t1.code_id = t2.code_id
                        LEFT JOIN mc_shares_name on mc_shares_name.code = t1.code_id 
                        HAVING rang > 0.5 and rang < 1 
                 )c
             )
        )
        and code_id not in (SELECT code from mc_shares_name where name like "ST%"  )) t
LEFT JOIN mc_shares_join_industry on mc_shares_join_industry.code_id = t.code_id 
LEFT JOIN mc_shares_name on mc_shares_join_industry.industry_code_id = mc_shares_name.code



// 4月 上涨概率比较高的股票
SELECT t1.code_id,  t1.c / t2.c as rang,t3.name,mc_shares_name.name
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_month` where  p_month = 4 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_month` where  p_month = 4  GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        LEFT JOIN mc_shares_name t3 on t1.code_id = t3.code
        left join mc_shares_join_industry on mc_shares_join_industry.code_id = t1.code_id
        left join mc_shares_name  on mc_shares_join_industry.industry_code_id = mc_shares_name.code
        where t1.code_id not in (SELECT code from mc_shares_name where name like "%ST%"  )
        HAVING rang > 0.7 and rang < 1
        order by rang desc



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

