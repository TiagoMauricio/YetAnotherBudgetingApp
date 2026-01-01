from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.routes.main import api_router
from contextlib import asynccontextmanager
import app.utils.exceptions as err


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Pexa - Personal Expense API",
    description="A self hostable API for personal expense tracking built with FastAPI",
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


# Exception Handlers
# Need to be here, not sure if they can be put somewhere else
@app.exception_handler(err.OperationNotPermitedException)
async def operation_not_permited(
    request: Request, exc: err.OperationNotPermitedException
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"message": exc.message})


@app.exception_handler(err.EntityNotFoundException)
async def not_found_exception(
    request: Request, exc: err.EntityNotFoundException
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": exc.message})

@app.exception_handler(err.PexaBadRequestException)
async def not_found_exception(
    request: Request, exc: err.PexaBadRequestException
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"message": exc.message})
