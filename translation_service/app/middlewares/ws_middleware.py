from starlette.middleware.base import BaseHTTPMiddleware
from  fastapi import Request

from app.services.error_handlers import app_error


class WSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith(("/v1/translate/ws/upload/", "/v1/translate/ws/logs/")):
            response.headers["Access-Control-Allow-Origin"] = "*"  # اجازه به همه دامنه‌ها
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, WS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response