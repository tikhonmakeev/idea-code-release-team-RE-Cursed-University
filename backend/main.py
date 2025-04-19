from fastapi import FastAPI
from app.core.logger import setup_logging
import logging

from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from app.routers.rest.auth_handler import router as auth_router
from app.routers.rest.message_handler import router as message_router

setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting application...")
app = FastAPI()

routers = [
    auth_router,
    message_router,
]

for router in routers:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app)
