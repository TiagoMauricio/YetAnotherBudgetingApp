from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status
from app.database import get_session

from app.crud import categories as cat_crud
from app.schemas.categories import CategoryResponse
from app.utils.dependencies import get_current_user
from app.models import Category, User

from app.utils.exceptions import exceptions as err
from app.utils.dependencies import get_current_user

router: APIRouter = APIRouter(tags=["categories"])


@router.get(path="", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category(
    user: Annotated[User, Depends(dependency=get_current_user)],
    session: Session = Depends(dependency=get_session),
) -> list[Category] | None:
    try:
        categories: list[Category] = cat_crud.get_user_accessible_categories(
            user, session
        )
    except Exception as e:
        raise err.UnknownException("Something unexpected happened.")
    return categories
