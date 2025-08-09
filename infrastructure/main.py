import logging

import uvicorn
from fastapi import FastAPI

from infrastructure.lifespan_manager import lifespan
from infrastructure.configuration.log_config import LOGGING_CONFIG
from app.core.middleware.middleware import configure_middleware
from app.core.exception.global_exception_handler import CustomExceptionHandler
from infrastructure.routes.api_router import router

logging.config.dictConfig(LOGGING_CONFIG)
# Silence boto3/botocore/s3transfer debug logs
for noisy_logger in ['boto3', 'botocore', 's3transfer', 'urllib3',"multipart"]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

# Also silence Starlette's multipart parser (used by FastAPI)
logging.getLogger("multipart.multipart").setLevel(logging.ERROR)
app = FastAPI(
    title="API Documentation",
    description="Amin-Travels-Hajj Core Service",
    version="0.1.0",
    lifespan=lifespan
)

# Configure middleware
configure_middleware(app)

# Exception handler
exception_handler = CustomExceptionHandler(app)
app.add_exception_handler(Exception, exception_handler)

# Routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7700, workers=1)
