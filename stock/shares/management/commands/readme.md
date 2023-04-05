
1. 计算kdj closepoll.py
2. 计算行业macd industry_macd.py
3. 分红 fh.py
4. 计算行业kdj industry.py
5. 支撑位代码检测 industry-max-min.py
6. 计算macd macd.py
7. 财报分析 shares_finance.py
10. 板块排行 shares_block_top.py
11. 统计日期 shares_date.py
12. 每年都涨的股票 shares_half_statistics.py
13. 上半年和下半年股票 shares_half_year.py 
14. 最高和最低
15. 行业中位数 shares_industry_finance.py
16. 每月行业 shares_industry_month.py shares_industry_season.py shares_industry_week.py
16. 每月行业 shares_month.py shares_season.py shares_wheel.py
17. 海外业务 seach_out.py
18. 公司最低价 stock_day.py
19. 股东人数 stock_members.py
20. 放量 stock_large_day.py
21. 统计涨幅比例 rate.py


 财报分析 确定公司
 计算macd 确定公司
 支撑位代码检测 确定反弹
 股东人数 
 统计涨幅比例 确定跑赢大盘的公司
 
 
 
 1. 先选强势股
 2. 强势股挑macd向上
 3. 选财务好的
 记录下来
 

// 强势股挑macd向上, 选财务好的
```
select * from mc_shares_name 
where mc_shares_name.macd_up = 2
and mc_shares_name.finance_up = 1
and code in (
    select code_id from (
     select code_id, count(1) c from mc_shares 
        where date_as > '2023-03-21' and p_range_win = 1
        group by code_id
        having c > 5
        order by c desc
    ) t
)
```


// 买入年报好的
2021年
回测 2022年




