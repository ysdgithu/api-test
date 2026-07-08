import logging
from utils.http_client import HTTPClient, APITestCase
from utils.auth_manager import AuthManager

logger = logging.getLogger(__name__)


class TestTemplate(APITestCase):
    """
    API接口测试用例模板

    使用说明：
    1. 复制此文件并重命名为 test_<模块名>.py
    2. 修改类名为 Test<模块名>
    3. 在 run_tests 方法中添加测试用例
    4. 在 __main__ 中实例化并运行测试

    测试分类：
    - 新增接口测试：测试新开发的接口
    - 修改接口测试：测试修改后的接口
    - 回归测试：测试可能受影响的其他接口
    """

    def __init__(self, client: HTTPClient):
        super().__init__(client)
        self.auth_manager = AuthManager(
            client,
            token_url='/api/token/',
            refresh_url='/api/token/refresh/'
        )
        self.test_data = {}

    def setup(self):
        """测试前置操作：登录、创建测试数据等"""
        logger.info("Setting up test environment...")
        login_success = self.auth_manager.login('test_user', 'test_password123')
        if not login_success:
            logger.warning("Login failed, some tests may be skipped")

    def teardown(self):
        """测试后置操作：清理测试数据、登出等"""
        logger.info("Cleaning up test environment...")
        self.auth_manager.logout()

    def run_tests(self):
        """
        执行所有测试用例

        测试结构：
        1. 新增接口测试
        2. 修改接口测试
        3. 回归测试（受影响的接口）
        """
        logger.info("=" * 60)
        logger.info("Running tests for Template Module")
        logger.info("=" * 60)

        self.setup()

        self.test_new_api_endpoints()
        self.test_modified_api_endpoints()
        self.test_regression()

        self.teardown()

    def test_new_api_endpoints(self):
        """新增接口测试"""
        logger.info("\n--- Testing New API Endpoints ---")

    def test_modified_api_endpoints(self):
        """修改接口测试"""
        logger.info("\n--- Testing Modified API Endpoints ---")

    def test_regression(self):
        """回归测试：可能受影响的接口"""
        logger.info("\n--- Regression Testing ---")


if __name__ == '__main__':
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from utils.http_client import load_config

    config = load_config()
    client = HTTPClient(config['base_url'], config['timeout'])

    test = TestTemplate(client)
    test.run_tests()
