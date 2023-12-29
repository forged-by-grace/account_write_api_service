from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import Field, EmailStr


class InvalidateCache(AvroBaseModel):
   key: str = Field(description='This is cache key')

