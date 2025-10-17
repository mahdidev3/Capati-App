from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.middlewares.ws_middleware import WSMiddleware
from app.services.error_handlers import (
    validation_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

# ایجاد جداول دیتابیس در صورت عدم وجود
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Translation Service API",
    description="API for a video Capati service platform.",
    version="1.0.0"
)

# تنظیمات CORS برای اتصال از فرانت‌اند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # آدرس فرانت‌اند خود را اینجا قرار دهید
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(WSMiddleware)

app.include_router(api_router, prefix="/v1")

# Register global exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Capati Service API. Go to /docs for documentation."}
