from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select

from app.config import settings
from app.models import Category

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
DATABASE_URL = settings.database_url

DEFAULT_CATEGORIES = [
    ("Salary", False),
    ("Dividends", False),
    ("Groceries", True),
    ("Health", True),
    ("Housing", True),
    ("Pets", True),
    ("Car", True),
]

engine = create_engine(url=DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        print("Checking database for Categories...")
        for c in DEFAULT_CATEGORIES:
            print("Checking: ", c)
            statement = select(Category).where(
                Category.name == c[0], Category.is_default
            )
            existing = session.exec(statement).first()

            if not existing:
                print("Creating missing category: ", c)
                new_category = Category(name=c[0], is_default=True, is_expense=c[1])
                session.add(new_category)

        session.commit()


def get_session():
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
