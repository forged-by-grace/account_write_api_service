from fastapi import status
import pytest
import httpx
from typing import AsyncIterator
from unittest.mock import patch
from app.main import app

# Account registration url
account_reg_url: str = '/api/v1/accounts/create/'

# Test account
test_account_1 = {
            "password": "stringst",
            "confirm_password": "stringst",
            "email": "johndoe@example.com",
            "firstname": "John",
            "lastname": "Doe",
            "phone_number": "915 1234 789",
            "country_code": "+234",
            "country": "Nigeria",
            "username": "ID used to retrieve the account username",
            "device": {
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
            "display_pics": "https://example.com/"
        }

test_account_2 = {
            "password": "stringst",
            "confirm_password": "stringst1",
            "email": "johndoe@example.com",
            "firstname": "John",
            "lastname": "Doe",
            "phone_number": "915 1234 789",
            "country_code": "+234",
            "country": "Nigeria",
            "username": "ID used to retrieve the account username",
            "device": {
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
            "display_pics": "https://example.com/"
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
async def test_failed_registration_account_exists(client: httpx.AsyncClient):
       
    # Send request
    response = await client.post(account_reg_url, json=test_account_1)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json().get('detail') == f"Account with email:{test_account_1.get('email')} already exists"


@pytest.mark.anyio
async def test_failed_registration_mismatch_password_and_confirm_password(client: httpx.AsyncClient):
     # Send request
    response = await client.post(account_reg_url, json=test_account_2)

    assert test_account_2.get('password') != test_account_2.get('confirm_password')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



