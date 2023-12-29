from fastapi import status
import pytest
import httpx
from typing import AsyncIterator
from app.main import app
from core.utils.settings import settings
from core.helper.request_helper import send_post_request


# Account registration url
account_url: str = '/api/v1/accounts/disable/'

# Test account login credentials
test_login_credentials = {
        "password": "stringst123",
        "device_info": {
            "device_name": "Samsong s23 ultra",
            "platform": "IOS",
            "ip_address": "127.0.0.1",
            "device_model": "string",
            "device_id": "string",
            "screen_info": {
                "height": 1920,
                "width": 720,
                "resolution": 1200
            },
            "device_serial_number": "124578963",
            "is_active": True
        },
        "email": "johndoe@example.com"
    }


test_user_login_credentials = {
        "password": "stringst",
        "device_info": {
            "device_name": "Samsong s23 ultra",
            "platform": "IOS",
            "ip_address": "127.0.0.1",
            "device_model": "string",
            "device_id": "string",
            "screen_info": {
            "height": 1920,
            "width": 720,
            "resolution": 1200
            },
            "device_serial_number": "124578963",
            "is_active": True
        },
        "email": "johndoe1@example.com"
    }

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as client:
        print("client is ready")
        yield client


@pytest.mark.anyio
async def test_disable_account_failed_invalid_access_token(client: httpx.AsyncClient):
    # Header
    test_header = {
        'Authorization': f"Bearer asdasdafdakjdasjdkljlskdj",
    }

    # Request body
    test_body = {
        "account_id": "string",        
    }

    # Send request
    response = await client.post(account_url, params=test_body, headers=test_header)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_disable_account_failed_not_admin(client: httpx.AsyncClient):

    # Login for access token
    status_code, test_access_token_response = await send_post_request(url=settings.api_login_for_access_token_url, body=test_user_login_credentials)
    
    if status_code < status.HTTP_200_OK:
        access_token = test_access_token_response.get('access_token')
        
        # auth header
        test_auth_header = {
                'Authorization': f"Bearer {access_token}",
            }
        
        # Reset body
        test_reset_phone_number_body = {"account_id": "08145632147"}

        # Send request
        response = await client.post(account_url, params=test_reset_phone_number_body, headers=test_auth_header)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_disable_account_failed_invalid_account_id(client: httpx.AsyncClient):

    # Login for access token
    status_code, test_access_token_response = await send_post_request(url=settings.api_login_for_access_token_url, body=test_login_credentials)
    
    if status_code < status.HTTP_200_OK:
        access_token = test_access_token_response.get('access_token')
        
        # auth header
        test_auth_header = {
                'Authorization': f"Bearer {access_token}",
            }
        
        # Reset body
        test_reset_phone_number_body = {"account_id": "08145632147"}

        # Send request
        response = await client.post(account_url, params=test_reset_phone_number_body, headers=test_auth_header)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_disable_account_failed_account_already_disabled(client: httpx.AsyncClient):

    # Login for access token
    status_code, test_access_token_response = await send_post_request(url=settings.api_login_for_access_token_url, body=test_login_credentials)
    
    if status_code < status.HTTP_200_OK:
        access_token = test_access_token_response.get('access_token')
        
        # auth header
        test_auth_header = {
                'Authorization': f"Bearer {access_token}",
            }
        
        # Reset body
        test_body = {"account_id": "9b5d7413-e9f0-4707-8ffb-2be2a8fb1e05"}

        # Send request
        response = await client.post(account_url, params=test_body, headers=test_auth_header)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
