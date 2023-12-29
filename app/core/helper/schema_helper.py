from schema_registry.client import AsyncSchemaRegistryClient, schema
from core.utils.settings import settings


async_client = AsyncSchemaRegistryClient(url=settings.api_schema_registry_host)


async def deploy_schema(subject: str, new_schema) -> str:
    # Get all subjects from registry
    subjects = await async_client.get_subjects()
    # Check if subject already exists
    if subject not in subjects:
        avro_schema = schema.AvroSchema(new_schema)
        schema_id = await async_client.register(subject=subject, schema=avro_schema)
        return schema_id
    else:
        return
    

async def get_schema_by_id(schema_id: str):
    return await async_client.get_by_id(schema_id=schema_id)
