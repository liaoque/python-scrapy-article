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






SELECT code FROM `mc_shares_name` t where npmos_ex > 5000 
LEFT JOIN mc_shares_join_industry i on i.code_id = t.code_id 
LEFT JOIN mc_shares_name n on n.code = i.industry_code_id
where s.p_start < e.p_end
and n.gpm_ex > 1500;