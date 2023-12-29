from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import HttpUrl, EmailStr, Field, model_validator, SecretStr

class Role(AvroBaseModel):
    name: str
    permissions: list[str] = []