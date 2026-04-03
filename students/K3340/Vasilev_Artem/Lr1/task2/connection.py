from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "postgresql://postgres:1@localhost:5432/task2_db"

engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session