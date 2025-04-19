from fastapi import FastAPI
from app.core.logger import setup_logging
import logging

import uvicorn

from app.routers.rest.auth_handler import router as auth_router

setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting application...")
app = FastAPI()

routers = [
    auth_router,
]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app)
