from core.model.token_model import *
from core.connection.cache_connection import redis
from core.utils.init_log import logger
import json


async def get_account_from_cache(id: str):
    logger.info(f'Fetching account:{id} from cache')

    # Create key
    key = f"account:{id}"

    try:
        # Get account from cache
        account_bytes = await redis.get(key.encode())
        
        if not account_bytes:
            logger.warning(f"Account:{id} not fount in cache.")
            return None
        
        logger.info(f"Account:{id} found in cache.")
        logger.info(f"Deserializing account:{id}")
        
        # Deserialize
        account_data = json.loads(s=account_bytes)

        return account_data
    except Exception as err:
        logger.error(f"Failed to retrieve account:{id} from cache due to error:{str(err)}")
