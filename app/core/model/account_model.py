from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import HttpUrl, EmailStr, Field, model_validator, SecretStr
from core.model.role_model import Role
from core.utils.settings import settings
from core.model.device_model import Device
from typing import Optional, List
from enum import Enum


class Password(AvroBaseModel):
    password: str = Field(min_length=settings.min_password_length,
                                description=f"A minimum {settings.min_password_length} digits alphanumeric string representing the account password")
    confirm_password: str = Field(min_length=settings.min_password_length, 
                                        description=f"A minimum {settings.min_password_length} digits alphanumeric string used to confirm the account password")    
    
    # Check if passwords match
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'Password':
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords do not match')
        return self


class Account(Password):    
    email: EmailStr = Field(description="An email string. This is the user's email address. It will be validated before use.", 
                            json_schema_extra={'email':'joe@example.com'},
                            examples=['johndoe@example.com'])
    firstname: str = Field(description="A string. This is the user's first name.",
                           examples=['John'])
    lastname: str = Field(description="A string. This is the user's lastname.",
                          examples=['Doe'])
    phone_number: str = Field(description="A string. This is the user's mobile or contact number. This will be validated before use.",
                              examples=['915 1234 789'])
    country_code: str = Field(description="A string. This is the user's country code.",
                              examples=['+234'])
    country: str = Field(description="A string. This is the user's country of residence. e.g. Nigeria", 
                         examples=['Nigeria'])
    username: Optional[str] = Field('ID used to retrieve the account username')
    device: Device = Field(description='A dict used to track the device info')   
 

class CreateAccount(Account): 
    display_pics: Optional[HttpUrl] = Field(description='Account display image',)    


class AccountEmail(AvroBaseModel):
     email: EmailStr = Field(description="An email string. This is the user's email address. It will be validated before use.", 
                            json_schema_extra={'email':'joe@example.com'},
                            examples=['johndoe@example.com'])

class AccountAvroOut(Account):
    display_pics: Optional[str] = Field(description='Account display image',)  


class AccountInDB(AvroBaseModel):
    _id: str = Field(description="A unique string representing the account id",
                    json_schema_extra={'id': '7845941214687'}, alias='id')
    email: EmailStr = Field(description="An email string. This is the user's email address. It will be validated before use.", 
                            json_schema_extra={'email':'joe@example.com'},
                            examples=['johndoe@example.com'])
    firstname: str = Field(description="A string. This is the user's first name.",
                           examples=['John'])
    lastname: str = Field(description="A string. This is the user's lastname.",
                          examples=['Doe'])
    phone_number: str = Field(description="A string. This is the user's mobile or contact number. This will be validated before use.",
                              examples=['915 1234 789'])
    country_code: str = Field(description="A string. This is the user's country code.",
                              examples=['+234'])
    country: str = Field(description="A string. This is the user's country of residence. e.g. Nigeria", 
                         examples=['Nigeria'])
    username: Optional[str] = Field('ID used to retrieve the account username')
    display_pics: Optional[str] = Field(description='Account display image',)
    hashed_password: str = Field(description='Account password hashed')
    version: int = Field(description="A string. This represents the version of database schema")
    disabled: bool = Field(default=True, 
                           description="A boolean. This is used to disable a user's account")
    email_verified: bool = Field(default=False, 
                                 description="A boolean used to check the verification state of the account's email")
    phone_verified: bool = Field(default=False, 
                                 description="A boolean used to check the verification state of the user's phone number")
    is_active: bool = Field(default=False, description="A boolean used to verify the login state of the account")
    active_device_count: int = Field(description='An integer representing the number of active devices connecting to a single account')
    active_devices: List[str] = Field(description='A list showing all active account devices')
    role: Role = Field(description='Account role')

class OTP(AvroBaseModel):
    otp: str = Field(description='This is used to verify the account email')

class VerifyAccountEmail(OTP):
    email: EmailStr = Field(description="This is the account's email")

class VerifyAccountPhoneNumber(OTP):
    phone_number: str = Field(description="This is the account's phone number")

class AccountID(AvroBaseModel):
    id: str = Field(description='Id to id an account.')

class Disable_Enable_Account(AccountID):
    disabled: bool = Field(description="Flag used to enable or disable an account.")

class AccountUpdate(AvroBaseModel):
    firstname: Optional[str] = Field(default=None, description="A string. This is the user's first name.",
                           examples=['John'])
    lastname: Optional[str] = Field(default=None, description="A string. This is the user's lastname.",
                          examples=['Doe'])
    display_pics: Optional[HttpUrl] = Field(default=None, description='Account display image',)

class AccountUpdateOut(AccountUpdate):
    id: str = Field(description='ID of account to be updated.')

class UpdatePhoneNumber(AvroBaseModel):
    otp: str = Field(description="This is used to authorize the update")
    new_phone_number: str = Field(description='New phone number.')

class UpdatePhoneNumberOut(AvroBaseModel):    
    id: str = Field(description='ID of account to be updated.')
    new_phone_number: str = Field(description='New phone number.')
    firstname: str = Field(description="A string. This is the account first name.")
    email: EmailStr = Field(description="This is the account's email")

class ResetPassword(AvroBaseModel):
    current_password: str = Field(description='The current account password.')