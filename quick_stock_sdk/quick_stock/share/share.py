import tushare as ts


class TushareObj:
    token = None
    pro = None

    def __init__(self, token):
        token = 'aa094b770b064cc444cdbaa934e352414cbdf70ac4c65b825db44773'
        self.token = token
        self.pro = ts.pro_api(token)

    def set_token(self, token):
        self.token = token
        self.pro = ts.pro_api(token)

    def stock_basic(self, name="", market="", list_status='L', exchange="", is_hs=""):
        """
        获取股票信息

        输入参数：
            name (str): 名称，非必选
            market (str): 市场类别（主板/创业板/科创板/CDR/北交所），非必选
            list_status (str): 上市状态 L上市 D退市 P暂停上市，默认是L，非必选
            exchange (str): 交易所 SSE上交所 SZSE深交所 BSE北交所，非必选
            is_hs (str): 是否沪深港通标的，N否 H沪股通 S深股通，非必选

        输出参数：
            ts_code (str): TS代码，默认显示
            symbol (str): 股票代码，默认显示
            name (str): 股票名称，默认显示
            area (str): 地域，默认显示
            industry (str): 所属行业，默认显示
            fullname (str): 股票全称，非默认显示
            enname (str): 英文全称，非默认显示
            cnspell (str): 拼音缩写，默认显示
            market (str): 市场类型（主板/创业板/科创板/CDR），默认显示
            exchange (str): 交易所代码，非默认显示
            curr_type (str): 交易货币，非默认显示
            list_status (str): 上市状态 L上市 D退市 P暂停上市，非默认显示
            list_date (str): 上市日期，默认显示
            delist_date (str): 退市日期，非默认显示
            is_hs (str): 是否沪深港通标的，N否 H沪股通 S深股通，非默认显示
            act_name (str): 实控人名称，默认显示
            act_ent_type (str): 实控人企业性质，默认显示
        """
        return self.pro.stock_basic(**{
            "ts_code": "",
            "name": name,
            "exchange": exchange,
            "market": market,
            "is_hs": is_hs,
            "list_status": list_status,
            "limit": "",
            "offset": ""
        }, fields=[
            "symbol",
            "name",
            "area",
            "industry",
            "market",
            "exchange",
            "list_status",
            "list_date",
            "delist_date",
            "is_hs",
            "act_name",
            "act_ent_type"
        ])

    def index_basic(self, name=None, market='SSE', publisher=None, category=None):
        """
        获取指数信息

        输入参数：
            ts_code (str): 指数代码，非必选
            name (str): 指数简称，非必选
            market (str): 交易所或服务商(默认SSE)，非必选
            publisher (str): 发布商，非必选
            category (str): 指数类别，非必选

        输出参数：
            ts_code (str): TS代码
            name (str): 简称
            fullname (str): 指数全称
            market (str): 市场
            publisher (str): 发布方
            index_type (str): 指数风格
            category (str): 指数类别
            base_date (str): 基期
            base_point (float): 基点
            list_date (str): 发布日期
            weight_rule (str): 加权方式
            desc (str): 描述
            exp_date (str): 终止日期
        """
        return self.pro.index_basic(**{
            "ts_code": "",
            "name": name,
            "market": market,
            "publisher": publisher,
            "category": category,
            "limit": "",
            "offset": ""
        }, fields=[
            "name",
            "market",
            "publisher",
            "category",
            "base_date",
            "base_point",
            "list_date",
            "fullname",
            "index_type",
            "weight_rule",
            "desc",
            "exp_date",
            "ts_code"
        ])

    def fund_basic(self, market='E', status=None):
        """
        获取基金信息

        输入参数：
            ts_code (str): 基金代码，非必选
            market (str): 交易市场： E场内 O场外（默认E），非必选
            status (str): 存续状态 D摘牌 I发行 L已上市，非必选

        输出参数：
            ts_code (str): 基金代码，默认显示
            name (str): 简称，默认显示
            management (str): 管理人，默认显示
            custodian (str): 托管人，默认显示
            fund_type (str): 投资类型，默认显示
            found_date (str): 成立日期，默认显示
            due_date (str): 到期日期，默认显示
            list_date (str): 上市时间，默认显示
            issue_date (str): 发行日期，默认显示
            delist_date (str): 退市日期，默认显示
            issue_amount (float): 发行份额(亿)，默认显示
            m_fee (float): 管理费，默认显示
            c_fee (float): 托管费，默认显示
            duration_year (float): 存续期，默认显示
            p_value (float): 面值，默认显示
            min_amount (float): 起点金额(万元)，默认显示
            exp_return (float): 预期收益率，默认显示
            benchmark (str): 业绩比较基准，默认显示
            status (str): 存续状态D摘牌 I发行 L已上市，默认显示
            invest_type (str): 投资风格，默认显示
            type (str): 基金类型，默认显示
            trustee (str): 受托人，默认显示
            purc_startdate (str): 日常申购起始日，默认显示
            redm_startdate (str): 日常赎回起始日，默认显示
            market (str): E场内O场外，默认显示
        """
        return self.pro.fund_basic(**{
            "ts_code": "",
            "market": market,
            "update_flag": "",
            "offset": "",
            "limit": "",
            "status": status,
            "name": ""
        }, fields=[
            "ts_code",
            "name",
            "management",
            "custodian",
            "fund_type",
            "found_date",
            "due_date",
            "list_date",
            "issue_date",
            "delist_date",
            "issue_amount",
            "m_fee",
            "c_fee",
            "duration_year",
            "p_value",
            "min_amount",
            "exp_return",
            "benchmark",
            "status",
            "invest_type",
            "type",
            "trustee",
            "purc_startdate",
            "redm_startdate",
            "market"
        ])
