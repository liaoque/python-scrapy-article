SELECT  mc_stock_members.code_id from  mc_stock_members 
    LEFT JOIN (
        SELECT code_id, date_as, avg_free_shares,members 
            FROM `mc_stock_members` 
            where date_as > '2022-05-22'
            GROUP by code_id ORDER BY date_as desc
            ) t 
    ON t.code_id = mc_stock_members.code_id 
    left join mc_shares_join_industry as i on t.code_id = i.code_id
    left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2 and gpm_ex > 1000) n on n.code = i.industry_code_id
    left JOIN (SELECT code_id, max(date_as) as date_as FROM `mc_stock_members` where date_as <= '2022-05-22' group by code_id) m on m.code_id = i.code_id 
    
    where t.date_as > mc_stock_members.date_as
    and n.roe  > 15
	and t.members < mc_stock_members.members
    and m.date_as = mc_stock_members.date_as
    
    GROUP by mc_stock_members.code_id
     
    ORDER BY  mc_stock_members.code_id asc, mc_stock_members.date_as desc;
    
-------
-------
    
SELECT COUNT(1) FROM `mc_shares_buys` where buy_start > sell_end
UNION ALL
SELECT COUNT(1)  FROM `mc_shares_buys` where buy_start < sell_end
UNION ALL
SELECT sum(sell_end) -sum(buy_start)  FROM `mc_shares_buys`
UNION ALL
SELECT COUNT(1) FROM `mc_shares_buys` where buy_pre > sell_end
UNION ALL
SELECT COUNT(1)  FROM `mc_shares_buys` where buy_pre < sell_end
UNION ALL
SELECT sum(sell_end) -sum(buy_pre)  FROM `mc_shares_buys`;



macd， pem
    - 240, 181, 
    - 138, 287
    
    
/// 高业绩公司
SELECT implement_date_as,register_date_as,t.code_id, s.p_start , e.p_end from (
    SELECT implement_date_as,register_date_as,code_id  
    FROM `mc_shares_fh` 
    where implement_date_as > '2022-04-01'  and 
        code_id in (SELECT code FROM `mc_shares_name` where npmos_ex > 5000 and npmos_ex < 10000)  
    ORDER BY `mc_shares_fh`.`implement_date_as`  ASC
) t
LEFT JOIN mc_shares s on s.code_id = t.code_id and s.date_as = t.implement_date_as
LEFT JOIN mc_shares e on e.code_id = t.code_id and e.date_as = t.register_date_as
LEFT JOIN mc_shares_join_block i on i.code_id = t.code_id 
LEFT JOIN (SELECT code  FROM `mc_shares_name` WHERE code_type = 4 and `name` LIKE '%汽车芯片%') n on n.code = i.block_code_id
where s.p_start < e.p_end
and n.gpm_ex > 1500;



// 查芯片板块，净利润同比增长 20%， 且高于行业平均净利润， 
select * from mc_shares_name t
LEFT JOIN mc_shares_join_industry i on i.code_id = t.code 
LEFT JOIN mc_shares_name n1 on n1.code = i.industry_code_id
LEFT JOIN mc_shares_join_block b on b.code_id = t.code 
LEFT JOIN (SELECT code  FROM `mc_shares_name` WHERE code_type = 4 and `name` LIKE '%汽车芯片%') n2 
    on n2.code = b.block_code_id
where t.code_type = 1
and t.npmos_ex > 2000
and t.npmos_ex > n1.npmos_ex
and n2.code is not null


select * from mc_shares_name t
LEFT JOIN mc_shares_join_industry i on i.code_id = t.code 
LEFT JOIN  (SELECT code  FROM `mc_shares_name` WHERE code_type = 2 and `name` LIKE '%钢铁%') n1 on n1.code = i.industry_code_id
where t.code_type = 1
and t.npmos_ex > 2000
and t.npmos_ex > n1.npmos_ex
and n2.code is not null



SELECT code FROM `mc_shares_name` t where npmos_ex > 5000 
LEFT JOIN mc_shares_join_industry i on i.code_id = t.code_id 
LEFT JOIN mc_shares_name n on n.code = i.industry_code_id
where s.p_start < e.p_end
and n.gpm_ex > 1500;


t1 今天
t2 昨天
t3 前天
buy1 环比
buy2 同比
同比 > 环比： 分歧
环比 > 同比： 看多
select ((t1.buy -t2.buy)/ abs(t2.buy)) buy1,  ((t1.buy -t3.buy)/ abs(t3.buy)) buy2, t1.industry_code_id, t1.name,t1.buy/ 1000000, t2.buy/ 1000000, t3.buy/ 1000000 from (
    SELECT SUM(master_buy_sum - master_buy_sell) buy,i.industry_code_id, t.name FROM `mc_shares`  n
    left join mc_shares_join_industry as i on n.code_id = i.code_id
    left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2) t on t.code = i.industry_code_id
    WHERE date_as = '2022-06-27'   and industry_code_id is not null
    GROUP BY industry_code_id 
) t1
left join (
    SELECT SUM(master_buy_sum - master_buy_sell) buy,i.industry_code_id, t.name FROM `mc_shares`  n
    left join mc_shares_join_industry as i on n.code_id = i.code_id
    left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2) t on t.code = i.industry_code_id
    WHERE date_as = '2022-06-24'   and industry_code_id is not null
    GROUP BY industry_code_id 
) t2 on t1.industry_code_id = t2.industry_code_id 
left join (
    SELECT SUM(master_buy_sum - master_buy_sell) buy,i.industry_code_id, t.name FROM `mc_shares`  n
    left join mc_shares_join_industry as i on n.code_id = i.code_id
    left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2) t on t.code = i.industry_code_id
    WHERE date_as = '2022-06-23'   and industry_code_id is not null
    GROUP BY industry_code_id 
) t3 on t1.industry_code_id = t3.industry_code_id  
where t1.buy > t2.buy and t1.buy > 0 
HAVING buy1 > buy2
ORDER BY `buy1` ASC;




SELECT SUM(master_buy_sum - master_buy_sell) buy,i.industry_code_id, t.name,date_as FROM `mc_shares`  n
    left join mc_shares_join_industry as i on n.code_id = i.code_id
    left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2) t on t.code = i.industry_code_id
    WHERE date_as >= '2022-06-22' and date_as < '2022-06-28'  and industry_code_id is not null
    and industry_code_id = 'BK0437'
    GROUP BY date_as;

