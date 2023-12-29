from fastapi import APIRouter, Depends
from core.model.account_model import *
from core.controller.write_controller import *
from typing import Annotated
from core.model.token_model import VerifyTokenResponse
from core.model.account_model import AccountUpdate

account_write_route = APIRouter(
    prefix=f"{settings.api_prefix}accounts",
    tags=['Write Account']
)


@account_write_route.post('/forgot-password/', description='Update the account password')
async def forgot_password(account_email: AccountEmail):
    return await forgot_password_ctrl(email=account_email.email)


@account_write_route.post('/reset-password/', description='Update the account password')
async def reset_password(current_password: ResetPassword, current_account: Annotated[VerifyTokenResponse, Depends(verify_access_token)]):
    return await reset_password_ctrl(current_password=current_password, current_account=current_account)


@account_write_route.put('/update/', description="Update the account fields other than password, phone number and email.")
async def update_account(new_updates: AccountUpdate, current_account: Annotated[VerifyTokenResponse, Depends(verify_access_token)]):
    return await update_account_ctrl(current_account=current_account, updates=new_updates)


@account_write_route.post('/reset-phone_number/', description='This is used to request a phone number reset')
async def reset_phone_number(new_phone_number: str, current_account: Annotated[VerifyTokenResponse, Depends(verify_access_token)]):
    return await reset_phone_number_ctrl(current_account=current_account, phone_number=new_phone_number)


@account_write_route.put('/update/phone_number/', description='This is used to request a phone number reset')
async def update_phone_number(update: UpdatePhoneNumber, current_account: Annotated[VerifyTokenResponse, Depends(verify_access_token)]):
    return await update_phone_number_ctrl(current_account=current_account, phone_number_update=update)


@account_write_route.put('/update/password', description='Update the current password')
async def update_password(update: UpdatePasswordIn):
    return await update_password_ctrl(update=update)


@account_write_route.post('/create/', description='Create a new account')
async def create_account(new_account: CreateAccount):
    return await create_new_account_controller(new_account=new_account)


@account_write_route.delete('/delete/', description='Delete an account')
async def delete_account(current_account: Annotated[VerifyTokenResponse, Depends(verify_access_token)], account_id: str):
    return await delete_account_ctrl(current_account=current_account, id=account_id)


@account_write_route.post('/verify-email', description='Verify account email')
async def verify_account_email(verify_account: VerifyAccountEmail):
    await verify_account_email_ctrl(data=verify_account)


@account_write_route.post('/verify-phone/', description='Verify account phone number')
async def verify_account_phone_number(verify_account: VerifyAccountPhoneNumber):
    await verify_account_phone_ctrl(data=verify_account)


@account_write_route.post('/disable/', description="Allows a client or an admin to disable an account.")
async def disable_account(id: str, current_account: Annotated[VerifyTokenResponse, Depends(verify_access_token)]):
    await disable_account_ctrl(account_id=id, current_account=current_account)


@account_write_route.post('/enable/', description="Allows a client or an admin to enable a disabled an account.")
async def enable_account(id: str, current_account: Annotated[VerifyTokenResponse, Depends(verify_access_token)]):
    await enable_account_ctrl(account_id=id, current_account=current_account)