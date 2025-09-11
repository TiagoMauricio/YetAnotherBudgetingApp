from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.database import create_db_and_tables
from app.routes import auth, user, account, category, entry
from app.utils import error_handlers
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Personal Budget App",
    description="API for Yet Another Budgeting Application",
    version="1.0.0",
    lifespan=lifespan
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
