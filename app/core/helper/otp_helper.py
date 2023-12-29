from core.connection.cache_connection import redis
from pydantic import EmailStr
from core.utils.init_log import logger
from core.helper.encryption_helper import encrypt
from fastapi import HTTPException, status
from core.model.otp_model import OTPAvroIn
from datetime import datetime, timezone


async def is_valid_otp(otp: str, email_or_phone_number: str, purpose: str):
    try:
        # Encrypt otp
        encrypted_otp = encrypt(value=otp)

        # Create key
        key = f"otp:{email_or_phone_number}-{encrypted_otp}-{purpose}"

        # Fetch OTP
        otp_bytes = await redis.get(key.encode())

        # Check if otp was found
        if not otp_bytes:
            return False
        
        logger.info('OTP found.')
        logger.info('Deserializing OTP')

        # Deserialize OTP
        deserialized_otp = OTPAvroIn.deserialize(data=otp_bytes)

        # Check if OTP have expired
        logger.info('Checking if OTP have expired.')
        if  datetime.now(timezone.utc) >= deserialized_otp.expires_on:
            logger.info('Expired OTP')
            return False
        
        return True
    except Exception as err:
        logger.error(f"Failed to retrieve OTP due to error: {str(err)}")
    finally:
        await redis.close()