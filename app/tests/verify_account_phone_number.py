from fastapi import status
import pytest
import httpx
from typing import AsyncIterator
from app.main import app
from core.utils.settings import settings
from core.helper.request_helper import send_post_request


# Account registration url
account_url: str = '/api/v1/accounts/verify-phone/'


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as client:
        print("client is ready")
        yield client


@pytest.mark.anyio
async def test_phone_verification_failed_invalid_phone(client: httpx.AsyncClient):
        # Reset body
        test_body = {
                    "otp": "string",
                    "phone_number": "user@example.com"
                }

        # Send request
        response = await client.post(account_url, json=test_body)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_phone_verification_failed_invalid_otp(client: httpx.AsyncClient):
        # Reset body
        test_body = {
                    "otp": "string",
                    "phone_number": "user@example.com"
                }

        # Send request
        response = await client.post(account_url, json=test_body)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

