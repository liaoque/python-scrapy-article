#!/usr/bin/env python3
"""
最终集成测试运行器

执行完整的测试套件，包括单元测试、集成测试、性能测试和数据准确性验证
生成详细的测试报告和性能分析
"""

import os
import sys
import subprocess
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quickstock.utils.performance_monitor import get_performance_monitor
from quickstock.utils.memory_optimizer import memory_efficient_processing


class FinalIntegrationTestRunner:
    """最终集成测试运行器"""
    
    def __init__(self, test_dir: str = None, output_dir: str = None):
        """
        初始化测试运行器
        
        Args:
            test_dir: 测试目录路径
            output_dir: 输出目录路径
        """
        self.project_root = project_root
        self.test_dir = Path(test_dir) if test_dir else self.project_root / "tests"
        self.output_dir = Path(output_dir) if output_dir else self.project_root / "test_reports"
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self._setup_logging()
        
        # 测试结果
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'performance_metrics': {},
            'coverage_report': {},
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'success_rate': 0.0,
                'total_duration': 0.0
            }
        }
        
        # 性能监控
        self.performance_monitor = get_performance_monitor()
    
    def _setup_logging(self):
        """设置日志配置"""
        log_file = self.output_dir / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"测试运行器初始化完成，日志文件: {log_file}")
    
    def run_all_tests(self, test_patterns: List[str] = None, 
                     include_performance: bool = True,
                     include_coverage: bool = True) -> Dict[str, Any]:
        """
        运行所有测试
        
        Args:
            test_patterns: 测试模式列表
            include_performance: 是否包含性能测试
            include_coverage: 是否包含覆盖率测试
            
        Returns:
            测试结果字典
        """
        start_time = time.time()
        self.logger.info("开始执行最终集成测试套件")
        
        try:
            # 1. 运行单元测试
            self.logger.info("执行单元测试...")
            unit_test_results = self._run_unit_tests(test_patterns)
            self.test_results['test_suites']['unit_tests'] = unit_test_results
            
            # 2. 运行集成测试
            self.logger.info("执行集成测试...")
            integration_test_results = self._run_integration_tests(test_patterns)
            self.test_results['test_suites']['integration_tests'] = integration_test_results
            
            # 3. 运行财务报告专项测试
            self.logger.info("执行财务报告专项测试...")
            financial_test_results = self._run_financial_tests()
            self.test_results['test_suites']['financial_tests'] = financial_test_results
            
            # 4. 运行性能测试（如果启用）
            if include_performance:
                self.logger.info("执行性能测试...")
                performance_test_results = self._run_performance_tests()
                self.test_results['test_suites']['performance_tests'] = performance_test_results
                
                # 收集性能指标
                self.test_results['performance_metrics'] = self._collect_performance_metrics()
            
            # 5. 运行覆盖率测试（如果启用）
            if include_coverage:
                self.logger.info("执行覆盖率测试...")
                coverage_results = self._run_coverage_tests()
                self.test_results['coverage_report'] = coverage_results
            
            # 6. 运行最终集成测试套件
            self.logger.info("执行最终集成测试套件...")
            final_integration_results = self._run_final_integration_suite()
            self.test_results['test_suites']['final_integration'] = final_integration_results
            
            # 7. 计算汇总统计
            self._calculate_summary_statistics()
            
            # 8. 生成测试报告
            self._generate_comprehensive_report()
            
            end_time = time.time()
            self.test_results['summary']['total_duration'] = end_time - start_time
            
            self.logger.info(f"测试套件执行完成，总耗时: {self.test_results['summary']['total_duration']:.2f}秒")
            
            return self.test_results
            
        except Exception as e:
            self.logger.error(f"测试执行失败: {e}")
            raise
    
    def _run_unit_tests(self, test_patterns: List[str] = None) -> Dict[str, Any]:
        """运行单元测试"""
        unit_test_patterns = [
            "test_models.py",
            "test_financial_models.py", 
            "test_financial_errors.py",
            "test_validators.py",
            "test_code_converter.py"
        ]
        
        if test_patterns:
            unit_test_patterns.extend([p for p in test_patterns if 'unit' in p.lower()])
        
        return self._run_pytest_suite("单元测试", unit_test_patterns)
    
    def _run_integration_tests(self, test_patterns: List[str] = None) -> Dict[str, Any]:
        """运行集成测试"""
        integration_test_patterns = [
            "test_client_integration.py",
            "test_data_source_integration.py",
            "test_error_handling_integration.py",
            "test_end_to_end.py"
        ]
        
        if test_patterns:
            integration_test_patterns.extend([p for p in test_patterns if 'integration' in p.lower()])
        
        return self._run_pytest_suite("集成测试", integration_test_patterns)
    
    def _run_financial_tests(self) -> Dict[str, Any]:
        """运行财务报告专项测试"""
        financial_test_patterns = [
            "test_financial_reports_service.py",
            "test_client_financial_reports_unit.py",
            "test_client_financial_reports_integration.py",
            "test_comprehensive_financial_reports_integration.py",
            "test_financial_reports_integration_suite.py",
            "test_financial_reports_workflow_integration.py",
            "test_config_financial_reports.py",
            "test_config_financial_reports_integration.py",
            "test_financial_error_integration.py",
            "test_baostock_financial_data.py"
        ]
        
        return self._run_pytest_suite("财务报告测试", financial_test_patterns)
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        performance_test_patterns = [
            "test_performance_integration.py",
            "test_performance_financial_reports.py",
            "test_performance_benchmarks.py",
            "test_performance_optimizations.py",
            "test_memory_optimization.py"
        ]
        
        return self._run_pytest_suite("性能测试", performance_test_patterns)
    
    def _run_coverage_tests(self) -> Dict[str, Any]:
        """运行覆盖率测试"""
        try:
            # 使用pytest-cov运行覆盖率测试
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.test_dir),
                "--cov=quickstock",
                "--cov-report=json",
                f"--cov-report=html:{self.output_dir}/coverage_html",
                "--cov-report=term-missing",
                "-v"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            # 解析覆盖率报告
            coverage_json_path = self.project_root / "coverage.json"
            coverage_data = {}
            
            if coverage_json_path.exists():
                with open(coverage_json_path, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
            
            return {
                'success': result.returncode == 0,
                'coverage_data': coverage_data,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            self.logger.error(f"覆盖率测试执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'coverage_data': {}
            }
    
    def _run_final_integration_suite(self) -> Dict[str, Any]:
        """运行最终集成测试套件"""
        return self._run_pytest_suite("最终集成测试", ["test_final_integration_suite.py"])
    
    def _run_pytest_suite(self, suite_name: str, test_patterns: List[str]) -> Dict[str, Any]:
        """
        运行pytest测试套件
        
        Args:
            suite_name: 测试套件名称
            test_patterns: 测试文件模式列表
            
        Returns:
            测试结果字典
        """
        start_time = time.time()
        
        try:
            # 构建pytest命令
            cmd = [sys.executable, "-m", "pytest"]
            
            # 添加测试文件
            for pattern in test_patterns:
                test_file = self.test_dir / pattern
                if test_file.exists():
                    cmd.append(str(test_file))
            
            # 添加pytest参数
            cmd.extend([
                "-v",  # 详细输出
                "--tb=short",  # 简短的traceback
                "--json-report",  # JSON报告
                f"--json-report-file={self.output_dir}/{suite_name.lower().replace(' ', '_')}_report.json"
            ])
            
            # 执行测试
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 解析JSON报告
            json_report_path = self.output_dir / f"{suite_name.lower().replace(' ', '_')}_report.json"
            json_data = {}
            
            if json_report_path.exists():
                try:
                    with open(json_report_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                except Exception as e:
                    self.logger.warning(f"无法解析JSON报告: {e}")
            
            # 构建结果
            test_result = {
                'suite_name': suite_name,
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'json_report': json_data,
                'test_patterns': test_patterns
            }
            
            # 从JSON报告中提取统计信息
            if json_data and 'summary' in json_data:
                summary = json_data['summary']
                test_result.update({
                    'total_tests': summary.get('total', 0),
                    'passed_tests': summary.get('passed', 0),
                    'failed_tests': summary.get('failed', 0),
                    'skipped_tests': summary.get('skipped', 0),
                    'success_rate': (
                        summary.get('passed', 0) / summary.get('total', 1)
                        if summary.get('total', 0) > 0 else 0
                    )
                })
            
            self.logger.info(f"{suite_name}完成: {test_result.get('success_rate', 0):.2%} 成功率")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"{suite_name}执行超时")
            return {
                'suite_name': suite_name,
                'success': False,
                'error': 'Timeout',
                'duration': 300,
                'test_patterns': test_patterns
            }
        except Exception as e:
            self.logger.error(f"{suite_name}执行失败: {e}")
            return {
                'suite_name': suite_name,
                'success': False,
                'error': str(e),
                'duration': 0,
                'test_patterns': test_patterns
            }
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        try:
            # 从性能监控器获取指标
            performance_summary = self.performance_monitor.get_performance_summary()
            
            # 收集系统资源使用情况
            import psutil
            
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
            }
            
            return {
                'performance_summary': performance_summary,
                'system_metrics': system_metrics,
                'collection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"性能指标收集失败: {e}")
            return {}
    
    def _calculate_summary_statistics(self):
        """计算汇总统计"""
        summary = self.test_results['summary']
        
        for suite_name, suite_results in self.test_results['test_suites'].items():
            if isinstance(suite_results, dict):
                summary['total_tests'] += suite_results.get('total_tests', 0)
                summary['passed_tests'] += suite_results.get('passed_tests', 0)
                summary['failed_tests'] += suite_results.get('failed_tests', 0)
                summary['skipped_tests'] += suite_results.get('skipped_tests', 0)
        
        # 计算总体成功率
        if summary['total_tests'] > 0:
            summary['success_rate'] = summary['passed_tests'] / summary['total_tests']
    
    def _generate_comprehensive_report(self):
        """生成综合测试报告"""
        # 生成JSON报告
        json_report_path = self.output_dir / f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # 生成HTML报告
        html_report_path = self.output_dir / f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self._generate_html_report(html_report_path)
        
        # 生成文本摘要报告
        text_report_path = self.output_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._generate_text_summary(text_report_path)
        
        self.logger.info(f"测试报告已生成:")
        self.logger.info(f"  JSON报告: {json_report_path}")
        self.logger.info(f"  HTML报告: {html_report_path}")
        self.logger.info(f"  文本摘要: {text_report_path}")
    
    def _generate_html_report(self, output_path: Path):
        """生成HTML测试报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickStock 最终集成测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .suite {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .suite-header {{ background-color: #e9e9e9; padding: 10px; font-weight: bold; }}
        .suite-content {{ padding: 15px; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>QuickStock 最终集成测试报告</h1>
        <p>生成时间: {self.test_results['timestamp']}</p>
        <p>测试持续时间: {self.test_results['summary']['total_duration']:.2f} 秒</p>
    </div>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{self.test_results['summary']['total_tests']}</div>
                <div>总测试数</div>
            </div>
            <div class="metric">
                <div class="metric-value success">{self.test_results['summary']['passed_tests']}</div>
                <div>通过测试</div>
            </div>
            <div class="metric">
                <div class="metric-value failure">{self.test_results['summary']['failed_tests']}</div>
                <div>失败测试</div>
            </div>
            <div class="metric">
                <div class="metric-value">{self.test_results['summary']['success_rate']:.2%}</div>
                <div>成功率</div>
            </div>
        </div>
    </div>
    
    <div class="test-suites">
        <h2>测试套件详情</h2>
"""
        
        # 添加每个测试套件的详情
        for suite_name, suite_results in self.test_results['test_suites'].items():
            if isinstance(suite_results, dict):
                status_class = "success" if suite_results.get('success', False) else "failure"
                html_content += f"""
        <div class="suite">
            <div class="suite-header {status_class}">
                {suite_results.get('suite_name', suite_name)} 
                - {suite_results.get('success_rate', 0):.2%} 成功率
            </div>
            <div class="suite-content">
                <p>执行时间: {suite_results.get('duration', 0):.2f} 秒</p>
                <p>测试文件: {', '.join(suite_results.get('test_patterns', []))}</p>
                <table>
                    <tr><th>指标</th><th>数值</th></tr>
                    <tr><td>总测试数</td><td>{suite_results.get('total_tests', 0)}</td></tr>
                    <tr><td>通过测试</td><td>{suite_results.get('passed_tests', 0)}</td></tr>
                    <tr><td>失败测试</td><td>{suite_results.get('failed_tests', 0)}</td></tr>
                    <tr><td>跳过测试</td><td>{suite_results.get('skipped_tests', 0)}</td></tr>
                </table>
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_text_summary(self, output_path: Path):
        """生成文本摘要报告"""
        summary = self.test_results['summary']
        
        content = f"""
QuickStock 最终集成测试摘要报告
{'='*60}

测试时间: {self.test_results['timestamp']}
测试持续时间: {summary['total_duration']:.2f} 秒

总体统计:
  总测试数: {summary['total_tests']}
  通过测试: {summary['passed_tests']}
  失败测试: {summary['failed_tests']}
  跳过测试: {summary['skipped_tests']}
  成功率: {summary['success_rate']:.2%}

测试套件详情:
{'-'*60}
"""
        
        for suite_name, suite_results in self.test_results['test_suites'].items():
            if isinstance(suite_results, dict):
                content += f"""
{suite_results.get('suite_name', suite_name)}:
  状态: {'通过' if suite_results.get('success', False) else '失败'}
  成功率: {suite_results.get('success_rate', 0):.2%}
  执行时间: {suite_results.get('duration', 0):.2f} 秒
  总测试数: {suite_results.get('total_tests', 0)}
  通过: {suite_results.get('passed_tests', 0)}
  失败: {suite_results.get('failed_tests', 0)}
  跳过: {suite_results.get('skipped_tests', 0)}
"""
        
        # 添加性能指标（如果有）
        if self.test_results.get('performance_metrics'):
            content += f"""
性能指标:
{'-'*60}
{json.dumps(self.test_results['performance_metrics'], indent=2, ensure_ascii=False)}
"""
        
        # 添加覆盖率信息（如果有）
        if self.test_results.get('coverage_report'):
            coverage_data = self.test_results['coverage_report'].get('coverage_data', {})
            if coverage_data and 'totals' in coverage_data:
                totals = coverage_data['totals']
                content += f"""
代码覆盖率:
{'-'*60}
  总行数: {totals.get('num_statements', 0)}
  覆盖行数: {totals.get('covered_lines', 0)}
  覆盖率: {totals.get('percent_covered', 0):.2f}%
  缺失行数: {totals.get('missing_lines', 0)}
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QuickStock 最终集成测试运行器')
    parser.add_argument('--test-dir', help='测试目录路径')
    parser.add_argument('--output-dir', help='输出目录路径')
    parser.add_argument('--no-performance', action='store_true', help='跳过性能测试')
    parser.add_argument('--no-coverage', action='store_true', help='跳过覆盖率测试')
    parser.add_argument('--patterns', nargs='*', help='测试文件模式')
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = FinalIntegrationTestRunner(
        test_dir=args.test_dir,
        output_dir=args.output_dir
    )
    
    try:
        # 运行测试
        results = runner.run_all_tests(
            test_patterns=args.patterns,
            include_performance=not args.no_performance,
            include_coverage=not args.no_coverage
        )
        
        # 输出结果摘要
        summary = results['summary']
        print(f"\n{'='*60}")
        print("测试执行完成!")
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过测试: {summary['passed_tests']}")
        print(f"失败测试: {summary['failed_tests']}")
        print(f"成功率: {summary['success_rate']:.2%}")
        print(f"执行时间: {summary['total_duration']:.2f} 秒")
        print(f"{'='*60}")
        
        # 根据测试结果设置退出码
        exit_code = 0 if summary['failed_tests'] == 0 else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"测试执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()