from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import Field, EmailStr
from core.model.media_model import *
from typing import Dict, Optional, List
from datetime import datetime
from core.utils.settings import settings


class OTPAvro(AvroBaseModel):
    email: EmailStr = Field(description="An email string. This is the user's email address. It will be validated before use.", 
                            json_schema_extra={'email':'joe@example.com'},
                            examples=['johndoe@example.com'])
    purpose: str = Field(description='The purpose of the OTP')


class OTPRequestAvro(OTPAvro):
    phone_number: str = Field(description="A string. This is the user's mobile or contact number. This will be validated before use.",
                              examples=['915 1234 789'])
   

class DeviceAvroData(AvroBaseModel):
    account_email: EmailStr = Field(description="An email string. This is the user's email address. It will be validated before use.", 
                            json_schema_extra={'email':'joe@example.com'},
                            examples=['johndoe@example.com'])
    device_name: str = Field(description='A string representing the user device name', 
                             examples=['Samsong s23 ultra', 'iphone 15 pro max'])
    platform: str = Field(description='A string representing the device platform',
                          examples=['IOS', 'Android', 'Web', 'MacOS', 'Linux', 'Windows'])
    ip_address: str = Field(description='A string representing the device ipv4 address',
                            examples=['127.0.0.1'])
    device_model: str = Field(description='A string representing the device model')
    device_id: str = Field(description='A string representing the device id')
    screen_info: Dict[str, int] = Field(description='A dict containing the device screen meta data')
    device_serial_number: Optional[str] = Field(description='An optional string representing the device serial number',
                                      examples=['124578963'])
    is_active: bool = Field(description='A boolean used to track the login state of the device')


class RoleAvro(AvroBaseModel):
    name: str = Field(description="The name of the role")
    permission: List[str] = Field(description='Role permissions')


class AccountEmailUpdate(OTPAvro):
   otp: str = Field(description="verified otp")


class AccountPhoneUpdate(AccountEmailUpdate):
    phone_number: Optional[str] = Field(description='Account phone number')


class PhoneNumberVerifiedUpdateAvro(AvroBaseModel):
   phone_number: EmailStr = Field(description="This is the verified account phone number.", examples=['johndoe@example.com'])


class InvalidateOTP(AvroBaseModel):
     email: EmailStr = Field(description='Email associated with the account')
     purpose: str = Field(description='The purpose of sending the one-time-password')
     otp: str = Field(description="One-time-password")
  
  