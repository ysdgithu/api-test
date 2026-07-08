import requests
import json
import logging
import time
from typing import Dict, Optional, Any, Tuple
from colorama import Fore, Style

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def set_auth_token(self, token: str):
        self.headers['Authorization'] = f'Bearer {token}'

    def remove_auth_token(self):
        self.headers.pop('Authorization', None)

    def set_custom_header(self, key: str, value: str):
        self.headers[key] = value

    def request(self, method: str, endpoint: str, **kwargs) -> Tuple[int, Dict[str, Any], float]:
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Request failed: {e}")
            return 0, {'error': str(e)}, elapsed_time

        elapsed_time = time.time() - start_time

        try:
            response_json = response.json()
        except ValueError:
            response_json = {'text': response.text}

        logger.info(f"{method.upper()} {endpoint} -> {response.status_code} ({elapsed_time:.2f}s)")
        return response.status_code, response_json, elapsed_time

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float]:
        return self.request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float]:
        return self.request('POST', endpoint, json=data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float]:
        return self.request('PUT', endpoint, json=data)

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float]:
        return self.request('PATCH', endpoint, json=data)

    def delete(self, endpoint: str) -> Tuple[int, Dict[str, Any], float]:
        return self.request('DELETE', endpoint)


class APITestCase:
    def __init__(self, client: HTTPClient):
        self.client = client
        self.results = []

    def assert_status_code(self, status_code: int, expected_code: int, test_name: str) -> bool:
        passed = status_code == expected_code
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = {
            'test_name': test_name,
            'status': status,
            'expected_code': expected_code,
            'actual_code': status_code,
            'message': f"Expected {expected_code}, got {status_code}"
        }
        self.results.append(result)

        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if not passed:
            print(f"  {result['message']}")

        return passed

    def assert_json_contains(self, response_json: Dict, key: str, test_name: str) -> bool:
        passed = key in response_json
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = {
            'test_name': test_name,
            'status': status,
            'expected_key': key,
            'message': f"Expected key '{key}' not found in response"
        }
        self.results.append(result)

        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if not passed:
            print(f"  {result['message']}")

        return passed

    def assert_value_equal(self, actual: Any, expected: Any, test_name: str) -> bool:
        passed = actual == expected
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = {
            'test_name': test_name,
            'status': status,
            'expected': expected,
            'actual': actual,
            'message': f"Expected {expected}, got {actual}"
        }
        self.results.append(result)

        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if not passed:
            print(f"  {result['message']}")

        return passed

    def assert_value_in(self, actual: Any, expected_list: list, test_name: str) -> bool:
        passed = actual in expected_list
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = {
            'test_name': test_name,
            'status': status,
            'expected': expected_list,
            'actual': actual,
            'message': f"Expected {actual} in {expected_list}"
        }
        self.results.append(result)

        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if not passed:
            print(f"  {result['message']}")

        return passed

    def get_results(self) -> list:
        return self.results


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        logger.warning("PyYAML not installed, using default config")
        return {
            'base_url': 'http://localhost:8000',
            'timeout': 30,
            'auth': {
                'token_url': '/api/token/',
                'refresh_url': '/api/token/refresh/',
                'username': 'test_user',
                'password': 'test_password123'
            },
            'report': {
                'output_dir': './reports',
                'html_filename': 'test_report.html'
            }
        }
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using default config")
        return {
            'base_url': 'http://localhost:8000',
            'timeout': 30,
            'auth': {
                'token_url': '/api/token/',
                'refresh_url': '/api/token/refresh/',
                'username': 'test_user',
                'password': 'test_password123'
            },
            'report': {
                'output_dir': './reports',
                'html_filename': 'test_report.html'
            }
        }
