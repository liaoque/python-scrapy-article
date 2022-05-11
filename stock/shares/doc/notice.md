


当前均价 * 上一季度持股数 - 上一季股本


预期
所有人都知道某个点会跌或者涨，这个叫做预期


下跌预期，这是一定的
所有人都知道某个点会跌，因此有些聪明的人就把预期提前了


上涨预期
所有人都知道某个点会涨，因此涨的时候，就在开始消化预期，
    当达到该点或者前几天的时候就会停止涨
    
反预期
因为黑天鹅灰犀牛事件，可能导致上涨或者下跌预期逻辑被破坏，而延迟上涨或下跌

买股票方式
20，20，20，40


情绪，估值，盈利预期，个股选时

盈利预期：
这个跟上涨预期是一个逻辑


个股选时
沿海， 内河航运，空运，信息基础化建设
内河港口的升级重建，码头，造船中小型机场，5g信息网络，大型计算机

机构重仓个股
排查近期加仓的股票
```
https://data.eastmoney.com/gjdcg/mx.html
https://datacenter-web.eastmoney.com/api/data/v1/get?callback=&sortColumns=TOTAL_SHARES_CHANGE&sortTypes=-1&pageSize=150&pageNumber=1&reportName=RPT_NATIONAL_STATISTICS&columns=ALL&quoteColumns=&source=WEB&client=WEB&filter=(REPORT_DATE%3D%272022-03-31%27)
a.result.data.map(item=>item.SECURITY_CODE).join('","')

SELECT mc_shares_join_industry.code_id, mc_shares_join_industry.industry_code_id,mc_shares_name.name,c.name from mc_shares_join_industry 
LEFT JOIN mc_shares_name on mc_shares_name.code = mc_shares_join_industry.industry_code_id
LEFT JOIN mc_shares_name as c on c.code = mc_shares_join_industry.code_id
where mc_shares_join_industry.code_id in("000400","002475","600557","002008","601666","600276","600535","002236","000898","601899","000100","002250","600851","600787","000600","600435","600028","601992","600894","000661","601012","600757","002241","600977","000069","601888","600309","002204","000997","600839","601718","600219","600369","600519","002202","000963","601117","000652","002594","000563","601628","000062","600325","002500","000031","001979","000729","000686","600812","601139","000402","601898","000006","601225","600636","002194","600887","601088","000598","002561","600570","002365","000417","000709","002073","300321","600729","600436","600064","300033","600547","600489","002294","002646","600703","600826","600750","600415","600999","600422","600660","002066","000061","000895","000001","600874","600066","600780","600332","600011","002142","000157","600196","600837","601818","600000","600674","600398","300498","002225","600297","601006","000823","601633","600578","601231","000063","300253","601009","600089","000883","300120","000631","600120","600863","300059","600169","601158","600198","000039","600586","601985","600688","600657","600010","600058","000539","002267","002038","600805","601600","002029","600510","000728","600761")  
ORDER BY `mc_shares_name`.`name` ASC;



SELECT mc_shares_join_industry.code_id, mc_shares_join_industry.industry_code_id,mc_shares_name.name,c.name 
from mc_shares_join_industry 
LEFT JOIN mc_shares_name on mc_shares_name.code = mc_shares_join_industry.industry_code_id
LEFT JOIN mc_shares_name as c on c.code = mc_shares_join_industry.code_id
where mc_shares_join_industry.code_id in(
"600030","601198","601669","002475","600737","601336","000528","000400","002007","600118","600037","603328","600297","600000",
"000100","600812","600027","000568","600741","601018","002396","600299","600428","300396","600373","600220","601139","002594",
"601088","600398","601628","000563","601818","000898","002561","000598","600887","002194","600570","002500","000883","600325",
"000963","000062","000031","000652","601117","601985","000686","000729","001979","000538","601801","002304","000690","601607",
"601788","601111","601800","002153","601989","601997","000625","601021","000897","300024","601601","000858","002482","600017",
"600031","600019","600406","600886","600690","300408","002246","600062","601901","601166","600583","600482","000002","603288",
"600633","600585","600587","600642","600795","002053","000768","600029","600410","601066","600023","600362","600021","601000",
"601808","600436","600729","002225","000063","000061","601899","300059","000417","300033","600064","600547","300253","600837",
"600780","600874","600011","000001","600196","000157","000895","300498","600332","002142","601009","600578","002294","002646",
"600276","600660","600557","000823","600826","600750","002008","600703","002066","600089","300321","000709","002236","002365",
"002073","600415","600422","600999","601633","600489","601231","601006","600787","002250","601666","600219","601718","600757",
"000600","600851","600894","000006","601898","601225","600636","000402","601012","000661","600435","601992","600028","600839",
"002241","600977","600309","002204","000069","000997","601888","600519","002202","600674","600066","600369"
)  
ORDER BY `mc_shares_name`.`name` ASC;




撒普的通往财富自由之路
机械交易系统
海龟交易法则

统计熊市哪些行业是涨的，每个月，哪些股票是涨的
http://baijiahao.baidu.com/s?id=1695019355258746519&wfr=spider&for=pc




                    if not ((p_year == 2007 and p_month in [11, 12]) or (
                            p_year == 2008 and p_month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) or (
                                    p_year == 2009 and p_month in [7, 8, 9, 10, 11, 12]) or (p_year == 2010) or (
                                    p_year == 2011) or (
                                    p_year == 2012 and p_month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]) or (
                                    p_year == 2013 and p_month in [3, 4, 5, 6, 9, 10, 11, 12]) or (
                                    p_year == 2014 and p_month in [1, 2, ]) or (
                                    p_year == 2015 and p_month in [6, 7, 8, 9, 10, 11, 12]) or (
                                    p_year == 2016 and p_month in [1]) or (
                                    p_year == 2018 and p_month in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])):
                        # 非熊市
                        continue


SELECT t.code_id,mc_shares_name.name, COUNT(1) from (
select * from mc_shares_industry_month where p_year = 2018 and p_month in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
) t 
LEFT JOIN mc_shares_name on mc_shares_name.code = t.code_id
where p_end > p_start
GROUP BY code_id  
ORDER BY `COUNT(1)`  DESC;



SELECT t.code_id,mc_shares_name.name, COUNT(1) from (
select * from mc_shares_industry_month where p_year = 2001 and p_month in (6, 7, 8, 9, 10, 11, 12)
UNION select * from mc_shares_industry_month where p_year = 2005 and p_month in (1, 2, 3, 4, 5)
UNION select * from mc_shares_industry_month where p_year  in (2002,2003,2004)
UNION select * from mc_shares_industry_month where p_year = 2007 and p_month in (11, 12)
UNION select * from mc_shares_industry_month where p_year = 2008 and p_month in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
UNION select * from mc_shares_industry_month where p_year = 2009 and p_month in (7, 8, 9, 10, 11, 12)
UNION select * from mc_shares_industry_month where p_year = 2010 
UNION select * from mc_shares_industry_month where p_year = 2011 
UNION select * from mc_shares_industry_month where p_year = 2012 and p_month in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
UNION select * from mc_shares_industry_month where p_year = 2013 and p_month in (3, 4, 5, 6, 9, 10, 11, 12)
UNION select * from mc_shares_industry_month where p_year = 2014 and p_month in (1, 2)
UNION select * from mc_shares_industry_month where p_year = 2015 and p_month in (6, 7, 8, 9, 10, 11, 12)
UNION select * from mc_shares_industry_month where p_year = 2016 and p_month in (1)
UNION select * from mc_shares_industry_month where p_year = 2018 and p_month in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
) t 
LEFT JOIN mc_shares_name on mc_shares_name.code = t.code_id
where p_end > p_start
GROUP BY code_id  
ORDER BY `COUNT(1)`  DESC;



```

情绪


估值

杀估值行情，买低估值股票
原理： 估值高的公司下降能影响整体估值，估值低的公司上涨影响不了



煤炭价格指数
https://www.cctd.com.cn/index.php?m=content&c=index&a=lists&catid=454&data=CCTD%C7%D8%BB%CA%B5%BA%B6%AF%C1%A6%C3%BA%BC%DB%B8%F1&name=CCTD%C7%D8%BB%CA%B5%BA%B6%AF%C1%A6%C3%BA%BC%DB%B8%F1




反过来，买股票或加仓就很简单了。选逻辑强劲，估值低位，业绩在线(增速越高越好，此处指未来复合增速)的股票，
这样三点齐备的好事会轮到咱？过去两年挺难的，现在进入了超级easy模式，遍地都是。投资人借机打造好自己的投资组合，以一个极强的弹性迎接下一轮牛市到来

