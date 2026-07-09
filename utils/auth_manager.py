import logging
import requests
from typing import Dict, Optional
from .http_client import HTTPClient

logger = logging.getLogger(__name__)


class AuthManager:
    def __init__(self, client: HTTPClient, token_url: str, refresh_url: str = None):
        self.client = client
        self.token_url = token_url
        self.refresh_url = refresh_url
        self.access_token = None
        self.refresh_token = None

    def login(self, username: str, password: str) -> bool:
        try:
            data = {'username': username, 'password': password}
            status_code, response, *_ = self.client.post(self.token_url, data)

            if status_code == 200 and 'access' in response:
                self.access_token = response['access']
                self.refresh_token = response.get('refresh')
                self.client.set_auth_token(self.access_token)
                logger.info("Login successful")
                return True
            else:
                logger.error(f"Login failed: {response}")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def login_with_basic_auth(self, username: str, password: str) -> bool:
        try:
            self.client.set_custom_header(
                'Authorization',
                f'Basic {requests.auth._basic_auth_str(username, password)}'
            )
            logger.info("Basic auth set")
            return True
        except Exception as e:
            logger.error(f"Basic auth error: {e}")
            return False

    def refresh_token(self) -> bool:
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False

        try:
            data = {'refresh': self.refresh_token}
            status_code, response, *_ = self.client.post(self.refresh_url, data)

            if status_code == 200 and 'access' in response:
                self.access_token = response['access']
                self.client.set_auth_token(self.access_token)
                logger.info("Token refreshed successfully")
                return True
            else:
                logger.error(f"Token refresh failed: {response}")
                return False
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False

    def logout(self):
        self.access_token = None
        self.refresh_token = None
        self.client.remove_auth_token()
        logger.info("Logged out")

    def get_access_token(self) -> Optional[str]:
        return self.access_token

    def is_authenticated(self) -> bool:
        return self.access_token is not None

    @staticmethod
    def create_test_user(client: HTTPClient, register_url: str, username: str, password: str, email: str = None):
        try:
            data = {'username': username, 'password': password}
            if email:
                data['email'] = email
            status_code, response, *_ = client.post(register_url, data)
            if status_code in [200, 201]:
                logger.info(f"Test user '{username}' created successfully")
                return True
            else:
                logger.info(f"User may already exist: {response}")
                return True
        except Exception as e:
            logger.warning(f"Failed to create test user: {e}")
            return False
