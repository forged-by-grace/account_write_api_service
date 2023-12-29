from core.utils.settings import settings
from schema_registry.client import AsyncSchemaRegistryClient, schema


async def get_schema_from_schema_registry(schema_registry_subject: str):
    # Connect to the schema registry
    asr =  AsyncSchemaRegistryClient(url=settings.api_schema_registry_host)
    # Get latest schema version
    latest_version = await asr.get_schema(subject=f"{schema_registry_subject}-value") 
    return asr, latest_version


async def register_schema(schema_registry_subject: str, new_schema: str):
    # Connect to the schema registry
    asr = AsyncSchemaRegistryClient(url=settings.api_schema_registry_host)
    # Convert to avro schema
    avro_schema = schema.AvroSchema(new_schema)
    # Register schema
    schema_id = await asr.register(subject=schema_registry_subject, schema=avro_schema)
    return schema_id


async def update_schema(schema_registry_subject: str, new_schema: str):
    # Connect to the schema registry
    asr = AsyncSchemaRegistryClient(url=settings.api_schema_registry_host)
    # Delete previous schema
    await asr.delete_subject(subject=schema_registry_subject)
    # Register new schema
    schema_id = await register_schema(schema_registry_subject=schema_registry_subject, new_schema=new_schema)
    return schema_id