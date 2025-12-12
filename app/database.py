from sqlmodel import create_engine, Session, SQLModel
from typing import Annotated
from fastapi import Depends
from app.config import settings

connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
DATABASE_URL = settings.database_url

engine = create_engine(url=DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
