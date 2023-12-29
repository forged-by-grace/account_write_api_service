from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import Field, EmailStr
from core.model.account_model import Password


class UpdatePasswordIn(Password):
    email: EmailStr = Field(description='An email string used to identify an account')
    auth_token: str = Field(description='A string representing the authorization token')


class UpdatePasswordOut(AvroBaseModel):
    email: EmailStr = Field(description='An email string used to identify an account')
    password: str = Field(description='A string representing the account password')

