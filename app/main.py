from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.routes import auth, user, account, category, entry
from app.utils.global_base_categories import ensure_global_base_categories
from app.utils import error_handlers
from app.models.user import User
from app.utils.security import get_current_active_user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Budget App",
    description="API for Yet Another Budgeting Application",
    version="1.0.0"
)

# CORS middleware for mobile app support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to restrict to your mobile app's domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom error handlers for consistent JSON errors
app.add_exception_handler(RequestValidationError, error_handlers.validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, error_handlers.http_exception_handler)
app.add_exception_handler(Exception, error_handlers.generic_exception_handler)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def create_global_base_categories():
    db = SessionLocal()
    try:
        ensure_global_base_categories(db)
    finally:
        db.close()

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/users", tags=["users"])
app.include_router(account.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(category.router, prefix="/api/categories", tags=["categories"])
app.include_router(entry.router, prefix="/api/entries", tags=["entries"])
