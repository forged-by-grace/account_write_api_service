from fastapi import status
import pytest
import httpx
from typing import AsyncIterator
from app.main import app
from core.utils.settings import settings
from typing import Dict

# Account registration url
account_url: str = '/api/v1/accounts/forgot-password/'


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as client:
        print("client is ready")
        yield client


@pytest.mark.anyio
async def test_failed_forgot_password_account_not_found(client: httpx.AsyncClient):
    # Account email
    fake_account_email: Dict[str, str] = {"email": "user@example.com"}

    # Send request
    response = await client.post(account_url, json=fake_account_email)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_successful_forgot_password(client: httpx.AsyncClient):
    # Account email
    test_account_email: Dict[str, str] = {"email": "johndoe@example.com"}

    # Send request
    response = await client.post(account_url, json=test_account_email)

    assert response.status_code == status.HTTP_200_OK





