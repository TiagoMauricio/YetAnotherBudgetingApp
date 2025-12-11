from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.routes.main import api_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Personal Budget App",
    description="API for Yet Another Budgeting Application",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for mobile app support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Update this to restrict to your mobile app's domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Include routers
app.include_router(api_router, prefix="/api")
