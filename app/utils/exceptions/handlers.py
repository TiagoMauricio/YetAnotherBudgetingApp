from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.exceptions import exceptions as err


async def operation_not_permited_handler(
    request: Request, exc: err.NotPermitedException
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"message": exc.message})


async def not_found_handler(
    request: Request, exc: err.EntityNotFoundException
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": exc.message})


async def bad_request_handler(
    request: Request, exc: err.BadRequestException
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"message": exc.message})


async def unknown_exception_handler(
    request: Request, exc: err.UnknownException
) -> JSONResponse:
    return JSONResponse(status_code=500, content={"message": exc.message})


async def password_verification_exception_handler(
    request: Request, exc: err.PasswordVerificationException
) -> JSONResponse:
    return JSONResponse(status_code=500, content={"message": exc.message})


async def authentication_missing_exception_handler(
    request: Request, exc: err.AuthenticationMissingException
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"message": exc.message})
