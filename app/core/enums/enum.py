from enum import Enum


class Account_Event_Type(str, Enum):
     new_account_event="account_new_account"
     get_account_event="account_get"
     update_account_event="account_update"


class OTP_Event_Type(str, Enum):
     create_event="otp_create"
     get_event="otp_get"


class OTP_Purpose(str, Enum):
     email_verification='Email verification'
     phone_verification='Phone verification'
     forgot_password='Forgot password'
     reset_password='Reset password'
     transaction_verification='Transaction verification'

class Role(str, Enum):
    anonymouse='anonymouse'
    authenticated='authenticated'
    admin='admin'
     