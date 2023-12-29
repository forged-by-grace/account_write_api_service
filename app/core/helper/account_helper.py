from pydantic import EmailStr
from core.helper.request_helper import *
from fastapi import Request
from core.model.avro_model import *
from core.model.token_model import VerifyTokenResponse
from core.connection.cache_connection import redis
from core.model.otp_model import *
from core.model.cache_model import *
from core.model.revoke_token import *
from datetime import timezone
from core.utils.init_log import logger
from core.utils.error import credential_error
from core.helper.db_helper import get_account_by_email, get_account_by_id
from core.helper.encryption_helper import encrypt
from core.event.produce_event import produce_event
from core.model.invalidate_cache_model import InvalidateCache
import json


async def get_account_from_cache(id: str):
    logger.info(f'Fetching account:{id} from cache')

    # Create key
    key = f"account:{id}"

    try:
        # Get account from cache
        account_bytes = await redis.get(key.encode())
        
        if not account_bytes:
            logger.warning(f"Account:{id} not fount in cache.")
            return None
        
        logger.info(f"Account:{id} found in cache.")
        logger.info(f"Deserializing account:{id}")
        
        # Deserialize
        account_data = json.loads(s=account_bytes)

        return account_data
    except Exception as err:
        logger.error(f"Failed to retrieve account:{id} from cache due to error:{str(err)}")


async def get_account_from_cache_or_db_by_id(id: str):
    account_data = {}

    # Check if account is in Cache
    account_data: dict = await get_account_from_cache(id=id)
    
    if account_data:
        return account_data
    else:
        account_data = await get_account_by_id(id=id)
        return account_data


async def account_exists(key: str, value) -> bool:
    try:
        logger.info('Fetching account data from database.')
        account_exists = await get_account_by_email(email=value)
        if not account_exists:
            logger.info('Account not found')
            return False
        logger.info('Account found.')
        return True
    except Exception as err:
        logger.error(f"Failed to Fetch account due to error: {str(err)}")


async def is_valid_one_time_password(otp: str, email: EmailStr, purpose: str) -> dict:
    # Encrypt OTP
    encrypted_otp = encrypt(value=otp)
    
    # Retrieve the otp
    key = f"otp:{email}-{encrypted_otp}-{purpose}"
    try:  
        logger.info('fetching one time password.')
        
        # Fetch otp
        otp_exists_bytes = await redis.get(key.encode())
        
        # Check if otp does not exists
        if not otp_exists_bytes:
            return None
        
        logger.info('OTP found.')
        
        # Deserialize OTP
        otp_obj = OTPAvroIn.deserialize(data=otp_exists_bytes)

        # Check if OTP have expired
        logger.info('Checking if OTP have expired.')

        if datetime.now(timezone.utc) >= otp_obj.expires_on:
            logger.info('Expired OTP')
            return None
        
        return otp_obj
            
    except Exception as err:
        logger.error(f'Failed to validate OTP due to error {str(err)}')


async def invalidate_otp(email: EmailStr, otp: str, purpose: str):
    # Invalidate auth token
    logger.info('Invalidating OTP')

    # Encrypt auth token
    encrypted_otp = encrypt(value=otp)

    # Create key
    key = f"otp:{email}-{encrypted_otp}-{purpose.lower()}"
    
    # Create
    invalidate_token = InvalidateCache(key=key)

    # Create event
    invalidate_token_event = invalidate_token.serialize()

    # Emit auth token invalidate
    logger.info('Emitting invalidate otp event.')
    await produce_event(topic=settings.api_invalidate_cache_topic, value=invalidate_token_event)
     

async def is_valid_auth_token(auth_token: str, email: EmailStr) -> dict:
    # request body
    body = {
        'email': email,
        'auth_token': auth_token
    }

    # headers
    headers = {
        'content-type': 'application/json'
    }

    # Send post request
    status_code, response = await send_post_request(
        url=settings.api_verify_auth_token_url, 
        body=body, 
        headers=headers
    )

    print(response)
    # Check response status
    if status_code >= 400:
        return False
    
    return True


async def verify_token(url: str, request: Request):
    # Get access token from request
    logger.info('Checking if header has authorization token')
    token_data = request.headers.get('Authorization')
    if not token_data:
        raise credential_error
    
    # Extract data
    token_type = token_data.split()[0]
    token = token_data.split()[1]

    # Check if token type is Bearer
    logger.info('Checking if token type is Bearer.')
    if not token_type or token_type != 'Bearer':
        raise credential_error
    
    # Check if access token was provided
    logger.info('Checking authorization token was found.')
    if not token:
        raise credential_error
    
    # Create request header
    headers = {
        'Authorization': f"Bearer {token}",
        'content-type': 'appication/json'
    }
    
    # Get response
    logger.info('Sending verify access token request to authorization server.')
    status_code, response = await send_get_request(url=url, headers=headers)

    if status_code >= 400:
        logger.warning(f'Failed to verify authorization token due to error: {str(response)}')
    
    logger.info('Token is valid.')
    return status_code, response, token
    

async def verify_access_token(request: Request):
   # Send request
    status_code, response, token = await verify_token(url=settings.api_verify_access_token_url, request=request)

    # Check status code
    if status_code >= 400:
        raise credential_error
    
    # Create obj
    token_data = VerifyTokenResponse(**response)

    return token_data

  
async def get_otp(otp: str, email: EmailStr, purpose: str) -> bool:
    try:
        # Create key
        # key = "field:{account_email}-{one-time_password}-{otp-purpose}"
        key = f"otp:{email}-{otp}-{purpose}"

        # Get cache 
        otp_byte = await redis.get(key.encode())

        if not otp_byte:
            return None

        # Deserialize cache byte
        otp_deserialized = OTPAvroIn.deserialize(data=otp_byte)
        return otp_deserialized.model_dump()
    except Exception as err:
        logger.error(f"Failed to validate OTP due to error: {str(err)}")


def otp_has_expired(data) -> bool:
    expiry = data.get('expires_on')
    now = datetime.now(timezone.utc)
    return now > expiry
      
