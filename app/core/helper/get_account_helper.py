from core.helper.cache_helper import get_account_from_cache
from core.helper.encryption_helper import encrypt
from core.helper.db_helper import get_account_by_id


async def get_account(id: str):
    account_data = {}

    # Check if account is in Cache

    account_data: dict = await get_account_from_cache(id=id)
    
    if account_data:
        return account_data       
    else:
        return await get_account_by_id(id=id)

