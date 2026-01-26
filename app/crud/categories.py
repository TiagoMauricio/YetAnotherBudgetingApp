from collections.abc import Sequence

from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.models import Category, User
from app.schemas.categories import CategoryCreate
from app.utils.exceptions import exceptions as err
from app.utils.messages import CATEGORY_NOT_FOUND


def _user_category_exists(
    user: User, session: Session, category_data: CategoryCreate
) -> Category | None:
    existing_category_query = select(Category).where(
        (Category.user_id == user.id), (Category.name == category_data.name)
    )
    existing_category: Category | None = session.exec(existing_category_query).first()
    return existing_category


def get_user_accessible_categories(user: User, session: Session) -> Sequence[Category]:
    categories_query: SelectOfScalar[Category] = select(Category).where(
        (Category.user_id == user.id) | (Category.is_default)
    )
    categories: Sequence[Category] = session.exec(categories_query).all()
    return categories


def get_category_by_id(
    user: User, session: Session, category_id: int
) -> Category | None:
    try:
        category: Category | None = session.get(Category, category_id)
        if not category:
            raise err.EntityNotFoundException(CATEGORY_NOT_FOUND)
        if category.user_id and category.user_id != user.id:
            raise err.NotPermitedException(
                f"User {user.id} tried to access Category {category_id}"
            )
        return category
    except err.NotPermitedException as e:
        # return this instead so user doesn't know
        # if the Cat actually exists or not
        print(e.message)
        return None


def create_category(user: User, session: Session, category_data: CategoryCreate):
    existing_category: Category | None = _user_category_exists(
        user, session, category_data
    )

    if existing_category:
        raise err.DuplicateEntityException(
            f"Category {category_data.name} already exists"
        )

    new_category = Category(
        name=category_data.name,
        is_expense=category_data.is_expense,
        description=category_data.description,
        user_id=user.id,
        is_default=False,
    )

    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category


def update_category(
    user: User, session: Session, category_id: int, category_data: CategoryCreate
) -> Category | None:
    try:
        category: Category | None = session.get(Category, category_id)
        if not category:
            raise err.EntityNotFoundException(CATEGORY_NOT_FOUND)
        if category.user_id != user.id or category.is_default:
            raise err.NotPermitedException(
                f"User {user.id} tried to update Category {category_id}"
            )

        existing_category: Category | None = _user_category_exists(
            user, session, category_data
        )

        if existing_category:
            raise err.DuplicateEntityException(
                f"Category {category_data.name} already exists"
            )
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    except err.NotPermitedException as e:
        print(e.message)
        return None


def delete_category(user: User, session: Session, category_id: int) -> bool:
    category: Category | None = get_category_by_id(user, session, category_id)
    if not category:
        raise err.EntityNotFoundException(CATEGORY_NOT_FOUND)
    if category.is_default:
        raise err.NotPermitedException("You can't delete a default category.")
    session.delete(category)
    session.commit()
    return True
