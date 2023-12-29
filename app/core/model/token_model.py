from pydantic import EmailStr, Field
from datetime import datetime
from dataclasses_avroschema.pydantic import AvroBaseModel


class VerifyTokenResponse(AvroBaseModel):
    iss: str = Field(description='Company issueing the token')
    aud: str = Field(description='The clients')
    sub: str = Field(description='The subject of the token')
    firstname: str = Field(description='The firstname of the client.')
    lastname: str  = Field(description='The lastname of the client.')
    email: EmailStr = Field(description='Email of the client.')
    id: str = Field(description='Unique client ID')
    admin: bool = Field(description='Checks if client is an admin')
    iat: datetime = Field(description='Timestamp token was issued')
    exp: datetime = Field(description='Token expiration timestamp')
    