"""
数据模型定义

定义SDK中使用的各种数据模型和请求对象
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
import re
from datetime import datetime


@dataclass
class DataRequest:
    """
    数据请求模型
    
    用于封装数据请求的参数，支持多种数据类型的查询。
    SDK会直接从数据源获取数据并返回，不涉及缓存或数据库持久化。
    
    Attributes:
        data_type: 数据类型 (如: stock_basic, stock_daily, index_basic等)
        ts_code: 股票代码 (可选)
        start_date: 开始日期 (可选，格式: YYYYMMDD 或 YYYY-MM-DD)
        end_date: 结束日期 (可选，格式: YYYYMMDD 或 YYYY-MM-DD)
        freq: 数据频率 (可选，如: 1min, 5min, 1d, 1w, 1m)
        fields: 需要返回的字段列表 (可选)
        extra_params: 额外的请求参数 (可选)
    """
    data_type: str  # stock_basic, stock_daily, index_basic等
    ts_code: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    freq: Optional[str] = None  # 1min, 5min, 1d, 1w, 1m
    fields: Optional[List[str]] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)
    

    
    def validate(self) -> bool:
        """
        验证请求参数
        
        Returns:
            验证是否通过
            
        Raises:
            ValidationError: 参数验证失败
        """
        from quickstock.core.errors import ValidationError
        
        # 验证数据类型
        if not self.data_type:
            raise ValidationError("data_type不能为空")
        
        # 验证日期格式
        if self.start_date and not self._is_valid_date(self.start_date):
            raise ValidationError(f"start_date格式无效: {self.start_date}")
        
        if self.end_date and not self._is_valid_date(self.end_date):
            raise ValidationError(f"end_date格式无效: {self.end_date}")
        
        # 验证日期范围
        if (self.start_date and self.end_date and 
            self.start_date > self.end_date):
            raise ValidationError("start_date不能大于end_date")
        
        # 验证频率
        if self.freq and self.freq not in ['1min', '5min', '15min', '30min', 
                                          '60min', '1d', '1w', '1m']:
            raise ValidationError(f"不支持的频率: {self.freq}")
        
        return True
    
    def _is_valid_date(self, date_str: str) -> bool:
        """
        验证日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否为有效日期格式
        """
        import re
        from datetime import datetime
        
        # 支持的日期格式: YYYYMMDD, YYYY-MM-DD
        patterns = [
            r'^\d{8}$',  # YYYYMMDD
            r'^\d{4}-\d{2}-\d{2}$'  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            if re.match(pattern, date_str):
                try:
                    if len(date_str) == 8:
                        datetime.strptime(date_str, '%Y%m%d')
                    else:
                        datetime.strptime(date_str, '%Y-%m-%d')
                    return True
                except ValueError:
                    continue
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            字典格式的请求数据
        """
        return {
            'data_type': self.data_type,
            'ts_code': self.ts_code,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'freq': self.freq,
            'fields': self.fields,
            'extra_params': self.extra_params
        }


# 标准化数据模型定义

# 股票基础信息标准格式
STOCK_BASIC_COLUMNS = {
    'ts_code': str,      # 股票代码
    'symbol': str,       # 股票代码（不含后缀）
    'name': str,         # 股票名称
    'area': str,         # 所属地域
    'industry': str,     # 所属行业
    'market': str,       # 市场类型
    'list_date': str,    # 上市日期
    'is_hs': str        # 是否沪深港通标的
}

# OHLCV数据标准格式
OHLCV_COLUMNS = {
    'ts_code': str,      # 股票代码
    'trade_date': str,   # 交易日期
    'open': float,       # 开盘价
    'high': float,       # 最高价
    'low': float,        # 最低价
    'close': float,      # 收盘价
    'volume': int,       # 成交量
    'amount': float      # 成交额
}

# 指数基础信息标准格式
INDEX_BASIC_COLUMNS = {
    'ts_code': str,      # 指数代码
    'name': str,         # 指数名称
    'market': str,       # 市场
    'publisher': str,    # 发布方
    'category': str,     # 指数类别
    'base_date': str,    # 基期
    'base_point': float, # 基点
    'list_date': str     # 发布日期
}

# 基金基础信息标准格式
FUND_BASIC_COLUMNS = {
    'ts_code': str,      # 基金代码
    'name': str,         # 基金名称
    'management': str,   # 管理人
    'custodian': str,    # 托管人
    'fund_type': str,    # 基金类型
    'found_date': str,   # 成立日期
    'due_date': str,     # 到期日期
    'list_date': str,    # 上市日期
    'issue_date': str,   # 发行日期
    'delist_date': str,  # 退市日期
    'issue_amount': float, # 发行份额
    'market': str        # 市场类型
}

# 交易日历标准格式
TRADE_CAL_COLUMNS = {
    'exchange': str,     # 交易所
    'cal_date': str,     # 日历日期
    'is_open': int,      # 是否交易
    'pretrade_date': str # 上一交易日
}


# ==================== 涨停统计相关数据模型 ====================

# Market classification rules constants
MARKET_CLASSIFICATION_RULES = {
    'shanghai': {
        'patterns': [r'^60', r'^68[0-7]', r'^900'],
        'description': '上海证券交易所'
    },
    'star': {
        'patterns': [r'^688'],
        'description': '科创板'
    },
    'shenzhen': {
        'patterns': [r'^00', r'^30[0-7]', r'^200'],
        'description': '深圳证券交易所'
    },
    'beijing': {
        'patterns': [r'^8', r'^4'],
        'description': '北京证券交易所'
    }
}

# ST stock detection patterns
ST_PATTERNS = [
    r'\*ST', r'ST', r'退市', r'暂停'
]

# Limit-up thresholds by stock type
LIMIT_UP_THRESHOLDS = {
    'normal': 0.10,      # 10% for normal stocks
    'st': 0.05,          # 5% for ST stocks
    'star': 0.20,        # 20% for STAR market
    'beijing': 0.30,     # 30% for Beijing exchange (new stocks)
    'new_stock': 0.44    # 44% for new stock first day
}


@dataclass
class StockDailyData:
    """
    股票日线数据模型
    
    封装股票的日线行情数据，包括OHLCV（开高低收量）等核心指标。
    
    Attributes:
        ts_code: 股票代码 (格式: "000001.SZ")
        trade_date: 交易日期 (格式: YYYYMMDD)
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        pre_close: 前收盘价
        change: 涨跌额
        pct_chg: 涨跌幅 (%)
        vol: 成交量 (手)
        amount: 成交额 (千元)
        name: 股票名称
    """
    ts_code: str          # 股票代码 (e.g., "000001.SZ")
    trade_date: str       # 交易日期 (YYYYMMDD format)
    open: float          # 开盘价
    high: float          # 最高价
    low: float           # 最低价
    close: float         # 收盘价
    pre_close: float     # 前收盘价
    change: float        # 涨跌额
    pct_chg: float       # 涨跌幅 (%)
    vol: int            # 成交量 (手)
    amount: float        # 成交额 (千元)
    name: str           # 股票名称
    
    def __post_init__(self):
        """数据验证和类型转换"""
        self.validate()
    
    def validate(self) -> bool:
        """验证数据完整性和有效性"""
        # 验证股票代码格式
        if not self.ts_code or not re.match(r'^\d{6}\.(SH|SZ|BJ)$', self.ts_code):
            raise ValueError(f"Invalid stock code format: {self.ts_code}")
        
        # 验证交易日期格式
        if not self.trade_date or not re.match(r'^\d{8}$', self.trade_date):
            raise ValueError(f"Invalid trade date format: {self.trade_date}")
        
        # 验证价格数据
        price_fields = ['open', 'high', 'low', 'close', 'pre_close']
        for field_name in price_fields:
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"Invalid {field_name}: {value}")
        
        # 验证价格逻辑关系
        if not (self.low <= self.open <= self.high and 
                self.low <= self.close <= self.high):
            raise ValueError("Price relationship validation failed")
        
        # 验证成交量和成交额
        if self.vol < 0 or self.amount < 0:
            raise ValueError("Volume and amount must be non-negative")
        
        # 验证股票名称
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Stock name is required and must be a string")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'ts_code': self.ts_code,
            'trade_date': self.trade_date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'pre_close': self.pre_close,
            'change': self.change,
            'pct_chg': self.pct_chg,
            'vol': self.vol,
            'amount': self.amount,
            'name': self.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockDailyData':
        """从字典创建实例"""
        return cls(**data)


@dataclass
class LimitUpStats:
    """
    涨停统计结果模型
    
    封装指定交易日的涨停股票统计结果，包括总数、市场分类、ST分类等信息。
    
    Attributes:
        trade_date: 交易日期 (格式: YYYYMMDD)
        total: 总涨停数量
        non_st: 非ST涨停数量
        shanghai: 上证涨停数量
        shenzhen: 深证涨停数量
        star: 科创板涨停数量
        beijing: 北证涨停数量
        st: ST涨停数量
        limit_up_stocks: 涨停股票代码列表
        market_breakdown: 按市场分类的涨停股票字典
        created_at: 创建时间 (ISO格式)
        updated_at: 更新时间 (ISO格式)
    """
    trade_date: str                           # 交易日期
    total: int                               # 总涨停数量
    non_st: int                              # 非ST涨停数量
    shanghai: int                            # 上证涨停数量
    shenzhen: int                            # 深证涨停数量
    star: int                                # 科创板涨停数量
    beijing: int                             # 北证涨停数量
    st: int                                  # ST涨停数量
    limit_up_stocks: List[str] = field(default_factory=list)  # 涨停股票代码列表
    market_breakdown: Dict[str, List[str]] = field(default_factory=dict)  # 按市场分类的涨停股票
    created_at: Optional[str] = None         # 创建时间
    updated_at: Optional[str] = None         # 更新时间
    
    def __post_init__(self):
        """数据验证和初始化"""
        self.validate()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def validate(self) -> bool:
        """验证统计数据的一致性"""
        # 验证交易日期格式
        if not self.trade_date or not re.match(r'^\d{8}$', self.trade_date):
            raise ValueError(f"Invalid trade date format: {self.trade_date}")
        
        # 验证数量字段为非负整数
        count_fields = ['total', 'non_st', 'shanghai', 'shenzhen', 'star', 'beijing', 'st']
        for field_name in count_fields:
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Invalid {field_name}: {value}")
        
        # 验证数据一致性：总数 = 各市场之和
        market_sum = self.shanghai + self.shenzhen + self.star + self.beijing
        if self.total != market_sum:
            raise ValueError(f"Total count ({self.total}) doesn't match market sum ({market_sum})")
        
        # 验证数据一致性：总数 = ST + 非ST
        if self.total != self.st + self.non_st:
            raise ValueError(f"Total count ({self.total}) doesn't match ST + non-ST ({self.st + self.non_st})")
        
        # 验证涨停股票列表长度与总数一致
        if len(self.limit_up_stocks) != self.total:
            raise ValueError(f"Limit up stocks count ({len(self.limit_up_stocks)}) doesn't match total ({self.total})")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'trade_date': self.trade_date,
            'total': self.total,
            'non_st': self.non_st,
            'shanghai': self.shanghai,
            'shenzhen': self.shenzhen,
            'star': self.star,
            'beijing': self.beijing,
            'st': self.st,
            'limit_up_stocks': self.limit_up_stocks,
            'market_breakdown': self.market_breakdown,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LimitUpStats':
        """从字典创建实例"""
        return cls(**data)
    
    def get_summary(self) -> Dict[str, int]:
        """获取简化的统计摘要"""
        return {
            'total': self.total,
            'non_st': self.non_st,
            'shanghai': self.shanghai,
            'shenzhen': self.shenzhen,
            'star': self.star,
            'beijing': self.beijing,
            'st': self.st
        }


@dataclass
class LimitUpStatsRequest(DataRequest):
    """
    涨停统计请求模型
    
    用于请求指定交易日的涨停股票统计数据。SDK会实时从数据源获取数据并进行统计分析。
    
    Attributes:
        trade_date: 交易日期 (必填，格式: YYYYMMDD 或 YYYY-MM-DD)
        include_st: 是否包含ST股票 (默认: True)
        market_filter: 市场过滤器，可选值: ['shanghai', 'shenzhen', 'star', 'beijing']
        force_refresh: 是否强制从外部数据源刷新数据 (默认: False)
        timeout: 请求超时时间，单位秒 (默认: 30)
    """
    # 重写父类字段以确保正确的字段顺序
    data_type: str = "limit_up_stats"        # 数据类型
    ts_code: Optional[str] = None            # 股票代码（继承自父类）
    start_date: Optional[str] = None         # 开始日期（继承自父类）
    end_date: Optional[str] = None           # 结束日期（继承自父类）
    freq: Optional[str] = None               # 频率（继承自父类）
    fields: Optional[List[str]] = None       # 字段（继承自父类）
    extra_params: Dict[str, Any] = field(default_factory=dict)  # 额外参数（继承自父类）
    
    # 涨停统计特有字段
    trade_date: str = ""                     # 交易日期 (YYYYMMDD 或 YYYY-MM-DD)
    include_st: bool = True                  # 是否包含ST股票
    market_filter: Optional[List[str]] = None  # 市场过滤器 ['shanghai', 'shenzhen', 'star', 'beijing']
    force_refresh: bool = False              # 是否强制从外部数据源刷新
    timeout: int = 30                        # 请求超时时间（秒）
    
    def __post_init__(self):
        """数据验证和标准化"""
        # 设置父类的data_type
        self.data_type = "limit_up_stats"
        self.normalize()
        self.validate()
    
    def validate(self) -> bool:
        """验证请求参数"""
        # 验证交易日期格式并标准化
        if not self.trade_date or self.trade_date == "":
            raise ValueError("Trade date is required")
        
        # 支持 YYYY-MM-DD 和 YYYYMMDD 格式
        if re.match(r'^\d{4}-\d{2}-\d{2}$', self.trade_date):
            # 转换为 YYYYMMDD 格式
            self.trade_date = self.trade_date.replace('-', '')
        elif not re.match(r'^\d{8}$', self.trade_date):
            raise ValueError(f"Invalid trade date format: {self.trade_date}. Expected YYYYMMDD or YYYY-MM-DD")
        
        # 验证日期有效性
        try:
            datetime.strptime(self.trade_date, '%Y%m%d')
        except ValueError:
            raise ValueError(f"Invalid date: {self.trade_date}")
        
        # 验证日期不能是未来日期
        today = datetime.now().strftime('%Y%m%d')
        if self.trade_date > today:
            raise ValueError(f"Trade date cannot be in the future: {self.trade_date}")
        
        # 验证市场过滤器
        if self.market_filter is not None:
            valid_markets = set(MARKET_CLASSIFICATION_RULES.keys())
            invalid_markets = set(self.market_filter) - valid_markets
            if invalid_markets:
                raise ValueError(f"Invalid market filters: {invalid_markets}. Valid options: {valid_markets}")
        
        # 验证超时时间
        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ValueError(f"Timeout must be a positive integer: {self.timeout}")
        
        return True
    
    def normalize(self):
        """标准化请求参数"""
        # 确保市场过滤器是列表
        if self.market_filter is not None and not isinstance(self.market_filter, list):
            # 检查是否是字符串，如果是字符串且是有效市场名称，转换为列表
            if isinstance(self.market_filter, str):
                self.market_filter = [self.market_filter]
            else:
                self.market_filter = [self.market_filter]
        
        # 去重市场过滤器，保持原始顺序
        if self.market_filter:
            seen = set()
            deduplicated = []
            for item in self.market_filter:
                if item not in seen:
                    seen.add(item)
                    deduplicated.append(item)
            self.market_filter = deduplicated
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'data_type': self.data_type,
            'ts_code': self.ts_code,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'freq': self.freq,
            'fields': self.fields,
            'extra_params': self.extra_params,
            'trade_date': self.trade_date,
            'include_st': self.include_st,
            'market_filter': self.market_filter,
            'force_refresh': self.force_refresh,
            'timeout': self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LimitUpStatsRequest':
        """从字典创建实例"""
        return cls(**data)
    
    def get_formatted_date(self) -> str:
        """获取格式化的日期字符串 (YYYY-MM-DD)"""
        return f"{self.trade_date[:4]}-{self.trade_date[4:6]}-{self.trade_date[6:8]}"
    
    def is_market_included(self, market: str) -> bool:
        """检查指定市场是否包含在过滤器中"""
        if self.market_filter is None:
            return True
        return market in self.market_filter


# ==================== 财务报告相关数据模型 ====================

@dataclass
class FinancialReport:
    """
    财务报告数据模型
    
    封装上市公司的财务报告数据，包括利润表、资产负债表和现金流量表的关键指标。
    
    Attributes:
        ts_code: 股票代码 (格式: "000001.SZ")
        report_date: 报告期 (格式: YYYYMMDD)
        report_type: 报告类型 (Q1-一季报, Q2-半年报, Q3-三季报, A-年报)
        total_revenue: 营业总收入 (单位: 万元)
        net_profit: 净利润 (单位: 万元)
        total_assets: 总资产 (单位: 万元)
        total_liabilities: 总负债 (单位: 万元)
        shareholders_equity: 股东权益 (单位: 万元)
        operating_cash_flow: 经营活动现金流 (单位: 万元)
        eps: 每股收益 (单位: 元)
        roe: 净资产收益率 (单位: %)
        created_at: 创建时间 (ISO格式)
        updated_at: 更新时间 (ISO格式)
    """
    ts_code: str              # 股票代码
    report_date: str          # 报告期 (YYYYMMDD)
    report_type: str          # 报告类型 (Q1, Q2, Q3, A)
    total_revenue: float      # 营业总收入 (万元)
    net_profit: float         # 净利润 (万元)
    total_assets: float       # 总资产 (万元)
    total_liabilities: float  # 总负债 (万元)
    shareholders_equity: float # 股东权益 (万元)
    operating_cash_flow: float # 经营活动现金流 (万元)
    eps: float               # 每股收益 (元)
    roe: float               # 净资产收益率 (%)
    created_at: Optional[str] = None  # 创建时间
    updated_at: Optional[str] = None  # 更新时间
    
    def __post_init__(self):
        """数据验证和初始化"""
        self.validate()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def validate(self) -> bool:
        """验证财务报告数据"""
        from quickstock.core.errors import ValidationError
        
        # 验证股票代码格式
        if not self.ts_code or not re.match(r'^\d{6}\.(SH|SZ|BJ)$', self.ts_code):
            raise ValidationError(f"Invalid stock code format: {self.ts_code}")
        
        # 验证报告日期格式
        if not self.report_date or not re.match(r'^\d{8}$', self.report_date):
            raise ValidationError(f"Invalid report date format: {self.report_date}")
        
        # 验证日期有效性
        try:
            datetime.strptime(self.report_date, '%Y%m%d')
        except ValueError:
            raise ValidationError(f"Invalid report date: {self.report_date}")
        
        # 验证报告类型
        valid_types = ['Q1', 'Q2', 'Q3', 'A']
        if self.report_type not in valid_types:
            raise ValidationError(f"Invalid report type: {self.report_type}. Valid types: {valid_types}")
        
        # 验证财务数据类型
        financial_fields = [
            'total_revenue', 'net_profit', 'total_assets', 
            'total_liabilities', 'shareholders_equity', 'operating_cash_flow', 'eps', 'roe'
        ]
        for field_name in financial_fields:
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Invalid {field_name}: must be numeric, got {type(value)}")
        
        # 验证财务数据逻辑关系
        if self.total_assets < 0:
            raise ValidationError("Total assets cannot be negative")
        
        if self.total_liabilities < 0:
            raise ValidationError("Total liabilities cannot be negative")
        
        # 资产负债表平衡验证（允许一定误差）
        if self.total_assets > 0 and self.shareholders_equity > 0:
            calculated_equity = self.total_assets - self.total_liabilities
            equity_diff = abs(calculated_equity - self.shareholders_equity)
            # 允许1%的误差
            if equity_diff > self.total_assets * 0.01:
                raise ValidationError(
                    f"Balance sheet validation failed: "
                    f"Assets({self.total_assets}) - Liabilities({self.total_liabilities}) "
                    f"!= Equity({self.shareholders_equity})"
                )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'ts_code': self.ts_code,
            'report_date': self.report_date,
            'report_type': self.report_type,
            'total_revenue': self.total_revenue,
            'net_profit': self.net_profit,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'shareholders_equity': self.shareholders_equity,
            'operating_cash_flow': self.operating_cash_flow,
            'eps': self.eps,
            'roe': self.roe,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinancialReport':
        """从字典创建实例"""
        return cls(**data)
    
    def get_formatted_date(self) -> str:
        """获取格式化的报告日期 (YYYY-MM-DD)"""
        return f"{self.report_date[:4]}-{self.report_date[4:6]}-{self.report_date[6:8]}"
    
    def get_profit_margin(self) -> float:
        """计算净利润率"""
        if self.total_revenue == 0:
            return 0.0
        return (self.net_profit / self.total_revenue) * 100
    
    def get_debt_ratio(self) -> float:
        """计算资产负债率"""
        if self.total_assets == 0:
            return 0.0
        return (self.total_liabilities / self.total_assets) * 100


@dataclass
class EarningsForecast:
    """
    业绩预告数据模型
    
    封装上市公司发布的业绩预告信息，包括预告类型、利润范围和增长率等。
    
    Attributes:
        ts_code: 股票代码 (格式: "000001.SZ")
        forecast_date: 预告日期 (格式: YYYYMMDD)
        forecast_period: 预告期间 (格式: YYYYMMDD)
        forecast_type: 预告类型 (如: 预增、预减、扭亏、首亏等)
        net_profit_min: 净利润下限 (单位: 万元)
        net_profit_max: 净利润上限 (单位: 万元)
        growth_rate_min: 增长率下限 (单位: %)
        growth_rate_max: 增长率上限 (单位: %)
        forecast_summary: 预告摘要
        created_at: 创建时间 (ISO格式)
        updated_at: 更新时间 (ISO格式)
    """
    ts_code: str             # 股票代码
    forecast_date: str       # 预告日期 (YYYYMMDD)
    forecast_period: str     # 预告期间 (YYYYMMDD)
    forecast_type: str       # 预告类型
    net_profit_min: float    # 净利润下限 (万元)
    net_profit_max: float    # 净利润上限 (万元)
    growth_rate_min: float   # 增长率下限 (%)
    growth_rate_max: float   # 增长率上限 (%)
    forecast_summary: str    # 预告摘要
    created_at: Optional[str] = None  # 创建时间
    updated_at: Optional[str] = None  # 更新时间
    
    def __post_init__(self):
        """数据验证和初始化"""
        self.validate()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def validate(self) -> bool:
        """验证业绩预告数据"""
        from quickstock.core.errors import ValidationError
        
        # 验证股票代码格式
        if not self.ts_code or not re.match(r'^\d{6}\.(SH|SZ|BJ)$', self.ts_code):
            raise ValidationError(f"Invalid stock code format: {self.ts_code}")
        
        # 验证预告日期格式
        if not self.forecast_date or not re.match(r'^\d{8}$', self.forecast_date):
            raise ValidationError(f"Invalid forecast date format: {self.forecast_date}")
        
        # 验证预告期间格式
        if not self.forecast_period or not re.match(r'^\d{8}$', self.forecast_period):
            raise ValidationError(f"Invalid forecast period format: {self.forecast_period}")
        
        # 验证日期有效性
        try:
            datetime.strptime(self.forecast_date, '%Y%m%d')
            datetime.strptime(self.forecast_period, '%Y%m%d')
        except ValueError as e:
            raise ValidationError(f"Invalid date format: {e}")
        
        # 验证预告类型
        valid_types = ['预增', '预减', '扭亏', '首亏', '续亏', '续盈', '略增', '略减', '不确定']
        if self.forecast_type and self.forecast_type not in valid_types:
            raise ValidationError(f"Invalid forecast type: {self.forecast_type}. Valid types: {valid_types}")
        
        # 验证数值类型
        numeric_fields = ['net_profit_min', 'net_profit_max', 'growth_rate_min', 'growth_rate_max']
        for field_name in numeric_fields:
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Invalid {field_name}: must be numeric, got {type(value)}")
        
        # 验证数值逻辑关系
        if self.net_profit_min > self.net_profit_max:
            raise ValidationError("Net profit minimum cannot be greater than maximum")
        
        if self.growth_rate_min > self.growth_rate_max:
            raise ValidationError("Growth rate minimum cannot be greater than maximum")
        
        # 验证摘要
        if not isinstance(self.forecast_summary, str):
            raise ValidationError("Forecast summary must be a string")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'ts_code': self.ts_code,
            'forecast_date': self.forecast_date,
            'forecast_period': self.forecast_period,
            'forecast_type': self.forecast_type,
            'net_profit_min': self.net_profit_min,
            'net_profit_max': self.net_profit_max,
            'growth_rate_min': self.growth_rate_min,
            'growth_rate_max': self.growth_rate_max,
            'forecast_summary': self.forecast_summary,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EarningsForecast':
        """从字典创建实例"""
        return cls(**data)
    
    def get_formatted_forecast_date(self) -> str:
        """获取格式化的预告日期 (YYYY-MM-DD)"""
        return f"{self.forecast_date[:4]}-{self.forecast_date[4:6]}-{self.forecast_date[6:8]}"
    
    def get_formatted_period(self) -> str:
        """获取格式化的预告期间 (YYYY-MM-DD)"""
        return f"{self.forecast_period[:4]}-{self.forecast_period[4:6]}-{self.forecast_period[6:8]}"
    
    def get_profit_range(self) -> str:
        """获取利润范围描述"""
        if self.net_profit_min == self.net_profit_max:
            return f"{self.net_profit_min}万元"
        return f"{self.net_profit_min}万元 ~ {self.net_profit_max}万元"
    
    def get_growth_range(self) -> str:
        """获取增长率范围描述"""
        if self.growth_rate_min == self.growth_rate_max:
            return f"{self.growth_rate_min}%"
        return f"{self.growth_rate_min}% ~ {self.growth_rate_max}%"


@dataclass
class FlashReport:
    """
    业绩快报数据模型
    
    封装上市公司发布的业绩快报信息，在正式财报前提供业绩速报。
    
    Attributes:
        ts_code: 股票代码 (格式: "000001.SZ")
        report_date: 报告日期 (格式: YYYYMMDD)
        publish_date: 发布日期 (格式: YYYYMMDD)
        report_period: 报告期间 (格式: YYYYMMDD)
        total_revenue: 营业收入 (单位: 万元)
        net_profit: 净利润 (单位: 万元)
        revenue_growth: 收入增长率 (单位: %)
        profit_growth: 利润增长率 (单位: %)
        eps: 每股收益 (单位: 元)
        report_summary: 快报摘要
        created_at: 创建时间 (ISO格式)
        updated_at: 更新时间 (ISO格式)
    """
    ts_code: str             # 股票代码
    report_date: str         # 报告日期 (YYYYMMDD)
    publish_date: str        # 发布日期 (YYYYMMDD)
    report_period: str       # 报告期间 (YYYYMMDD)
    total_revenue: float     # 营业收入 (万元)
    net_profit: float        # 净利润 (万元)
    revenue_growth: float    # 收入增长率 (%)
    profit_growth: float     # 利润增长率 (%)
    eps: float              # 每股收益 (元)
    report_summary: str      # 快报摘要
    created_at: Optional[str] = None  # 创建时间
    updated_at: Optional[str] = None  # 更新时间
    
    def __post_init__(self):
        """数据验证和初始化"""
        self.validate()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def validate(self) -> bool:
        """验证业绩快报数据"""
        from quickstock.core.errors import ValidationError
        
        # 验证股票代码格式
        if not self.ts_code or not re.match(r'^\d{6}\.(SH|SZ|BJ)$', self.ts_code):
            raise ValidationError(f"Invalid stock code format: {self.ts_code}")
        
        # 验证日期格式
        date_fields = ['report_date', 'publish_date', 'report_period']
        for field_name in date_fields:
            date_value = getattr(self, field_name)
            if not date_value or not re.match(r'^\d{8}$', date_value):
                raise ValidationError(f"Invalid {field_name} format: {date_value}")
            
            # 验证日期有效性
            try:
                datetime.strptime(date_value, '%Y%m%d')
            except ValueError:
                raise ValidationError(f"Invalid {field_name}: {date_value}")
        
        # 验证数值类型
        numeric_fields = ['total_revenue', 'net_profit', 'revenue_growth', 'profit_growth', 'eps']
        for field_name in numeric_fields:
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Invalid {field_name}: must be numeric, got {type(value)}")
        
        # 验证日期逻辑关系
        if self.publish_date < self.report_date:
            raise ValidationError("Publish date cannot be earlier than report date")
        
        # 验证摘要
        if not isinstance(self.report_summary, str):
            raise ValidationError("Report summary must be a string")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'ts_code': self.ts_code,
            'report_date': self.report_date,
            'publish_date': self.publish_date,
            'report_period': self.report_period,
            'total_revenue': self.total_revenue,
            'net_profit': self.net_profit,
            'revenue_growth': self.revenue_growth,
            'profit_growth': self.profit_growth,
            'eps': self.eps,
            'report_summary': self.report_summary,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlashReport':
        """从字典创建实例"""
        return cls(**data)
    
    def get_formatted_report_date(self) -> str:
        """获取格式化的报告日期 (YYYY-MM-DD)"""
        return f"{self.report_date[:4]}-{self.report_date[4:6]}-{self.report_date[6:8]}"
    
    def get_formatted_publish_date(self) -> str:
        """获取格式化的发布日期 (YYYY-MM-DD)"""
        return f"{self.publish_date[:4]}-{self.publish_date[4:6]}-{self.publish_date[6:8]}"
    
    def get_formatted_period(self) -> str:
        """获取格式化的报告期间 (YYYY-MM-DD)"""
        return f"{self.report_period[:4]}-{self.report_period[4:6]}-{self.report_period[6:8]}"
    
    def get_profit_margin(self) -> float:
        """计算净利润率"""
        if self.total_revenue == 0:
            return 0.0
        return (self.net_profit / self.total_revenue) * 100


# 财务数据请求模型

@dataclass
class FinancialReportsRequest(DataRequest):
    """
    财务报告请求模型
    
    用于请求上市公司的财务报告数据。SDK会实时从数据源获取数据。
    
    Attributes:
        report_type: 报告类型 (可选，Q1-一季报, Q2-半年报, Q3-三季报, A-年报)
        fields: 需要返回的字段列表 (可选)
    """
    data_type: str = "financial_reports"
    report_type: Optional[str] = None  # Q1, Q2, Q3, A
    fields: Optional[List[str]] = None
    
    def __post_init__(self):
        """数据验证和标准化"""
        self.data_type = "financial_reports"
        self.validate()
    
    def validate(self) -> bool:
        """验证请求参数"""
        # 调用父类验证
        super().validate()
        
        # 验证报告类型
        if self.report_type is not None:
            valid_types = ['Q1', 'Q2', 'Q3', 'A']
            if self.report_type not in valid_types:
                from quickstock.core.errors import ValidationError
                raise ValidationError(f"Invalid report type: {self.report_type}. Valid types: {valid_types}")
        
        return True


@dataclass
class EarningsForecastRequest(DataRequest):
    """
    业绩预告请求模型
    
    用于请求上市公司的业绩预告数据。SDK会实时从数据源获取数据。
    
    Attributes:
        forecast_type: 预告类型 (可选，如: 预增、预减、扭亏、首亏等)
    """
    data_type: str = "earnings_forecast"
    forecast_type: Optional[str] = None
    
    def __post_init__(self):
        """数据验证和标准化"""
        self.data_type = "earnings_forecast"
        self.validate()
    
    def validate(self) -> bool:
        """验证请求参数"""
        # 调用父类验证
        super().validate()
        
        # 验证预告类型
        if self.forecast_type is not None:
            valid_types = ['预增', '预减', '扭亏', '首亏', '续亏', '续盈', '略增', '略减', '不确定']
            if self.forecast_type not in valid_types:
                from quickstock.core.errors import ValidationError
                raise ValidationError(f"Invalid forecast type: {self.forecast_type}. Valid types: {valid_types}")
        
        return True


@dataclass
class FlashReportsRequest(DataRequest):
    """
    业绩快报请求模型
    
    用于请求上市公司的业绩快报数据。SDK会实时从数据源获取数据。
    
    Attributes:
        sort_by: 排序字段 (默认: publish_date，可选: report_date, report_period)
    """
    data_type: str = "flash_reports"
    sort_by: str = "publish_date"
    
    def __post_init__(self):
        """数据验证和标准化"""
        self.data_type = "flash_reports"
        self.validate()
    
    def validate(self) -> bool:
        """验证请求参数"""
        # 调用父类验证
        super().validate()
        
        # 验证排序字段
        valid_sort_fields = ['publish_date', 'report_date', 'report_period']
        if self.sort_by not in valid_sort_fields:
            from quickstock.core.errors import ValidationError
            raise ValidationError(f"Invalid sort field: {self.sort_by}. Valid fields: {valid_sort_fields}")
        
        return True

# ==================== 涨跌分布统计相关数据模型 ====================

@dataclass
class DistributionRange:
    """
    分布区间定义模型
    
    定义涨跌幅分布统计的区间范围，用于将股票按涨跌幅分类统计。
    
    Attributes:
        name: 区间名称 (如: "0-3%")
        min_value: 最小值 (包含)
        max_value: 最大值 (不包含)
        is_positive: 是否为正区间 (True表示涨幅区间，False表示跌幅区间)
        display_name: 显示名称
    """
    name: str                    # 区间名称 (如: "0-3%")
    min_value: float            # 最小值 (包含)
    max_value: float            # 最大值 (不包含)
    is_positive: bool           # 是否为正区间
    display_name: str           # 显示名称
    
    def __post_init__(self):
        """数据验证和初始化"""
        self.validate()
    
    def validate(self) -> bool:
        """验证区间定义的有效性"""
        from quickstock.core.errors import ValidationError
        
        # 验证区间名称
        if not self.name or not isinstance(self.name, str):
            raise ValidationError("Range name is required and must be a string")
        
        # 验证显示名称
        if not self.display_name or not isinstance(self.display_name, str):
            raise ValidationError("Display name is required and must be a string")
        
        # 验证数值范围
        if not isinstance(self.min_value, (int, float)) or not isinstance(self.max_value, (int, float)):
            raise ValidationError("Min and max values must be numeric")
        
        # 验证区间逻辑
        if self.min_value >= self.max_value and self.max_value != float('inf'):
            raise ValidationError(f"Min value ({self.min_value}) must be less than max value ({self.max_value})")
        
        # 验证正负区间一致性
        if self.is_positive and (self.min_value < 0 or (self.max_value < 0 and self.max_value != float('inf'))):
            raise ValidationError("Positive range cannot have negative values")
        
        if not self.is_positive and (self.min_value > 0 or self.max_value > 0):
            raise ValidationError("Negative range cannot have positive values")
        
        return True
    
    def contains(self, value: float) -> bool:
        """检查值是否在区间内"""
        if self.max_value == float('inf'):
            return value >= self.min_value
        elif self.min_value == float('-inf'):
            return value < self.max_value
        return self.min_value <= value < self.max_value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'is_positive': self.is_positive,
            'display_name': self.display_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DistributionRange':
        """从字典创建实例"""
        return cls(**data)
    
    @classmethod
    def create_default_ranges(cls) -> List['DistributionRange']:
        """创建默认的涨跌幅区间"""
        ranges = []
        
        # 正涨幅区间
        positive_ranges = [
            ("0-3%", 0.0, 3.0, "0-3%"),
            ("3-5%", 3.0, 5.0, "3-5%"),
            ("5-7%", 5.0, 7.0, "5-7%"),
            ("7-10%", 7.0, 10.0, "7-10%"),
            (">=10%", 10.0, float('inf'), ">=10%")
        ]
        
        for name, min_val, max_val, display in positive_ranges:
            ranges.append(cls(
                name=name,
                min_value=min_val,
                max_value=max_val,
                is_positive=True,
                display_name=display
            ))
        
        # 负涨幅区间
        negative_ranges = [
            ("0--3%", -3.0, 0.0, "0到-3%"),
            ("-3--5%", -5.0, -3.0, "-3到-5%"),
            ("-5--7%", -7.0, -5.0, "-5到-7%"),
            ("-7--10%", -10.0, -7.0, "-7到-10%"),
            ("<=-10%", float('-inf'), -10.0, "<=-10%")
        ]
        
        for name, min_val, max_val, display in negative_ranges:
            ranges.append(cls(
                name=name,
                min_value=min_val,
                max_value=max_val,
                is_positive=False,
                display_name=display
            ))
        
        return ranges


@dataclass
class PriceDistributionStats:
    """
    涨跌分布统计结果模型
    
    封装指定交易日的股票涨跌幅分布统计结果，包括各区间的股票数量和占比。
    
    Attributes:
        trade_date: 交易日期 (格式: YYYYMMDD)
        total_stocks: 总股票数
        positive_ranges: 正涨幅区间统计 (区间名称 -> 股票数量)
        positive_percentages: 正涨幅区间占比 (区间名称 -> 百分比)
        negative_ranges: 负涨幅区间统计 (区间名称 -> 股票数量)
        negative_percentages: 负涨幅区间占比 (区间名称 -> 百分比)
        market_breakdown: 按市场分类的分布统计
        created_at: 创建时间 (ISO格式)
        processing_time: 处理耗时 (单位: 秒)
        data_quality_score: 数据质量分数 (0-1之间)
    """
    trade_date: str                          # 交易日期
    total_stocks: int                        # 总股票数
    
    # 涨幅分布
    positive_ranges: Dict[str, int]          # 正涨幅区间统计
    positive_percentages: Dict[str, float]   # 正涨幅区间占比
    
    # 跌幅分布  
    negative_ranges: Dict[str, int]          # 负涨幅区间统计
    negative_percentages: Dict[str, float]   # 负涨幅区间占比
    
    # 市场板块分布
    market_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # 按市场分类的分布
    
    # 元数据
    created_at: Optional[str] = None
    processing_time: float = 0.0
    data_quality_score: float = 1.0
    
    def __post_init__(self):
        """数据验证和初始化"""
        self.validate()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def validate(self) -> bool:
        """验证统计数据的一致性"""
        from quickstock.core.errors import ValidationError
        
        # 验证交易日期格式
        if not self.trade_date or not re.match(r'^\d{8}$', self.trade_date):
            raise ValidationError(f"Invalid trade date format: {self.trade_date}")
        
        # 验证总股票数
        if not isinstance(self.total_stocks, int) or self.total_stocks < 0:
            raise ValidationError(f"Invalid total stocks count: {self.total_stocks}")
        
        # 验证正涨幅分布数据
        if not isinstance(self.positive_ranges, dict):
            raise ValidationError("Positive ranges must be a dictionary")
        
        if not isinstance(self.positive_percentages, dict):
            raise ValidationError("Positive percentages must be a dictionary")
        
        # 验证负涨幅分布数据
        if not isinstance(self.negative_ranges, dict):
            raise ValidationError("Negative ranges must be a dictionary")
        
        if not isinstance(self.negative_percentages, dict):
            raise ValidationError("Negative percentages must be a dictionary")
        
        # 验证区间数据一致性
        positive_total = sum(self.positive_ranges.values())
        negative_total = sum(self.negative_ranges.values())
        
        if positive_total + negative_total != self.total_stocks:
            raise ValidationError(f"Range totals ({positive_total + negative_total}) don't match total stocks ({self.total_stocks})")
        
        # 验证百分比数据
        for range_name, count in self.positive_ranges.items():
            if range_name not in self.positive_percentages:
                raise ValidationError(f"Missing percentage for positive range: {range_name}")
            
            expected_pct = (count / self.total_stocks * 100) if self.total_stocks > 0 else 0.0
            actual_pct = self.positive_percentages[range_name]
            
            if abs(expected_pct - actual_pct) > 0.01:  # 允许0.01%的误差
                raise ValidationError(f"Percentage mismatch for {range_name}: expected {expected_pct:.2f}%, got {actual_pct:.2f}%")
        
        for range_name, count in self.negative_ranges.items():
            if range_name not in self.negative_percentages:
                raise ValidationError(f"Missing percentage for negative range: {range_name}")
            
            expected_pct = (count / self.total_stocks * 100) if self.total_stocks > 0 else 0.0
            actual_pct = self.negative_percentages[range_name]
            
            if abs(expected_pct - actual_pct) > 0.01:  # 允许0.01%的误差
                raise ValidationError(f"Percentage mismatch for {range_name}: expected {expected_pct:.2f}%, got {actual_pct:.2f}%")
        
        # 验证处理时间和数据质量分数
        if not isinstance(self.processing_time, (int, float)) or self.processing_time < 0:
            raise ValidationError(f"Invalid processing time: {self.processing_time}")
        
        if not isinstance(self.data_quality_score, (int, float)) or not (0 <= self.data_quality_score <= 1):
            raise ValidationError(f"Data quality score must be between 0 and 1: {self.data_quality_score}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'trade_date': self.trade_date,
            'total_stocks': self.total_stocks,
            'positive_ranges': self.positive_ranges,
            'positive_percentages': self.positive_percentages,
            'negative_ranges': self.negative_ranges,
            'negative_percentages': self.negative_percentages,
            'market_breakdown': self.market_breakdown,
            'created_at': self.created_at,
            'processing_time': self.processing_time,
            'data_quality_score': self.data_quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceDistributionStats':
        """从字典创建实例"""
        return cls(**data)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        positive_total = sum(self.positive_ranges.values())
        negative_total = sum(self.negative_ranges.values())
        
        return {
            'trade_date': self.trade_date,
            'total_stocks': self.total_stocks,
            'positive_stocks': positive_total,
            'negative_stocks': negative_total,
            'positive_percentage': (positive_total / self.total_stocks * 100) if self.total_stocks > 0 else 0.0,
            'negative_percentage': (negative_total / self.total_stocks * 100) if self.total_stocks > 0 else 0.0,
            'processing_time': self.processing_time,
            'data_quality_score': self.data_quality_score
        }
    
    def get_market_summary(self, market: str) -> Optional[Dict[str, Any]]:
        """获取指定市场的统计摘要"""
        if market not in self.market_breakdown:
            return None
        
        market_data = self.market_breakdown[market]
        return {
            'market': market,
            'total_stocks': market_data.get('total_stocks', 0),
            'positive_ranges': market_data.get('positive_ranges', {}),
            'negative_ranges': market_data.get('negative_ranges', {}),
            'positive_percentages': market_data.get('positive_percentages', {}),
            'negative_percentages': market_data.get('negative_percentages', {})
        }


@dataclass
class PriceDistributionRequest(DataRequest):
    """
    涨跌分布统计请求模型
    
    用于请求指定交易日的股票涨跌幅分布统计数据。SDK会实时从数据源获取数据并进行统计分析。
    
    Attributes:
        trade_date: 交易日期 (必填，格式: YYYYMMDD 或 YYYY-MM-DD)
        include_st: 是否包含ST股票 (默认: True)
        market_filter: 市场过滤器，可选值: ['shanghai', 'shenzhen', 'star', 'beijing']
        distribution_ranges: 自定义分布区间 (可选，默认使用标准区间)
        force_refresh: 是否强制从外部数据源刷新数据 (默认: False)
        timeout: 请求超时时间，单位秒 (默认: 30)
    """
    # 重写父类字段以确保正确的字段顺序
    data_type: str = "price_distribution_stats"  # 数据类型
    ts_code: Optional[str] = None            # 股票代码（继承自父类）
    start_date: Optional[str] = None         # 开始日期（继承自父类）
    end_date: Optional[str] = None           # 结束日期（继承自父类）
    freq: Optional[str] = None               # 频率（继承自父类）
    fields: Optional[List[str]] = None       # 字段（继承自父类）
    extra_params: Dict[str, Any] = field(default_factory=dict)  # 额外参数（继承自父类）
    
    # 涨跌分布统计特有字段
    trade_date: str = ""                     # 交易日期 (YYYYMMDD 或 YYYY-MM-DD)
    include_st: bool = True                  # 是否包含ST股票
    market_filter: Optional[List[str]] = None # 市场过滤器 ['shanghai', 'shenzhen', 'star', 'beijing']
    distribution_ranges: Optional[List[DistributionRange]] = None  # 自定义区间
    force_refresh: bool = False              # 是否强制刷新
    timeout: int = 30                        # 请求超时时间（秒）
    
    def __post_init__(self):
        """数据验证和标准化"""
        # 设置父类的data_type
        self.data_type = "price_distribution_stats"
        self.normalize()
        self.validate()
    
    def validate(self) -> bool:
        """验证请求参数"""
        from quickstock.core.errors import ValidationError
        
        # 验证交易日期格式并标准化
        if not self.trade_date or self.trade_date == "":
            raise ValidationError("Trade date is required")
        
        # 支持 YYYY-MM-DD 和 YYYYMMDD 格式
        if re.match(r'^\d{4}-\d{2}-\d{2}$', self.trade_date):
            # 转换为 YYYYMMDD 格式
            self.trade_date = self.trade_date.replace('-', '')
        elif not re.match(r'^\d{8}$', self.trade_date):
            raise ValidationError(f"Invalid trade date format: {self.trade_date}. Expected YYYYMMDD or YYYY-MM-DD")
        
        # 验证日期有效性
        try:
            datetime.strptime(self.trade_date, '%Y%m%d')
        except ValueError:
            raise ValidationError(f"Invalid date: {self.trade_date}")
        
        # 验证日期不能是未来日期
        today = datetime.now().strftime('%Y%m%d')
        if self.trade_date > today:
            raise ValidationError(f"Trade date cannot be in the future: {self.trade_date}")
        
        # 验证市场过滤器
        if self.market_filter is not None:
            valid_markets = set(MARKET_CLASSIFICATION_RULES.keys())
            invalid_markets = set(self.market_filter) - valid_markets
            if invalid_markets:
                raise ValidationError(f"Invalid market filters: {invalid_markets}. Valid options: {valid_markets}")
        
        # 验证自定义区间
        if self.distribution_ranges is not None:
            if not isinstance(self.distribution_ranges, list):
                raise ValidationError("Distribution ranges must be a list")
            
            for i, range_obj in enumerate(self.distribution_ranges):
                if not isinstance(range_obj, DistributionRange):
                    raise ValidationError(f"Range at index {i} must be a DistributionRange instance")
                
                # 验证区间本身
                range_obj.validate()
        
        # 验证超时时间
        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ValidationError(f"Timeout must be a positive integer: {self.timeout}")
        
        return True
    
    def normalize(self):
        """标准化请求参数"""
        # 确保市场过滤器是列表
        if self.market_filter is not None and not isinstance(self.market_filter, list):
            self.market_filter = [self.market_filter]
        
        # 去重市场过滤器（保持顺序）
        if self.market_filter:
            seen = set()
            self.market_filter = [x for x in self.market_filter if not (x in seen or seen.add(x))]
        
        # 如果没有提供自定义区间，使用默认区间
        if self.distribution_ranges is None:
            self.distribution_ranges = DistributionRange.create_default_ranges()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'data_type': self.data_type,
            'ts_code': self.ts_code,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'freq': self.freq,
            'fields': self.fields,
            'extra_params': self.extra_params,
            'trade_date': self.trade_date,
            'include_st': self.include_st,
            'market_filter': self.market_filter,
            'distribution_ranges': [r.to_dict() for r in self.distribution_ranges] if self.distribution_ranges else None,
            'force_refresh': self.force_refresh,
            'timeout': self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceDistributionRequest':
        """从字典创建实例"""
        # 处理分布区间
        if 'distribution_ranges' in data and data['distribution_ranges'] is not None:
            data['distribution_ranges'] = [
                DistributionRange.from_dict(r) for r in data['distribution_ranges']
            ]
        
        return cls(**data)
    
    def get_formatted_date(self) -> str:
        """获取格式化的日期字符串 (YYYY-MM-DD)"""
        return f"{self.trade_date[:4]}-{self.trade_date[4:6]}-{self.trade_date[6:8]}"
    
    def is_market_included(self, market: str) -> bool:
        """检查指定市场是否包含在过滤器中"""
        if self.market_filter is None:
            return True
        return market in self.market_filter
    
    def get_positive_ranges(self) -> List[DistributionRange]:
        """获取正涨幅区间"""
        if not self.distribution_ranges:
            return []
        return [r for r in self.distribution_ranges if r.is_positive]
    
    def get_negative_ranges(self) -> List[DistributionRange]:
        """获取负涨幅区间"""
        if not self.distribution_ranges:
            return []
        return [r for r in self.distribution_ranges if not r.is_positive]
    
    def find_range_for_value(self, value: float) -> Optional[DistributionRange]:
        """为给定值找到对应的区间"""
        if not self.distribution_ranges:
            return None
        
        for range_obj in self.distribution_ranges:
            if range_obj.contains(value):
                return range_obj
        
        return None