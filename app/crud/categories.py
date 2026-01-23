from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.models import Category
from app.schemas.categories import CategoryCreate
from app.utils.exceptions import exceptions as err
from collections.abc import Sequence

def get_user_accessible_categories(user, session: Session) -> Sequence[Category]:
    categories_query: SelectOfScalar[Category] = select(Category).where((Category.user_id == user.id) | (Category.is_default))
    categories : Sequence[Category] = session.exec(categories_query).all()
    return categories


def create_category(user, category_data: CategoryCreate, session: Session):
    existing_category_query = select(Category).where(
        (Category.user_id == user.id) and (Category.name == category_data.name)
    )
    existing_category = session.exec(existing_category_query).first()

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
