"""
涨停统计服务

提供涨停股票统计分析的核心业务逻辑
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd

from ..models import (
    DataRequest, LimitUpStatsRequest, LimitUpStats, StockDailyData,
    MARKET_CLASSIFICATION_RULES
)
from ..core.data_manager import DataManager
from ..core.errors import (
    ValidationError, DataSourceError, LimitUpStatsError,
    InvalidTradeDateError, InsufficientDataError, 
    StockClassificationError, LimitUpDetectionError
)
from ..utils.stock_classifier import StockCodeClassifier, ClassificationResult
from ..utils.limit_up_detector import LimitUpDetector, LimitUpDetectionResult
from ..utils.price_utils import PriceUtils
from ..utils.limit_up_validators import (
    TradeDateValidator, DataValidator, FallbackManager, ValidationUtils
)
from ..utils.performance_optimizations import PerformanceOptimizer, PerformanceConfig


class InsufficientDataError(LimitUpStatsError):
    """数据不足异常"""
    
    def __init__(self, trade_date: str, missing_data_info: Dict[str, Any]):
        """
        初始化数据不足异常
        
        Args:
            trade_date: 交易日期
            missing_data_info: 缺失数据信息
        """
        message = f"交易日期 {trade_date} 的数据不足，无法进行涨停统计"
        super().__init__(message, details={
            'trade_date': trade_date,
            'missing_data_info': missing_data_info,
            'suggestions': [
                '检查交易日期是否为有效交易日',
                '确认数据源是否包含该日期的数据',
                '尝试使用其他数据源'
            ]
        })


class LimitUpStatsService:
    """
    涨停统计服务
    
    提供涨停股票统计分析的核心业务逻辑，包括：
    - 实时获取指定日期的股票数据
    - 检测涨停股票
    - 按市场分类统计
    - 生成统计报告
    """
    
    def __init__(self, data_manager: DataManager, logger: Optional[logging.Logger] = None):
        """
        初始化涨停统计服务
        
        Args:
            data_manager: 数据管理器
            logger: 日志记录器
        """
        self.data_manager = data_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化工具类
        self.stock_classifier = StockCodeClassifier(enable_fallback=True, logger=self.logger)
        self.limit_up_detector = LimitUpDetector(logger=self.logger)
        self.price_utils = PriceUtils()
        
        # 初始化验证和回退管理器
        self.date_validator = TradeDateValidator()
        self.data_validator = DataValidator()
        self.fallback_manager = FallbackManager()
        
        # 初始化性能优化器
        perf_config = PerformanceConfig(
            enable_vectorization=True,
            enable_parallel_processing=True,
            enable_memory_optimization=True,
            max_workers=4,
            batch_size=1000
        )
        self.performance_optimizer = PerformanceOptimizer(perf_config, logger)
        
        # 统计信息
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'last_request_time': None,
            'validation_errors': 0,
            'fallback_used': 0
        }
    
    async def get_daily_limit_up_stats(self, request: LimitUpStatsRequest) -> LimitUpStats:
        """
        获取指定日期的涨停统计
        
        Args:
            request: 涨停统计请求
            
        Returns:
            涨停统计结果
            
        Raises:
            LimitUpStatsError: 统计过程中的错误
            InsufficientDataError: 数据不足
        """
        start_time = datetime.now()
        self._stats['total_requests'] += 1
        self._stats['last_request_time'] = start_time
        
        try:
            self.logger.info(f"开始获取 {request.trade_date} 的涨停统计")
            
            # 1. 验证交易日期
            try:
                validated_date = self.date_validator.validate_trade_date(request.trade_date)
                request.trade_date = validated_date  # 使用标准化的日期
            except InvalidTradeDateError as e:
                self._stats['validation_errors'] += 1
                self.logger.error(f"交易日期验证失败: {e}")
                raise
            
            # 2. 验证请求参数
            request.validate()
            
            # 3. 获取股票日线数据
            stock_data = await self._fetch_daily_stock_data(request.trade_date)
            
            # 4. 验证数据完整性
            try:
                is_valid, validation_message = self.data_validator.validate_stock_data(
                    stock_data, request.trade_date, min_stocks=50
                )
                if not is_valid:
                    # 尝试使用回退机制处理数据不足
                    stock_data = self.fallback_manager.handle_insufficient_data(
                        request.trade_date, stock_data, min_required=50
                    )
                    self._stats['fallback_used'] += 1
            except InsufficientDataError as e:
                self.logger.error(f"数据验证失败: {e}")
                raise
            
            self.logger.info(f"获取到 {len(stock_data)} 只股票的数据")
            
            # 5. 检测涨停股票（带错误处理和回退）
            limit_up_stocks, failed_detections = await self._detect_limit_up_stocks_with_fallback(
                stock_data, request
            )
            
            self.logger.info(f"检测到 {len(limit_up_stocks)} 只涨停股票")
            if failed_detections:
                self.logger.warning(f"有 {len(failed_detections)} 只股票检测失败")
            
            # 6. 按市场分类股票（带错误处理和回退）
            classified_stocks, failed_classifications = await self._classify_stocks_with_fallback(
                limit_up_stocks, request
            )
            
            if failed_classifications:
                self.logger.warning(f"有 {len(failed_classifications)} 只股票分类失败")
            
            # 7. 聚合统计数据
            stats = self._aggregate_statistics(classified_stocks, request)
            
            # 8. 验证统计数据一致性
            if not ValidationUtils.validate_statistics_consistency(stats):
                self.logger.error("统计数据一致性验证失败")
                raise LimitUpStatsError("统计数据不一致", request)
            
            # 9. 创建统计结果
            result = LimitUpStats(
                trade_date=request.trade_date,
                total=stats['total'],
                non_st=stats['non_st'],
                shanghai=stats['shanghai'],
                shenzhen=stats['shenzhen'],
                star=stats['star'],
                beijing=stats['beijing'],
                st=stats['st'],
                limit_up_stocks=stats['limit_up_stocks'],
                market_breakdown=stats['market_breakdown']
            )
            
            # 10. 如果有失败的处理，创建部分结果
            if failed_detections or failed_classifications:
                all_failed = failed_detections + failed_classifications
                result = self.fallback_manager.create_partial_results(
                    request.trade_date, result.to_dict(), all_failed
                )
                # 转换回LimitUpStats对象
                result = LimitUpStats.from_dict(result)
            
            # 记录成功
            processing_time = (datetime.now() - start_time).total_seconds()
            self._stats['successful_requests'] += 1
            self._stats['total_processing_time'] += processing_time
            
            self.logger.info(f"涨停统计完成，处理时间: {processing_time:.2f}s，"
                           f"总计: {result.total}, 非ST: {result.non_st}")
            
            return result
            
        except Exception as e:
            # 记录失败
            self._stats['failed_requests'] += 1
            
            if isinstance(e, (LimitUpStatsError, InsufficientDataError)):
                raise
            else:
                # 包装其他异常
                self.logger.error(f"涨停统计失败: {e}")
                raise LimitUpStatsError(
                    f"涨停统计处理失败: {str(e)}", 
                    request, 
                    {'original_error': str(e), 'error_type': type(e).__name__}
                )
    
    async def _fetch_daily_stock_data(self, trade_date: str) -> pd.DataFrame:
        """
        获取指定日期的股票日线数据
        
        Args:
            trade_date: 交易日期 (YYYYMMDD格式)
            
        Returns:
            股票日线数据DataFrame
        """
        try:
            # 1. 先获取所有上市股票列表（只获取股票，不包括指数等）
            # 使用 stock_detail 并筛选 type='1'(股票) 和 status='1'(上市)
            stock_list = await self.data_manager.source_manager.providers['baostock'].get_stock_detail(
                type='1',  # 只获取股票
                status='1'  # 只获取上市股票
            )
            
            if stock_list.empty:
                self.logger.warning("未获取到上市股票列表")
                return pd.DataFrame()
            
            total_stocks = len(stock_list)
            self.logger.info(f"获取到 {total_stocks} 只上市股票，开始批量获取日线数据")
            
            # 2. 批量获取每只股票的日线数据
            # 为了提高效率，分批处理（每批100只股票）
            all_daily_data = []
            failed_stocks = []
            batch_size = 100
            
            for batch_start in range(0, total_stocks, batch_size):
                batch_end = min(batch_start + batch_size, total_stocks)
                batch_stocks = stock_list.iloc[batch_start:batch_end]
                
                self.logger.info(f"处理第 {batch_start//batch_size + 1} 批股票 ({batch_start+1}-{batch_end}/{total_stocks})")
                
                # 创建批量请求
                batch_requests = []
                for _, stock in batch_stocks.iterrows():
                    # stock_detail 返回的是 baostock 格式的 code (如 sz.000001)
                    # 需要转换为标准格式 (如 000001.SZ)
                    baostock_code = stock['code']
                    
                    # 转换为标准格式
                    if baostock_code.startswith('sz.'):
                        ts_code = baostock_code[3:] + '.SZ'
                    elif baostock_code.startswith('sh.'):
                        ts_code = baostock_code[3:] + '.SH'
                    else:
                        ts_code = baostock_code
                    
                    data_request = DataRequest(
                        data_type='stock_daily',
                        ts_code=ts_code,
                        start_date=trade_date,
                        end_date=trade_date,
                        extra_params={
                            'fields': [
                                'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                                'pre_close', 'change', 'pct_chg', 'vol', 'amount'
                            ]
                        }
                    )
                    batch_requests.append(data_request)
                
                # 批量获取数据
                try:
                    batch_results = await self.data_manager.get_data_batch(batch_requests)
                    
                    for i, result in enumerate(batch_results):
                        if not result.empty:
                            all_daily_data.append(result)
                        else:
                            failed_stocks.append(batch_stocks.iloc[i]['ts_code'])
                            
                except Exception as e:
                    self.logger.error(f"批量获取第 {batch_start//batch_size + 1} 批数据失败: {e}")
                    # 如果批量失败，尝试逐个获取
                    self.logger.info("尝试逐个获取...")
                    for request in batch_requests:
                        try:
                            result = await self.data_manager.get_data(request)
                            if not result.empty:
                                all_daily_data.append(result)
                            else:
                                failed_stocks.append(request.ts_code)
                        except Exception as single_error:
                            self.logger.warning(f"获取 {request.ts_code} 数据失败: {single_error}")
                            failed_stocks.append(request.ts_code)
                
                self.logger.info(f"第 {batch_start//batch_size + 1} 批完成，已获取 {len(all_daily_data)} 只股票数据")
            
            if failed_stocks:
                self.logger.warning(f"有 {len(failed_stocks)} 只股票数据获取失败")
            
            self.logger.info(f"批量获取完成，成功获取 {len(all_daily_data)} 只股票的数据")
            
            # 3. 合并所有数据
            if not all_daily_data:
                self.logger.warning(f"未获取到 {trade_date} 的任何股票数据")
                return pd.DataFrame()
            
            raw_data = pd.concat(all_daily_data, ignore_index=True)
            
            # 4. 合并股票名称信息
            merged_data = raw_data.merge(
                stock_list[['ts_code', 'name']], 
                on='ts_code', 
                how='left',
                suffixes=('', '_basic')
            )
            
            # 处理合并后的name列
            if 'name' not in merged_data.columns:
                if 'name_basic' in merged_data.columns:
                    merged_data['name'] = merged_data['name_basic']
                    merged_data = merged_data.drop(columns=['name_basic'])
                else:
                    merged_data['name'] = '未知'
            
            # 填充缺失的股票名称
            merged_data['name'] = merged_data['name'].fillna('未知')
            
            self.logger.info(f"成功获取 {len(merged_data)} 只股票的 {trade_date} 数据")
            return merged_data
            
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {e}")
            raise DataSourceError(f"无法获取 {trade_date} 的股票数据: {str(e)}")
    
    async def _detect_limit_up_stocks(self, stock_data: pd.DataFrame, 
                                    request: LimitUpStatsRequest) -> List[StockDailyData]:
        """
        检测涨停股票
        
        Args:
            stock_data: 股票数据DataFrame
            request: 请求参数
            
        Returns:
            涨停股票数据列表
        """
        limit_up_stocks = []
        detection_errors = []
        
        # 转换为StockDailyData对象列表
        stock_data_list = []
        for _, row in stock_data.iterrows():
            try:
                stock_daily = StockDailyData(
                    ts_code=row['ts_code'],
                    trade_date=row['trade_date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    pre_close=float(row['pre_close']),
                    change=float(row['change']),
                    pct_chg=float(row['pct_chg']),
                    vol=int(row['vol']) if pd.notna(row['vol']) else 0,
                    amount=float(row['amount']) if pd.notna(row['amount']) else 0.0,
                    name=str(row['name'])
                )
                stock_data_list.append(stock_daily)
            except Exception as e:
                detection_errors.append({
                    'ts_code': row.get('ts_code', 'UNKNOWN'),
                    'error': str(e)
                })
                continue
        
        if detection_errors:
            self.logger.warning(f"数据转换失败的股票数量: {len(detection_errors)}")
        
        # 批量检测涨停
        detection_results = self.limit_up_detector.batch_detect_limit_up(stock_data_list)
        
        # 筛选涨停股票
        for i, result in enumerate(detection_results):
            if result.is_limit_up and result.confidence > 0.5:  # 置信度阈值
                # 检查是否符合过滤条件
                stock_data_obj = stock_data_list[i]
                
                # ST股票过滤
                if not request.include_st:
                    try:
                        is_st = self.stock_classifier.is_st_stock(stock_data_obj.name)
                        if is_st:
                            continue
                    except Exception:
                        # 如果ST检测失败，保守处理，包含该股票
                        pass
                
                # 市场过滤
                if request.market_filter:
                    try:
                        market = self.stock_classifier.classify_market(stock_data_obj.ts_code)
                        if market not in request.market_filter:
                            continue
                    except Exception:
                        # 如果市场分类失败，保守处理，包含该股票
                        pass
                
                limit_up_stocks.append(stock_data_obj)
        
        self.logger.info(f"涨停检测完成: 总股票数 {len(stock_data_list)}, "
                        f"涨停股票数 {len(limit_up_stocks)}, "
                        f"数据错误数 {len(detection_errors)}")
        
        return limit_up_stocks
    
    async def _classify_stocks_by_market(self, limit_up_stocks: List[StockDailyData], 
                                       request: LimitUpStatsRequest) -> Dict[str, List[StockDailyData]]:
        """
        按市场分类涨停股票
        
        Args:
            limit_up_stocks: 涨停股票列表
            request: 请求参数
            
        Returns:
            按市场分类的股票字典
        """
        classified_stocks = {
            'shanghai': [],
            'shenzhen': [],
            'star': [],
            'beijing': [],
            'st': [],
            'non_st': [],
            'unknown': []
        }
        
        classification_errors = []
        
        for stock in limit_up_stocks:
            try:
                # 进行完整分类
                classification_result = self.stock_classifier.classify_stock(
                    stock.ts_code, stock.name
                )
                
                market = classification_result.market
                is_st = classification_result.is_st
                
                # 按市场分类
                if market in classified_stocks:
                    classified_stocks[market].append(stock)
                else:
                    classified_stocks['unknown'].append(stock)
                
                # 按ST分类
                if is_st:
                    classified_stocks['st'].append(stock)
                else:
                    classified_stocks['non_st'].append(stock)
                
            except Exception as e:
                classification_errors.append({
                    'ts_code': stock.ts_code,
                    'name': stock.name,
                    'error': str(e)
                })
                
                # 分类失败的股票放入unknown
                classified_stocks['unknown'].append(stock)
                classified_stocks['non_st'].append(stock)  # 保守处理，当作非ST
        
        if classification_errors:
            self.logger.warning(f"分类失败的股票数量: {len(classification_errors)}")
            for error in classification_errors[:5]:  # 只记录前5个错误
                self.logger.debug(f"分类失败: {error}")
        
        # 记录分类统计
        for market, stocks in classified_stocks.items():
            if stocks:
                self.logger.debug(f"{market}: {len(stocks)} 只股票")
        
        return classified_stocks
    
    def _aggregate_statistics(self, classified_stocks: Dict[str, List[StockDailyData]], 
                            request: LimitUpStatsRequest) -> Dict[str, Any]:
        """
        聚合统计数据
        
        Args:
            classified_stocks: 按市场分类的股票
            request: 请求参数
            
        Returns:
            聚合后的统计数据
        """
        # 计算各市场数量
        shanghai_count = len(classified_stocks['shanghai'])
        shenzhen_count = len(classified_stocks['shenzhen'])
        star_count = len(classified_stocks['star'])
        beijing_count = len(classified_stocks['beijing'])
        st_count = len(classified_stocks['st'])
        non_st_count = len(classified_stocks['non_st'])
        
        # 总数应该等于各市场之和
        total_count = shanghai_count + shenzhen_count + star_count + beijing_count
        
        # 数据一致性检查
        consistency_check = self._validate_statistics_consistency(
            total_count, st_count, non_st_count, classified_stocks
        )
        
        if not consistency_check['is_consistent']:
            self.logger.warning(f"数据一致性检查失败: {consistency_check['issues']}")
            # 使用修正后的数据
            total_count = consistency_check['corrected_total']
            st_count = consistency_check['corrected_st']
            non_st_count = consistency_check['corrected_non_st']
        
        # 构建涨停股票代码列表和市场分解
        aggregation_result = self._build_market_breakdown(classified_stocks)
        all_limit_up_stocks = aggregation_result['all_stocks']
        market_breakdown = aggregation_result['market_breakdown']
        
        # 添加未知市场的股票到总数
        if classified_stocks.get('unknown'):
            total_count += len(classified_stocks['unknown'])
        
        # 最终一致性检查和修正
        final_validation = self._validate_final_statistics(
            all_limit_up_stocks, total_count, market_breakdown
        )
        
        if not final_validation['is_valid']:
            self.logger.warning(f"最终统计验证失败: {final_validation['issues']}")
            total_count = final_validation['corrected_total']
            all_limit_up_stocks = final_validation['corrected_stocks']
        
        stats = {
            'total': total_count,
            'non_st': non_st_count,
            'shanghai': shanghai_count,
            'shenzhen': shenzhen_count,
            'star': star_count,
            'beijing': beijing_count,
            'st': st_count,
            'limit_up_stocks': all_limit_up_stocks,
            'market_breakdown': market_breakdown,
            'aggregation_metadata': {
                'consistency_check': consistency_check,
                'final_validation': final_validation,
                'aggregation_time': datetime.now().isoformat()
            }
        }
        
        # 记录统计摘要
        self.logger.info(f"统计聚合完成: 总计={total_count}, 非ST={non_st_count}, "
                        f"上证={shanghai_count}, 深证={shenzhen_count}, "
                        f"科创板={star_count}, 北证={beijing_count}, ST={st_count}")
        
        return stats
    
    def _validate_statistics_consistency(self, total_count: int, st_count: int, 
                                       non_st_count: int, 
                                       classified_stocks: Dict[str, List[StockDailyData]]) -> Dict[str, Any]:
        """
        验证统计数据一致性
        
        Args:
            total_count: 市场总数
            st_count: ST股票数量
            non_st_count: 非ST股票数量
            classified_stocks: 分类后的股票
            
        Returns:
            一致性检查结果
        """
        issues = []
        is_consistent = True
        corrected_total = total_count
        corrected_st = st_count
        corrected_non_st = non_st_count
        
        # 检查市场总数与ST分类总数的一致性
        st_total = st_count + non_st_count
        if total_count != st_total:
            issues.append(f"市场总数({total_count}) != ST分类总数({st_total})")
            is_consistent = False
            
            # 修正策略：使用实际股票数量
            actual_total = len(set(
                stock.ts_code 
                for stocks in classified_stocks.values() 
                for stock in stocks
                if stocks  # 确保stocks不为空
            ))
            corrected_total = actual_total
        
        # 检查各分类是否有重复股票
        all_stocks_by_category = {}
        for category, stocks in classified_stocks.items():
            if stocks:
                stock_codes = [stock.ts_code for stock in stocks]
                duplicates = len(stock_codes) - len(set(stock_codes))
                if duplicates > 0:
                    issues.append(f"{category}分类中有{duplicates}个重复股票")
                    is_consistent = False
                all_stocks_by_category[category] = set(stock_codes)
        
        # 检查ST和非ST分类的重叠
        if 'st' in all_stocks_by_category and 'non_st' in all_stocks_by_category:
            overlap = all_stocks_by_category['st'] & all_stocks_by_category['non_st']
            if overlap:
                issues.append(f"ST和非ST分类有重叠股票: {list(overlap)[:5]}")  # 只显示前5个
                is_consistent = False
        
        # 重新计算修正后的数量
        if not is_consistent:
            corrected_st = len(classified_stocks.get('st', []))
            corrected_non_st = len(classified_stocks.get('non_st', []))
            
            # 确保总数一致性
            market_total = (len(classified_stocks.get('shanghai', [])) + 
                          len(classified_stocks.get('shenzhen', [])) + 
                          len(classified_stocks.get('star', [])) + 
                          len(classified_stocks.get('beijing', [])) +
                          len(classified_stocks.get('unknown', [])))
            corrected_total = market_total
        
        return {
            'is_consistent': is_consistent,
            'issues': issues,
            'corrected_total': corrected_total,
            'corrected_st': corrected_st,
            'corrected_non_st': corrected_non_st,
            'validation_details': {
                'original_total': total_count,
                'original_st': st_count,
                'original_non_st': non_st_count,
                'categories_checked': list(classified_stocks.keys())
            }
        }
    
    def _build_market_breakdown(self, classified_stocks: Dict[str, List[StockDailyData]]) -> Dict[str, Any]:
        """
        构建市场分解数据
        
        Args:
            classified_stocks: 分类后的股票
            
        Returns:
            市场分解结果
        """
        all_limit_up_stocks = []
        market_breakdown = {}
        
        # 处理主要市场
        main_markets = ['shanghai', 'shenzhen', 'star', 'beijing']
        for market in main_markets:
            stocks = classified_stocks.get(market, [])
            stock_codes = [stock.ts_code for stock in stocks]
            market_breakdown[market] = stock_codes
            all_limit_up_stocks.extend(stock_codes)
        
        # 处理未知市场
        if classified_stocks.get('unknown'):
            unknown_codes = [stock.ts_code for stock in classified_stocks['unknown']]
            market_breakdown['unknown'] = unknown_codes
            all_limit_up_stocks.extend(unknown_codes)
        
        # 去重并保持顺序
        seen = set()
        unique_stocks = []
        for code in all_limit_up_stocks:
            if code not in seen:
                seen.add(code)
                unique_stocks.append(code)
        
        # 构建详细的市场统计
        market_stats = {}
        for market, codes in market_breakdown.items():
            market_stats[market] = {
                'count': len(codes),
                'percentage': len(codes) / len(unique_stocks) * 100 if unique_stocks else 0,
                'codes': codes
            }
        
        return {
            'all_stocks': unique_stocks,
            'market_breakdown': market_breakdown,
            'market_stats': market_stats,
            'total_unique_stocks': len(unique_stocks)
        }
    
    def _validate_final_statistics(self, all_stocks: List[str], total_count: int, 
                                 market_breakdown: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        验证最终统计数据
        
        Args:
            all_stocks: 所有股票代码列表
            total_count: 总数
            market_breakdown: 市场分解
            
        Returns:
            验证结果
        """
        issues = []
        is_valid = True
        corrected_total = total_count
        corrected_stocks = all_stocks.copy()
        
        # 检查股票列表长度与总数的一致性
        if len(all_stocks) != total_count:
            issues.append(f"股票列表长度({len(all_stocks)}) != 总数({total_count})")
            is_valid = False
            corrected_total = len(all_stocks)
        
        # 检查市场分解的总数
        breakdown_total = sum(len(codes) for codes in market_breakdown.values())
        if breakdown_total != len(all_stocks):
            issues.append(f"市场分解总数({breakdown_total}) != 股票列表长度({len(all_stocks)})")
            is_valid = False
        
        # 检查股票代码的重复
        unique_stocks = list(set(all_stocks))
        if len(unique_stocks) != len(all_stocks):
            duplicates = len(all_stocks) - len(unique_stocks)
            issues.append(f"股票列表中有{duplicates}个重复代码")
            is_valid = False
            corrected_stocks = unique_stocks
            corrected_total = len(unique_stocks)
        
        # 检查股票代码格式
        invalid_codes = []
        for code in unique_stocks:
            if not self._is_valid_stock_code(code):
                invalid_codes.append(code)
        
        if invalid_codes:
            issues.append(f"发现{len(invalid_codes)}个无效股票代码: {invalid_codes[:5]}")
            # 不标记为无效，因为这可能是数据源的问题
        
        return {
            'is_valid': is_valid,
            'issues': issues,
            'corrected_total': corrected_total,
            'corrected_stocks': corrected_stocks,
            'validation_details': {
                'original_total': total_count,
                'original_stock_count': len(all_stocks),
                'unique_stock_count': len(unique_stocks),
                'breakdown_total': breakdown_total,
                'invalid_codes': invalid_codes
            }
        }
    
    def _is_valid_stock_code(self, code: str) -> bool:
        """
        检查股票代码格式是否有效
        
        Args:
            code: 股票代码
            
        Returns:
            是否有效
        """
        import re
        # 基本的股票代码格式检查
        pattern = r'^\d{6}\.(SH|SZ|BJ)$'
        return bool(re.match(pattern, code))
    
    def get_aggregation_summary(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取聚合统计摘要
        
        Args:
            stats: 统计数据
            
        Returns:
            统计摘要
        """
        summary = {
            'basic_stats': {
                'total': stats['total'],
                'non_st': stats['non_st'],
                'st': stats['st']
            },
            'market_distribution': {
                'shanghai': stats['shanghai'],
                'shenzhen': stats['shenzhen'],
                'star': stats['star'],
                'beijing': stats['beijing']
            },
            'percentages': {},
            'data_quality': {}
        }
        
        # 计算百分比
        total = stats['total']
        if total > 0:
            summary['percentages'] = {
                'non_st_pct': (stats['non_st'] / total) * 100,
                'st_pct': (stats['st'] / total) * 100,
                'shanghai_pct': (stats['shanghai'] / total) * 100,
                'shenzhen_pct': (stats['shenzhen'] / total) * 100,
                'star_pct': (stats['star'] / total) * 100,
                'beijing_pct': (stats['beijing'] / total) * 100
            }
        
        # 数据质量指标
        metadata = stats.get('aggregation_metadata', {})
        consistency_check = metadata.get('consistency_check', {})
        final_validation = metadata.get('final_validation', {})
        
        summary['data_quality'] = {
            'consistency_passed': consistency_check.get('is_consistent', True),
            'validation_passed': final_validation.get('is_valid', True),
            'consistency_issues': len(consistency_check.get('issues', [])),
            'validation_issues': len(final_validation.get('issues', []))
        }
        
        return summary
    
    def validate_data_completeness(self, stock_data: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据完整性
        
        Args:
            stock_data: 股票数据
            
        Returns:
            验证结果
        """
        validation_result = {
            'is_complete': True,
            'total_stocks': len(stock_data),
            'missing_fields': {},
            'invalid_data': {},
            'warnings': [],
            'recommendations': []
        }
        
        if stock_data.empty:
            validation_result['is_complete'] = False
            validation_result['warnings'].append('股票数据为空')
            validation_result['recommendations'].append('检查数据源和交易日期')
            return validation_result
        
        # 检查必需字段
        required_fields = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close']
        for field in required_fields:
            if field not in stock_data.columns:
                validation_result['missing_fields'][field] = '字段缺失'
                validation_result['is_complete'] = False
            else:
                # 检查空值
                null_count = stock_data[field].isnull().sum()
                if null_count > 0:
                    validation_result['missing_fields'][field] = f'{null_count} 个空值'
                    if null_count > len(stock_data) * 0.1:  # 超过10%的空值
                        validation_result['is_complete'] = False
        
        # 检查数据有效性
        if 'close' in stock_data.columns and 'pre_close' in stock_data.columns:
            # 检查异常的价格变动
            try:
                pct_changes = ((stock_data['close'] - stock_data['pre_close']) / stock_data['pre_close']).abs()
                extreme_changes = (pct_changes > 0.5).sum()  # 超过50%变动的股票数
                if extreme_changes > 0:
                    validation_result['warnings'].append(f'{extreme_changes} 只股票有极端价格变动')
            except Exception as e:
                validation_result['invalid_data']['price_calculation'] = str(e)
        
        # 检查股票名称
        if 'name' in stock_data.columns:
            unnamed_count = (stock_data['name'].isnull() | (stock_data['name'] == '未知')).sum()
            if unnamed_count > 0:
                validation_result['warnings'].append(f'{unnamed_count} 只股票缺少名称信息')
                validation_result['recommendations'].append('缺少名称信息可能影响ST股票检测准确性')
        
        # 数据量检查
        if len(stock_data) < 100:
            validation_result['warnings'].append(f'股票数据量较少: {len(stock_data)} 只')
            validation_result['recommendations'].append('检查是否为有效交易日或数据源是否正常')
        elif len(stock_data) > 6000:
            validation_result['warnings'].append(f'股票数据量异常多: {len(stock_data)} 只')
        
        return validation_result
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息
        
        Returns:
            服务统计信息
        """
        stats = self._stats.copy()
        
        # 计算成功率
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
        
        # 计算平均处理时间
        if stats['successful_requests'] > 0:
            stats['average_processing_time'] = stats['total_processing_time'] / stats['successful_requests']
        else:
            stats['average_processing_time'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """重置服务统计信息"""
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'last_request_time': None
        }
        self.logger.info("服务统计信息已重置")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        服务健康检查
        
        Returns:
            健康检查结果
        """
        health_result = {
            'service_status': 'healthy',
            'components': {},
            'last_check': datetime.now().isoformat(),
            'issues': []
        }
        
        try:
            # 检查数据管理器
            if self.data_manager:
                health_result['components']['data_manager'] = 'healthy'
            else:
                health_result['components']['data_manager'] = 'unhealthy'
                health_result['issues'].append('数据管理器未初始化')
                health_result['service_status'] = 'unhealthy'
            
            # 检查工具类
            try:
                # 测试股票分类器
                test_result = self.stock_classifier.classify_market('000001.SZ')
                health_result['components']['stock_classifier'] = 'healthy'
            except Exception as e:
                health_result['components']['stock_classifier'] = 'unhealthy'
                health_result['issues'].append(f'股票分类器异常: {str(e)}')
            
            try:
                # 测试涨停检测器
                test_result = self.limit_up_detector.is_limit_up(10.0, 11.0, 11.0, 10.0)
                health_result['components']['limit_up_detector'] = 'healthy'
            except Exception as e:
                health_result['components']['limit_up_detector'] = 'unhealthy'
                health_result['issues'].append(f'涨停检测器异常: {str(e)}')
            
            # 检查服务统计
            stats = self.get_service_stats()
            if stats['total_requests'] > 0 and stats['success_rate'] < 0.5:
                health_result['issues'].append(f'服务成功率过低: {stats["success_rate"]:.2%}')
                health_result['service_status'] = 'degraded'
            
        except Exception as e:
            health_result['service_status'] = 'unhealthy'
            health_result['issues'].append(f'健康检查异常: {str(e)}')
        
        return health_result
    
    def analyze_market_concentration(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析市场集中度
        
        Args:
            stats: 统计数据
            
        Returns:
            市场集中度分析结果
        """
        total = stats['total']
        if total == 0:
            return {
                'concentration_index': 0.0,
                'dominant_market': None,
                'market_diversity': 0.0,
                'analysis': '无涨停股票数据'
            }
        
        # 计算各市场占比
        market_counts = {
            'shanghai': stats['shanghai'],
            'shenzhen': stats['shenzhen'],
            'star': stats['star'],
            'beijing': stats['beijing']
        }
        
        # 过滤掉零值
        non_zero_markets = {k: v for k, v in market_counts.items() if v > 0}
        
        if not non_zero_markets:
            return {
                'concentration_index': 0.0,
                'dominant_market': None,
                'market_diversity': 0.0,
                'analysis': '无有效市场数据'
            }
        
        # 计算赫芬达尔指数（HHI）衡量集中度
        market_shares = {k: v / total for k, v in non_zero_markets.items()}
        hhi = sum(share ** 2 for share in market_shares.values())
        
        # 找出主导市场
        dominant_market = max(market_shares.items(), key=lambda x: x[1])
        
        # 计算市场多样性（有效市场数量）
        effective_markets = 1 / hhi if hhi > 0 else 0
        
        # 集中度分析
        if hhi > 0.5:
            concentration_level = '高度集中'
        elif hhi > 0.25:
            concentration_level = '中度集中'
        else:
            concentration_level = '分散'
        
        return {
            'concentration_index': hhi,
            'concentration_level': concentration_level,
            'dominant_market': {
                'name': dominant_market[0],
                'share': dominant_market[1],
                'count': non_zero_markets[dominant_market[0]]
            },
            'market_diversity': effective_markets,
            'market_shares': market_shares,
            'active_markets': len(non_zero_markets),
            'analysis': f'市场呈现{concentration_level}特征，{dominant_market[0]}市场占主导地位'
        }
    
    def analyze_st_stock_impact(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析ST股票影响
        
        Args:
            stats: 统计数据
            
        Returns:
            ST股票影响分析
        """
        total = stats['total']
        st_count = stats['st']
        non_st_count = stats['non_st']
        
        if total == 0:
            return {
                'st_ratio': 0.0,
                'impact_level': '无影响',
                'analysis': '无涨停股票数据'
            }
        
        st_ratio = st_count / total
        
        # 影响程度分析
        if st_ratio > 0.3:
            impact_level = '高影响'
            analysis = 'ST股票在涨停股票中占比较高，可能反映市场投机情绪较强'
        elif st_ratio > 0.15:
            impact_level = '中等影响'
            analysis = 'ST股票占比适中，市场存在一定的投机成分'
        elif st_ratio > 0.05:
            impact_level = '低影响'
            analysis = 'ST股票占比较低，市场相对理性'
        else:
            impact_level = '极低影响'
            analysis = 'ST股票占比极低，市场表现理性'
        
        return {
            'st_count': st_count,
            'non_st_count': non_st_count,
            'st_ratio': st_ratio,
            'impact_level': impact_level,
            'analysis': analysis,
            'recommendations': self._generate_st_recommendations(st_ratio)
        }
    
    def _generate_st_recommendations(self, st_ratio: float) -> List[str]:
        """
        生成ST股票相关建议
        
        Args:
            st_ratio: ST股票占比
            
        Returns:
            建议列表
        """
        recommendations = []
        
        if st_ratio > 0.3:
            recommendations.extend([
                '关注市场投机情绪，注意风险控制',
                '重点分析非ST股票的涨停质量',
                '考虑市场可能存在过度投机行为'
            ])
        elif st_ratio > 0.15:
            recommendations.extend([
                '适度关注ST股票动向',
                '平衡关注ST和非ST股票表现',
                '注意区分投机和价值驱动的涨停'
            ])
        else:
            recommendations.extend([
                '市场表现相对理性，可关注优质涨停股票',
                '重点分析行业和主题驱动的涨停',
                '关注基本面支撑的涨停股票'
            ])
        
        return recommendations
    
    def generate_market_insights(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成市场洞察
        
        Args:
            stats: 统计数据
            
        Returns:
            市场洞察报告
        """
        # 基础统计分析
        summary = self.get_aggregation_summary(stats)
        
        # 市场集中度分析
        concentration_analysis = self.analyze_market_concentration(stats)
        
        # ST股票影响分析
        st_analysis = self.analyze_st_stock_impact(stats)
        
        # 综合市场评估
        market_assessment = self._assess_market_condition(stats, concentration_analysis, st_analysis)
        
        return {
            'summary': summary,
            'concentration_analysis': concentration_analysis,
            'st_analysis': st_analysis,
            'market_assessment': market_assessment,
            'key_insights': self._extract_key_insights(stats, concentration_analysis, st_analysis),
            'generated_at': datetime.now().isoformat()
        }
    
    def _assess_market_condition(self, stats: Dict[str, Any], 
                               concentration: Dict[str, Any], 
                               st_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估市场状况
        
        Args:
            stats: 统计数据
            concentration: 集中度分析
            st_analysis: ST分析
            
        Returns:
            市场状况评估
        """
        total = stats['total']
        
        # 涨停数量评估
        if total > 200:
            volume_assessment = '涨停数量较多，市场活跃度高'
            volume_level = '高'
        elif total > 100:
            volume_assessment = '涨停数量适中，市场表现正常'
            volume_level = '中'
        elif total > 50:
            volume_assessment = '涨停数量较少，市场相对平静'
            volume_level = '低'
        else:
            volume_assessment = '涨停数量很少，市场较为冷清'
            volume_level = '极低'
        
        # 综合评分（0-100）
        volume_score = min(total / 2, 50)  # 涨停数量得分，最高50分
        concentration_score = (1 - concentration['concentration_index']) * 25  # 分散度得分，最高25分
        st_score = max(0, 25 - st_analysis['st_ratio'] * 100)  # ST占比得分，最高25分
        
        overall_score = volume_score + concentration_score + st_score
        
        # 市场状况等级
        if overall_score >= 80:
            market_grade = 'A'
            market_condition = '优秀'
        elif overall_score >= 60:
            market_grade = 'B'
            market_condition = '良好'
        elif overall_score >= 40:
            market_grade = 'C'
            market_condition = '一般'
        else:
            market_grade = 'D'
            market_condition = '较差'
        
        return {
            'overall_score': round(overall_score, 1),
            'market_grade': market_grade,
            'market_condition': market_condition,
            'volume_level': volume_level,
            'volume_assessment': volume_assessment,
            'score_breakdown': {
                'volume_score': round(volume_score, 1),
                'concentration_score': round(concentration_score, 1),
                'st_score': round(st_score, 1)
            }
        }
    
    def _extract_key_insights(self, stats: Dict[str, Any], 
                            concentration: Dict[str, Any], 
                            st_analysis: Dict[str, Any]) -> List[str]:
        """
        提取关键洞察
        
        Args:
            stats: 统计数据
            concentration: 集中度分析
            st_analysis: ST分析
            
        Returns:
            关键洞察列表
        """
        insights = []
        
        total = stats['total']
        
        # 涨停数量洞察
        if total > 200:
            insights.append(f'今日涨停股票数量达到{total}只，市场情绪较为活跃')
        elif total < 50:
            insights.append(f'今日涨停股票仅{total}只，市场表现相对冷静')
        
        # 市场分布洞察
        dominant_market = concentration['dominant_market']
        if dominant_market and dominant_market['share'] > 0.5:
            insights.append(f'{dominant_market["name"]}市场占主导地位，占比{dominant_market["share"]:.1%}')
        
        # ST股票洞察
        if st_analysis['st_ratio'] > 0.2:
            insights.append(f'ST股票占比{st_analysis["st_ratio"]:.1%}，需关注市场投机情绪')
        elif st_analysis['st_ratio'] < 0.05:
            insights.append('ST股票占比较低，市场表现相对理性')
        
        # 市场多样性洞察
        if concentration['market_diversity'] < 2:
            insights.append('涨停股票主要集中在少数市场，市场分化明显')
        elif concentration['market_diversity'] > 3:
            insights.append('涨停股票分布较为均匀，各市场表现相对均衡')
        
        return insights  
  
    async def _detect_limit_up_stocks_with_fallback(self, stock_data: pd.DataFrame, 
                                                  request: LimitUpStatsRequest) -> Tuple[List[StockDailyData], List[str]]:
        """
        带回退机制的涨停股票检测
        
        Args:
            stock_data: 股票数据DataFrame
            request: 请求参数
            
        Returns:
            (成功检测的涨停股票列表, 失败的股票代码列表)
        """
        limit_up_stocks = []
        failed_detections = []
        
        # 转换为StockDailyData对象列表
        stock_data_list = []
        for _, row in stock_data.iterrows():
            try:
                # 验证价格数据
                price_data = {
                    'open': row['open'],
                    'close': row['close'],
                    'high': row['high'],
                    'low': row['low']
                }
                
                self.data_validator.validate_price_data(row['ts_code'], price_data)
                
                stock_daily = StockDailyData(
                    ts_code=row['ts_code'],
                    trade_date=row['trade_date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    pre_close=float(row['pre_close']),
                    change=float(row['change']),
                    pct_chg=float(row['pct_chg']),
                    vol=int(row['vol']) if pd.notna(row['vol']) else 0,
                    amount=float(row['amount']) if pd.notna(row['amount']) else 0.0,
                    name=str(row['name'])
                )
                stock_data_list.append(stock_daily)
                
            except LimitUpDetectionError as e:
                # 使用回退机制处理检测错误
                is_limit_up = self.fallback_manager.handle_detection_error(row['ts_code'], e)
                if is_limit_up:
                    # 如果回退结果认为是涨停，仍然尝试创建对象
                    try:
                        stock_daily = StockDailyData(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date'],
                            open=float(row.get('open', 0)),
                            high=float(row.get('high', 0)),
                            low=float(row.get('low', 0)),
                            close=float(row.get('close', 0)),
                            pre_close=float(row.get('pre_close', 0)),
                            change=float(row.get('change', 0)),
                            pct_chg=float(row.get('pct_chg', 0)),
                            vol=int(row.get('vol', 0)) if pd.notna(row.get('vol')) else 0,
                            amount=float(row.get('amount', 0)) if pd.notna(row.get('amount')) else 0.0,
                            name=str(row.get('name', '未知'))
                        )
                        stock_data_list.append(stock_daily)
                    except Exception:
                        failed_detections.append(row['ts_code'])
                else:
                    failed_detections.append(row['ts_code'])
                self._stats['fallback_used'] += 1
                
            except Exception as e:
                failed_detections.append(row['ts_code'])
                self.logger.debug(f"股票 {row['ts_code']} 数据转换失败: {e}")
        
        # 批量检测涨停
        try:
            detection_results = self.limit_up_detector.batch_detect_limit_up(stock_data_list)
            
            # 筛选涨停股票
            for i, result in enumerate(detection_results):
                if result.is_limit_up and result.confidence > 0.5:
                    stock_data_obj = stock_data_list[i]
                    
                    # 应用过滤条件
                    if self._should_include_stock(stock_data_obj, request):
                        limit_up_stocks.append(stock_data_obj)
                        
        except Exception as e:
            self.logger.error(f"批量涨停检测失败: {e}")
            # 如果批量检测失败，尝试逐个检测
            for stock_data_obj in stock_data_list:
                try:
                    result = self.limit_up_detector.detect_limit_up(stock_data_obj)
                    if result.is_limit_up and result.confidence > 0.5:
                        if self._should_include_stock(stock_data_obj, request):
                            limit_up_stocks.append(stock_data_obj)
                except Exception as detection_error:
                    # 使用回退机制
                    limit_up_error = LimitUpDetectionError(
                        stock_data_obj.ts_code, 
                        str(detection_error)
                    )
                    is_limit_up = self.fallback_manager.handle_detection_error(
                        stock_data_obj.ts_code, limit_up_error
                    )
                    if not is_limit_up:
                        failed_detections.append(stock_data_obj.ts_code)
                    self._stats['fallback_used'] += 1
        
        self.logger.info(f"涨停检测完成: 成功 {len(limit_up_stocks)}, 失败 {len(failed_detections)}")
        return limit_up_stocks, failed_detections
    
    async def _classify_stocks_with_fallback(self, limit_up_stocks: List[StockDailyData], 
                                           request: LimitUpStatsRequest) -> Tuple[Dict[str, List[StockDailyData]], List[str]]:
        """
        带回退机制的股票分类
        
        Args:
            limit_up_stocks: 涨停股票列表
            request: 请求参数
            
        Returns:
            (分类结果字典, 失败的股票代码列表)
        """
        classified_stocks = {
            'shanghai': [],
            'shenzhen': [],
            'star': [],
            'beijing': [],
            'st': [],
            'non_st': [],
            'unknown': []
        }
        
        failed_classifications = []
        
        for stock in limit_up_stocks:
            try:
                # 进行完整分类
                classification_result = self.stock_classifier.classify_stock(
                    stock.ts_code, stock.name
                )
                
                market = classification_result.market
                is_st = classification_result.is_st
                
                # 按市场分类
                if market in classified_stocks:
                    classified_stocks[market].append(stock)
                else:
                    classified_stocks['unknown'].append(stock)
                
                # 按ST分类
                if is_st:
                    classified_stocks['st'].append(stock)
                else:
                    classified_stocks['non_st'].append(stock)
                    
            except StockClassificationError as e:
                # 使用回退机制处理分类错误
                fallback_market = self.fallback_manager.handle_classification_error(stock.ts_code, e)
                
                # 使用回退分类结果
                if fallback_market in classified_stocks:
                    classified_stocks[fallback_market].append(stock)
                else:
                    classified_stocks['unknown'].append(stock)
                
                # 保守处理ST分类
                classified_stocks['non_st'].append(stock)
                
                self._stats['fallback_used'] += 1
                self.logger.debug(f"股票 {stock.ts_code} 使用回退分类: {fallback_market}")
                
            except Exception as e:
                # 完全失败的情况
                failed_classifications.append(stock.ts_code)
                
                # 使用最保守的分类
                classified_stocks['unknown'].append(stock)
                classified_stocks['non_st'].append(stock)
                
                self.logger.warning(f"股票 {stock.ts_code} 分类完全失败: {e}")
        
        # 记录分类统计
        for market, stocks in classified_stocks.items():
            if stocks:
                self.logger.debug(f"{market}: {len(stocks)} 只股票")
        
        if failed_classifications:
            self.logger.warning(f"分类失败的股票: {failed_classifications}")
        
        return classified_stocks, failed_classifications
    
    def _should_include_stock(self, stock: StockDailyData, request: LimitUpStatsRequest) -> bool:
        """
        判断是否应该包含某只股票
        
        Args:
            stock: 股票数据
            request: 请求参数
            
        Returns:
            是否应该包含
        """
        try:
            # ST股票过滤
            if not request.include_st:
                is_st = self.stock_classifier.is_st_stock(stock.name)
                if is_st:
                    return False
            
            # 市场过滤
            if request.market_filter:
                market = self.stock_classifier.classify_market(stock.ts_code)
                validated_filter = ValidationUtils.validate_market_filter(request.market_filter)
                if market not in validated_filter:
                    return False
            
            return True
            
        except Exception as e:
            # 如果过滤检查失败，保守处理，包含该股票
            self.logger.debug(f"股票 {stock.ts_code} 过滤检查失败: {e}")
            return True