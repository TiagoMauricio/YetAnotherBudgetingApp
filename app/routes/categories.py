from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status

from app.crud import categories as cat_crud
from app.database import get_session
from app.models import Category, User
from app.schemas.categories import CategoryCreate, CategoryResponse
from app.utils.dependencies import get_current_user
from app.utils.exceptions import exceptions as err
from app.utils.messages import CATEGORY_NOT_FOUND

router: APIRouter = APIRouter(tags=["categories"])


@router.get(
    path="", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK
)
async def get_category_list(
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Sequence[Category]:
    try:
        categories: Sequence[Category] = cat_crud.get_user_accessible_categories(
            user, session
        )
        return categories
    except Exception as e:
        print(e)
        raise err.UnknownException("Something unexpected happened.")


@router.get(
    path="/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_category(
    category_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Category:
    category: Category | None = cat_crud.get_category_by_id(user, session, category_id)
    if not category:
        raise err.EntityNotFoundException(CATEGORY_NOT_FOUND)
    return category


@router.post(
    path="", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CategoryCreate,
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Category:
    try:
        new_category: Category = cat_crud.create_category(user, session, category_data)
        return new_category
    except Exception as e:
        raise e


@router.patch(
    path="/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Category:
    category: Category | None = cat_crud.update_category(
        user, session, category_id, category_data
    )
    if not category:
        raise err.EntityNotFoundException(CATEGORY_NOT_FOUND)
    return category


@router.delete(path="/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> None:
    deleted_category: bool = cat_crud.delete_category(user, session, category_id)
    if not deleted_category:
        raise err.UnknownException("Something unexpected happened.")
