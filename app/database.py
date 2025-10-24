from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends

load_dotenv()
connect_args = (
    {"check_same_thread": False}
    if os.getenv("DATABASE_URL").startswith("sqlite")
    else {}
)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")

engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
