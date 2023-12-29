from core.model.account_model import *
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from core.helper.password_helper import verify_password
from core.event.produce_event import *
from core.helper.account_helper import *
from core.model.update_request_model import *

from core.model.avro_model import *
from core.model.otp_model import *
from core.model.revoke_token import *
from core.model.invalidate_cache_model import *
from core.utils.init_log import logger
from core.helper.otp_helper import is_valid_otp
from core.helper.encryption_helper import encrypt
from core.helper.db_helper import *
from core.helper.get_account_helper import get_account


async def create_new_account_controller(new_account: CreateAccount) -> None:
    # check if password is alphanumeric
    logger.info('Checking if password is alphanumeric')
    if not new_account.password.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Password must be an alphanumeric string.'
        )
    
    # Check if account exists
    logging.info('Validating email address')
    account_found = await account_exists(key='email', value=new_account.email)
    if account_found:
        logging.warning('Account registration failed because email already exist')
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account with email:{new_account.email} already exists"
        )
    
    # Convert to dict
    account_dict = new_account.model_dump()
    
    # Convert Uri to str
    account_dict.update({'display_pics': str(new_account.display_pics)})
    
    # Create new account obj
    account_obj = AccountAvroOut(**account_dict)

    # Serialize
    new_account_event = account_obj.serialize()

    # Emit event
    logging.info('Emitting create account event...')
    await produce_event(topic=settings.api_create_account_topic, value=new_account_event)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f"Account with email:{new_account.email} is being created."
    )


async def forgot_password_ctrl(email: EmailStr):
    # Check if account exists
    account_found = await get_account_by_email(email=email)
    if not account_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with email:{email} does not exist"
        )
    
    # Create otp obj
    otp_obj = OTPAvroOut(
        purpose=OTP_Purpose.forgot_password.value.lower(),
        firstname=account_found.firstname,
        email=email,
        phone_number=account_found.phone_number
    )

    # Serialize
    otp_event = otp_obj.serialize()

    # Emit event
    logger.info('Emitting otp event.')
    await produce_event(topic=settings.api_otp_topic, value=otp_event)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'One-time-password was sent to {email} for authorization.'
    )


async def reset_password_ctrl(current_password, current_account: VerifyTokenResponse):
    # Fetch account
    account_data = await get_account(id=current_account.id)

    # Check if current passoword is valid
    logger.info('Verifying password.')
    valid_password = verify_password(hashed_password=account_data.get('hashed_password'), plain_password=current_password.current_password)
    if not valid_password:
        logger.warning('Password verification failed.')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Create otp obj
    otp_obj = OTPAvroOut(
        purpose=OTP_Purpose.reset_password.value.lower(),
        firstname=account_data.get('firstname'),
        email=account_data.get('email'),
        phone_number=account_data.get('phone_number')
    )

    # Serialize
    otp_event = otp_obj.serialize()

    # Emit event
    logger.info('Emitting otp event.')
    await produce_event(topic=settings.api_otp_topic, value=otp_event)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f'One-time-password was sent to {current_account.email} for authorization.'
    )
    

async def update_password_ctrl(update: UpdatePasswordIn) -> None:
    # Validate update token
    logger.info('Validating auth token.')
    valid_token = await is_valid_auth_token(auth_token=update.auth_token, email=update.email)
    if not valid_token:
        logger.error('Invalid auth token')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid auth token'
        )
    
    # Create new password update obj
    password_obj = UpdatePasswordOut(
        email=update.email,
        password=update.password,
    )

    # Serialize
    password_update_event = password_obj.serialize()
    
    # Produce password update event
    logger.info('Emitting account password event.')
    await produce_event(topic=settings.api_update_password_topic, value=password_update_event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content='Password update in progress'
    )


async def delete_account_ctrl(id: str, current_account: VerifyTokenResponse) -> None:
    # Check if account belongs to admin
    logger.info("Checking if client is admin.")
    if not current_account.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Reserved for admins only.'
        )
    
    # Check if account exists
    logger.info("Checking if account exists.")
    account_exists = await get_account_from_cache_or_db_by_id(id=id)
    if not account_exists:
        logger.warning('Account not found due to invalid account id.')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid account id."
        )
    
    # Create objs
    delete_obj = AccountID(id=id)

    # Serialize
    delete_event = delete_obj.serialize()

    # produce delete account event
    logger.info(f'Emitting delete account:{id} event.')
    await produce_event(topic=settings.api_delete_account_topic, value=delete_event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content='Account deletion in progress'
    )


async def disable_account_ctrl(account_id: str, current_account):
    # Check if account belongs to admin
    logger.info(f'Checking if account:{current_account.id} has admin role. or account belongs to the client.')
   
    if current_account.id != account_id and not current_account.admin:
        logger.info(f'Account:{current_account.id} is not an admin and does not belong to the current client')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be an admin or the owner of the account'
        )
    
    # Validate account id
    logger.info('Validating account id.')
    account_data = await get_account_from_cache_or_db_by_id(id=account_id)
    if not account_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account does not exist"
        )
    
    # Check if account is already disabled
    logger.info('Checking if account is already diabled.')
    if account_data.get('disabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already disabled"
        )
    
    # Disable account
    logger.info(f'Disabling account: {account_id}')
    disable_account_obj = Disable_Enable_Account(
        id=account_id, 
        disabled=True
    )

    # Serialize
    disable_account_event = disable_account_obj.serialize()
    await produce_event(topic=settings.api_disable_enable_account_topic, value=disable_account_event)
  
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Disabling account"
    )


async def enable_account_ctrl(account_id: str, current_account):
    # Check if account belongs to client or admin
    logger.info(f'Checking if account:{current_account.id} has admin role. or account belongs to the client.')
    if not current_account.admin:
        logger.info(f'Account:{current_account.id} is not an admin and does not belong to the current client')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Reserved for admins only.'
        )
    
    # Validate account id
    logger.info('Validating account id')
    account_data = await get_account_from_cache_or_db_by_id(id=account_id)
    if not account_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid account ID"
        )
    
    # Check if account is already enabled
    logger.info('Checking if account is already enabled.')
    if not account_data.get('disabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already enabled"
        )
    
     # Enable account
    logger.info(f'Enabling account: {account_id}')
    enable_account_obj = Disable_Enable_Account(
        id=account_id,
        disabled=False
    )

    # Serialize
    enable_account_event = enable_account_obj.serialize()
    await produce_event(topic=settings.api_disable_enable_account_topic, value=enable_account_event)
  
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Enabling account."
    )


async def verify_account_email_ctrl(data: VerifyAccountEmail):
    # Validate email
    logger.info('Validating email.')
    valid_email = await get_account_by_email(email=data.email)
    if not valid_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid email.'
        )
    
    # Validate OTP
    logger.info(f'Validating OTP')
    valid_otp = await is_valid_otp(otp=data.otp, email_or_phone_number=data.email, purpose=OTP_Purpose.email_verification.value)
    
    # Check if OTP is valid
    if not valid_otp:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid OTP'
            )
    
    logger.info(f'OTP found.')
    
    # Encrypt OTP
    encrypted_otp = encrypt(value=data.otp)

    # Create an account update obj
    account_update_obj = AccountEmailUpdate(email=data.email, otp=encrypted_otp, purpose=OTP_Purpose.email_verification)

    # Serialize
    account_update_event = account_update_obj.serialize()

    # Emit event
    logger.info(f'Emitting email verification event.')
    await produce_event(topic=settings.api_email_verified_topic, value=account_update_event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"msg": 'Email verified successfully'}
    )


async def verify_account_phone_ctrl(data: VerifyAccountPhoneNumber):
    # Validate phone number
    logger.info('Validating phone number.')
    valid_phone_number = await get_account_by_phone_number(phone_number=data.phone_number)
    if not valid_phone_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid phone number.'
        )
    
    logger.info('Validating OTP')
    # Validating OTP
    valid_otp = is_valid_otp(otp=data.otp, email_or_phone_number=data.phone_number, purpose=OTP_Purpose.phone_verification.value)
    
    # Check if otp is valid
    if not valid_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid OTP'
        )
    
    logger.info('Encrypting OTP')
    
    # Encrypt OTP
    encrypted_otp = encrypt(value=data.otp)
    
    # Create an account update obj
    account_update_obj = AccountPhoneUpdate(email=valid_phone_number.get('email'), otp=encrypted_otp, purpose=OTP_Purpose.phone_verification.value, phone_number=data.phone_number)

    # Serialize
    account_update_event = account_update_obj.serialize()

    # Emit event
    logger.info(f'Emitting phone number verification event.')
    await produce_event(topic=settings.api_phone_number_verified_topic, value=account_update_event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content='Phone number verified successfully'
    )


async def update_account_ctrl(current_account, updates: AccountUpdate) -> None:
    # deserialize update
    update_dict = updates.to_dict()

    # Add id to update dict
    update_dict.update({'id': current_account.id})

    # create update out obj
    update_out_obj = AccountUpdateOut(**update_dict)

    # Serialize
    update_request_event = update_out_obj.serialize()

    # Emit update request event
    await produce_event(topic=settings.api_account_update_request, value=update_request_event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Account update in progress."
    )


async def reset_phone_number_ctrl(current_account, phone_number: str):
    # Create reset phone number obj
    reset_phone_number = UpdatePhoneNumberOut(
        id=current_account.id,
        new_phone_number=phone_number,
        email=current_account.email,
        firstname=current_account.firstname
    )

    # Serialize
    reset_phone_number_event = reset_phone_number.serialize()

    # Emit reset event
    logger.info('Emitting phone number update event.')
    await produce_event(topic=settings.api_reset_phone_number, value=reset_phone_number_event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="OTP sent to email for authorization."
    )

async def update_phone_number_ctrl(current_account, phone_number_update: UpdatePhoneNumber):
    # Validate auth token
    logger.info('Validating OTP.')
    valid_otp = await is_valid_one_time_password(
        otp=phone_number_update.otp, 
        email=current_account.email, 
        purpose=OTP_Purpose.phone_verification.value.lower()
    )

    if not valid_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid OTP.'
        )
    
    # Validate phone number
    valid_phone_number = valid_otp.phone_number == phone_number_update.new_phone_number
    if not valid_phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is different from the validated phone number."
        )
    
    # Invalidate OTP
    await invalidate_otp(otp=phone_number_update.otp, email=current_account.email, purpose=OTP_Purpose.phone_verification.value.lower())
    
    # Create update phone number obj
    update_phone_number = UpdatePhoneNumberOut(
        id=current_account.id,
        firstname=current_account.firstname,
        email=current_account.email,
        new_phone_number=phone_number_update.new_phone_number
    )

    # Serialize
    update_phone_number_event = update_phone_number.serialize()

    # Emit reset event
    logger.info('Emitting phone number update event.')
    await produce_event(topic=settings.api_update_phone_number, value=update_phone_number_event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Phone number update in progress."
    )