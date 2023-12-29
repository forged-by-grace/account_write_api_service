from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import Field, EmailStr


class RevokeRefreshToken(AvroBaseModel):
    email: EmailStr = Field(description='Account email.')
    refresh_token: str = Field(description='Token used to retrieve a new access token')

