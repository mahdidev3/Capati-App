from fastapi import APIRouter
from .endpoints import auth, dashboard, account, wallet, translate

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(account.router, tags=["Account"])
api_router.include_router(wallet.router, tags=["Wallet"])
api_router.include_router(translate.router, tags=["Translate"])
