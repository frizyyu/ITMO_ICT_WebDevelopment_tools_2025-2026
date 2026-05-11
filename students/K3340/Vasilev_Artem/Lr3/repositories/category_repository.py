from sqlalchemy import select
from sqlalchemy.orm import Session

from models.category import Category


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, category: Category) -> Category:
        self.session.add(category)
        self.session.flush()
        self.session.refresh(category)
        return category

    def list_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> list[Category]:
        statement = (
            select(Category)
            .where(Category.owner_id == owner_id)
            .order_by(Category.id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def get_by_id_and_owner(self, category_id: int, owner_id: int) -> Category | None:
        statement = select(Category).where(Category.id == category_id, Category.owner_id == owner_id)
        return self.session.scalar(statement)

    def save(self, category: Category) -> Category:
        self.session.add(category)
        self.session.flush()
        self.session.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.flush()
