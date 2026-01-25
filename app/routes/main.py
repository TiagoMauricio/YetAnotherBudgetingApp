from fastapi import APIRouter

from app.routes import users
from app.routes import accounts
from app.routes import auth
from app.routes import transactions
from app.routes import categories

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
