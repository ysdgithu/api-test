import os
import json
import time
from typing import List, Dict, Any
from datetime import datetime
from colorama import Fore, Style


def _format_json(obj: Any) -> str:
    if obj is None:
        return "None"
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return str(obj)


class TestReport:
    def __init__(self):
        self.test_cases: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.base_url = ""
        self.module_name = ""

    def add_test_result(self, result: Dict[str, Any]):
        self.test_cases.append(result)
        self.total_tests += 1
        if result['status'] == 'PASS':
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def add_results(self, results: List[Dict[str, Any]]):
        for result in results:
            self.add_test_result(result)

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()

    def get_duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

    def get_summary(self) -> Dict[str, Any]:
        return {
            'total': self.total_tests,
            'passed': self.passed_tests,
            'failed': self.failed_tests,
            'pass_rate': round(self.passed_tests / self.total_tests * 100, 2) if self.total_tests > 0 else 0,
            'duration': round(self.get_duration(), 2),
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'module_name': self.module_name
        }

    def print_console_report(self):
        print("\n" + "=" * 70)
        print("API Interface Test Report")
        print("=" * 70)

        summary = self.get_summary()
        print(f"\n基本信息")
        print(f"--------")
        print(f"项目地址: {summary['base_url']}")
        print(f"测试模块: {summary['module_name']}")
        print(f"测试时间: {summary['timestamp']}")
        print(f"耗时: {summary['duration']}s")

        print(f"\n测试结果")
        print(f"--------")
        print(f"总测试数: {summary['total']}")
        print(f"通过: {Fore.GREEN}{summary['passed']}{Style.RESET_ALL}")
        print(f"失败: {Fore.RED}{summary['failed']}{Style.RESET_ALL}")
        print(f"通过率: {summary['pass_rate']}%")

        if self.failed_tests > 0:
            print(f"\n{Fore.RED}失败详情{Style.RESET_ALL}")
            print(f"----------")
            for test in self.test_cases:
                if test['status'] == 'FAIL':
                    print(f"  - {test['test_name']}")
                    print(f"    {test.get('message', '')}")
                    req = test.get('request')
                    if req:
                        print(f"    请求: {req.get('method', '')} {req.get('url', '')}")
                        print(f"    请求头: {req.get('request_headers', {})}")
                        if req.get('request_body'):
                            print(f"    请求体: {_format_json(req['request_body'])}")
                        print(f"    响应状态码: {req.get('status_code', '')}")
                        print(f"    响应头: {req.get('response_headers', {})}")
                        print(f"    响应体: {_format_json(req['response_body'])}")
                        if req.get('error'):
                            print(f"    错误: {req['error']}")
                        print()

        print("\n" + "=" * 70)

    def generate_html_report(self, output_dir: str = './reports', filename: str = 'test_report.html') -> str:
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, filename)

        summary = self.get_summary()

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Interface Test Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.8; font-size: 14px; }}
        .info {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #eee;
        }}
        .info-item {{ font-size: 14px; color: #666; }}
        .info-item strong {{ color: #333; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .summary-card.total {{ border-top: 4px solid #6c757d; }}
        .summary-card.passed {{ border-top: 4px solid #28a745; }}
        .summary-card.failed {{ border-top: 4px solid #dc3545; }}
        .summary-card.rate {{ border-top: 4px solid #17a2b8; }}
        .summary-card.duration {{ border-top: 4px solid #ffc107; }}
        .summary-card .number {{ font-size: 32px; font-weight: bold; color: #333; }}
        .summary-card .label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .test-details {{ padding: 30px; }}
        .test-details h2 {{
            font-size: 20px;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .test-table {{ width: 100%; border-collapse: collapse; }}
        .test-table th, .test-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        .test-table th {{ background: #f8f9fa; font-weight: 600; color: #555; }}
        .test-table tr:hover {{ background: #f8f9fa; }}
        .status {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status.pass {{ background: #d4edda; color: #155724; }}
        .status.fail {{ background: #f8d7da; color: #721c24; }}
        .timestamp {{
            font-size: 12px;
            color: #999;
            margin-top: 20px;
            text-align: center;
        }}
        .chart {{
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .chart-bar {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            border-radius: 10px;
            transition: width 0.5s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API Interface Test Report</h1>
            <p>Generated at {summary['timestamp']}</p>
        </div>
        <div class="info">
            <div class="info-item"><strong>项目地址:</strong> {summary['base_url']}</div>
            <div class="info-item"><strong>测试模块:</strong> {summary['module_name']}</div>
        </div>
        <div class="summary">
            <div class="summary-card total">
                <div class="number">{summary['total']}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="summary-card passed">
                <div class="number">{summary['passed']}</div>
                <div class="label">Passed</div>
            </div>
            <div class="summary-card failed">
                <div class="number">{summary['failed']}</div>
                <div class="label">Failed</div>
            </div>
            <div class="summary-card rate">
                <div class="number">{summary['pass_rate']}%</div>
                <div class="label">Pass Rate</div>
                <div class="chart">
                    <div class="chart-bar" style="width: {summary['pass_rate']}%"></div>
                </div>
            </div>
            <div class="summary-card duration">
                <div class="number">{summary['duration']}s</div>
                <div class="label">Duration</div>
            </div>
        </div>
        <div class="test-details">
            <h2>Test Cases</h2>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>"""

        for test in self.test_cases:
            status_class = 'pass' if test['status'] == 'PASS' else 'fail'
            expected = test.get('expected_code', test.get('expected', test.get('expected_key', '-')))
            actual = test.get('actual_code', test.get('actual', '-'))
            message = test.get('message', '')

            html_content += f"""                    <tr>
                        <td>{test['test_name']}</td>
                        <td><span class="status {status_class}">{test['status']}</span></td>
                        <td>{expected}</td>
                        <td>{actual}</td>
                        <td>{message}</td>
                    </tr>"""

        html_content += """                </tbody>
            </table>
        </div>"""

        # 失败详情（含原始请求/响应）
        failed_tests = [t for t in self.test_cases if t['status'] == 'FAIL']
        if failed_tests:
            html_content += """
        <div class="test-details">
            <h2>Failure Details</h2>"""
            for test in failed_tests:
                req = test.get('request', {})
                html_content += f"""
            <div style="margin-bottom: 30px; border: 1px solid #dc3545; border-radius: 8px; overflow: hidden;">
                <div style="background: #f8d7da; padding: 12px 16px; color: #721c24; font-weight: 600;">
                    {test['test_name']} - {test.get('message', '')}
                </div>
                <div style="padding: 16px;">
                    <div style="margin-bottom: 16px;">
                        <strong>Request:</strong>
                        <pre style="background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 13px; margin-top: 8px;">{req.get('method', '')} {req.get('url', '')}
Headers: {_format_json(req.get('request_headers', {}))}
Body: {_format_json(req.get('request_body'))}</pre>
                    </div>
                    <div>
                        <strong>Response:</strong>
                        <pre style="background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 13px; margin-top: 8px;">Status: {req.get('status_code', '')}
Headers: {_format_json(req.get('response_headers', {}))}
Body: {_format_json(req.get('response_body'))}{f'{chr(10)}Error: {req["error"]}' if req.get('error') else ''}</pre>
                    </div>
                </div>
            </div>"""
            html_content += """
        </div>"""

        html_content += """
        <div class="timestamp">Report generated by API Interface Test Skill</div>
    </div>
</body>
</html>"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_path

    def generate_json_report(self, output_dir: str = './reports', filename: str = 'test_results.json') -> str:
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, filename)

        report_data = {
            'summary': self.get_summary(),
            'test_cases': self.test_cases,
            'generated_at': datetime.now().isoformat()
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return report_path
