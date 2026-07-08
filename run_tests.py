import os
import sys
import logging
import glob
import importlib
from datetime import datetime
from colorama import init, Fore, Style

from utils.http_client import HTTPClient, load_config
from report_generator import TestReport

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def discover_tests(test_dir: str = 'tests') -> list:
    test_modules = []
    test_files = glob.glob(os.path.join(test_dir, 'test_*.py'))

    for test_file in test_files:
        if 'test_template.py' in test_file:
            continue

        module_name = os.path.basename(test_file)[:-3]
        module_path = f"{test_dir}.{module_name}"

        try:
            module = importlib.import_module(module_path)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr_name.startswith('Test'):
                    test_modules.append((module_name, attr))
                    logger.info(f"Discovered test class: {attr_name}")
        except ImportError as e:
            logger.warning(f"Failed to import {module_path}: {e}")

    return test_modules


def run_all_tests(config: dict) -> TestReport:
    report = TestReport()
    report.base_url = config['base_url']
    report.start()

    client = HTTPClient(config['base_url'], config['timeout'])
    test_modules = discover_tests()

    if not test_modules:
        logger.warning("No test modules found. Please create test files in the 'tests' directory.")
        report.end()
        return report

    logger.info(f"\nDiscovered {len(test_modules)} test modules")
    logger.info("=" * 60)

    for module_name, test_class in test_modules:
        report.module_name = module_name.replace('test_', '')
        logger.info(f"\nRunning tests from: {module_name}")
        logger.info("-" * 60)

        try:
            test_instance = test_class(client)
            test_instance.run_tests()
            report.add_results(test_instance.get_results())
        except Exception as e:
            logger.error(f"Error running {module_name}: {e}")
            import traceback
            traceback.print_exc()

            error_result = {
                'test_name': f"{module_name} - Initialization Error",
                'status': 'FAIL',
                'expected': 'Test execution',
                'actual': f'Error: {str(e)}',
                'message': f"Test module failed to run: {str(e)}"
            }
            report.add_test_result(error_result)

    report.end()
    return report


def main():
    print(Fore.CYAN + "\n" + "=" * 70)
    print("API Interface Test Runner")
    print("=" * 70 + Style.RESET_ALL)

    config = load_config()

    print(f"\nConfiguration:")
    print(f"  Base URL: {config['base_url']}")
    print(f"  Timeout: {config['timeout']}s")
    print(f"  Report Output: {config['report']['output_dir']}")

    print(f"\n{Fore.YELLOW}Starting tests...{Style.RESET_ALL}")

    report = run_all_tests(config)

    print(f"\n{Fore.GREEN}Generating reports...{Style.RESET_ALL}")

    report.print_console_report()

    report_dir = config['report']['output_dir']
    os.makedirs(report_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_filename = f"test_report_{timestamp}.html"
    json_filename = f"test_results_{timestamp}.json"

    html_path = report.generate_html_report(report_dir, html_filename)
    json_path = report.generate_json_report(report_dir, json_filename)

    print(f"\n{Fore.GREEN}Reports generated successfully:{Style.RESET_ALL}")
    print(f"  HTML Report: {html_path}")
    print(f"  JSON Results: {json_path}")

    if report.failed_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
