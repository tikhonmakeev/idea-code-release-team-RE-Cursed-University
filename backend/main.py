from fastapi import FastAPI
from app.core.logger import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting application...")
app = FastAPI()

