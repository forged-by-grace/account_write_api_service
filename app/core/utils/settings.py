from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, HttpUrl
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.abspath('.env'), env_file_encoding='utf-8')
    
    # API meta info
    api_name: str
    api_version: str
    api_description: str
    api_terms_of_service: str
    api_company_name: str
    api_prefix: str
    api_company_url: HttpUrl
    api_company_email: EmailStr

    # ACCOUNT API info
    api_entry_point: str
    api_port: int
    api_reload: bool
    api_host: str
    api_lifespan: str

    # Cache credentials    
    api_redis_host: str
    api_redis_port: int
    api_redis_password: str
    api_redis_decode_response: bool
    api_redis_host_local: str

    # API constants
    min_password_length: int
    password_regex: str
    max_otp_length: int

    # API model versions
    account_model_version: int

    # Schema Registry Server 
    api_schema_registry_host: str

    # Event Streaming Server
    api_event_streaming_host: str
    api_event_streaming_client_id: str
    api_otp_schema_subject: str
    api_account_schema_subject: str

    # Streaming topics    
    api_phone_number_verified_topic: str
    api_email_verified_topic: str
    api_invalidate_cache_topic: str
    api_create_account_topic: str
    api_otp_topic: str
    api_update_password_topic: str
    api_cache_topic: str
    api_revoke_refresh_token_topic: str
    api_delete_account_topic: str
    api_disable_enable_account_topic: str
    api_account_update_request: str
    api_reset_phone_number: str
    api_update_phone_number: str
    api_invalidate_cache_topic: str
    
    # DB credentials
    api_db_url: str

    # API Externa Url
    api_verify_auth_token_url: str
    api_verify_access_token_url: str
    api_verify_otp_url: str
    api_login_for_access_token_url: str
    
settings = Settings()
