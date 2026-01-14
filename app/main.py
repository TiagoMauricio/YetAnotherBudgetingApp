from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routes.main import api_router
from app.utils.exceptions import exceptions, handlers


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
# not sure if I like this or not
# TODO: Check in a few weeks
exception_handler_pairs = [
    (exceptions.OperationNotPermitedException, handlers.operation_not_permited_handler),
    (exceptions.EntityNotFoundException, handlers.not_found_handler),
    (exceptions.BadRequestException, handlers.bad_request_handler),
    (exceptions.UnknownException, handlers.unknown_exception_handler),
    (
        exceptions.PasswordVerificationException,
        handlers.password_verification_exception_handler,
    ),
    (
        exceptions.AuthenticationMissingException,
        handlers.authentication_missing_exception_handler,
    ),
]
for pair in exception_handler_pairs:
    app.add_exception_handler(pair[0], pair[1])
