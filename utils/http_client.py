import requests
import json
import logging
import time
from typing import Dict, Optional, Any, Tuple
from colorama import Fore, Style

logger = logging.getLogger(__name__)


class RequestResult:
    """封装一次HTTP请求的完整信息"""

    def __init__(self):
        self.method: str = ""
        self.url: str = ""
        self.request_headers: Dict[str, str] = {}
        self.request_body: Any = None
        self.status_code: int = 0
        self.response_headers: Dict[str, str] = {}
        self.response_body: Any = None
        self.elapsed_time: float = 0
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'method': self.method,
            'url': self.url,
            'request_headers': self.request_headers,
            'request_body': self.request_body,
            'status_code': self.status_code,
            'response_headers': self.response_headers,
            'response_body': self.response_body,
            'elapsed_time': self.elapsed_time,
            'error': self.error
        }


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

    def request(self, method: str, endpoint: str, **kwargs) -> Tuple[int, Dict[str, Any], float, RequestResult]:
        result = RequestResult()
        result.method = method.upper()
        result.url = f"{self.base_url}{endpoint}"
        result.request_headers = dict(self.headers)

        # 记录请求体
        if 'json' in kwargs:
            result.request_body = kwargs['json']
        elif 'data' in kwargs:
            result.request_body = kwargs['data']

        start_time = time.time()

        try:
            response = self.session.request(
                method=method.upper(),
                url=result.url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
        except requests.exceptions.RequestException as e:
            result.elapsed_time = time.time() - start_time
            result.error = str(e)
            logger.error(f"Request failed: {e}")
            return 0, {'error': str(e)}, result.elapsed_time, result

        result.elapsed_time = time.time() - start_time
        result.status_code = response.status_code
        result.response_headers = dict(response.headers)

        try:
            result.response_body = response.json()
        except ValueError:
            result.response_body = {'text': response.text}

        logger.info(f"{method.upper()} {endpoint} -> {response.status_code} ({result.elapsed_time:.2f}s)")
        return response.status_code, result.response_body, result.elapsed_time, result

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float, RequestResult]:
        return self.request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float, RequestResult]:
        return self.request('POST', endpoint, json=data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float, RequestResult]:
        return self.request('PUT', endpoint, json=data)

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict[str, Any], float, RequestResult]:
        return self.request('PATCH', endpoint, json=data)

    def delete(self, endpoint: str) -> Tuple[int, Dict[str, Any], float, RequestResult]:
        return self.request('DELETE', endpoint)


class APITestCase:
    def __init__(self, client: HTTPClient):
        self.client = client
        self.results = []

    def _make_result(self, test_name: str, status: str, check_type: str, expected: Any, actual: Any, message: str, request_result: Optional[RequestResult] = None) -> Dict:
        result = {
            'test_name': test_name,
            'status': status,
            'check_type': check_type,
            'expected': expected,
            'actual': actual,
            'message': message,
        }
        if request_result:
            result['request'] = request_result.to_dict()
        return result

    def assert_status_code(self, status_code: int, expected_code: int, test_name: str, request_result: Optional[RequestResult] = None) -> bool:
        passed = status_code == expected_code
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = self._make_result(
            test_name, status, 'status_code',
            expected_code, status_code,
            f"Expected {expected_code}, got {status_code}",
            request_result
        )
        self.results.append(result)

        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if not passed:
            print(f"  {result['message']}")

        return passed

    def assert_json_contains(self, response_json: Dict, key: str, test_name: str, request_result: Optional[RequestResult] = None) -> bool:
        passed = key in response_json
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = self._make_result(
            test_name, status, 'json_contains',
            key, 'not found',
            f"Expected key '{key}' not found in response",
            request_result
        )
        self.results.append(result)

        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if not passed:
            print(f"  {result['message']}")

        return passed

    def assert_value_equal(self, actual: Any, expected: Any, test_name: str, request_result: Optional[RequestResult] = None) -> bool:
        passed = actual == expected
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = self._make_result(
            test_name, status, 'value_equal',
            expected, actual,
            f"Expected {expected}, got {actual}",
            request_result
        )
        self.results.append(result)

        print(f"{color}[{status}]{Style.RESET_ALL} {test_name}")
        if not passed:
            print(f"  {result['message']}")

        return passed

    def assert_value_in(self, actual: Any, expected_list: list, test_name: str, request_result: Optional[RequestResult] = None) -> bool:
        passed = actual in expected_list
        status = "PASS" if passed else "FAIL"
        color = Fore.GREEN if passed else Fore.RED

        result = self._make_result(
            test_name, status, 'value_in',
            expected_list, actual,
            f"Expected {actual} in {expected_list}",
            request_result
        )
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