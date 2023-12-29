import time
from fastapi import Request
import logging
from fastapi.responses import StreamingResponse


# Initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
logger = logging.getLogger("Account Write API")

async def log_req_info():
    print('am cool')
    logging.info(' logging request')


async def add_process_time_header(request: Request, call_next):
    # Before request processing
    start_time = time.time()
    response = await call_next(request)
 
    # After the request processing
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response