from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.category import Category
from models.user import User
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.category_repository = CategoryRepository(session)

    def create_category(self, payload: CategoryCreate, current_user: User) -> Category:
        category = Category(owner_id=current_user.id, **payload.model_dump())
        self.category_repository.create(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def list_categories(self, current_user: User, skip: int = 0, limit: int = 100) -> list[Category]:
        return self.category_repository.list_by_owner(current_user.id, skip=skip, limit=limit)

    def get_category(self, category_id: int, current_user: User) -> Category:
        category = self.category_repository.get_by_id_and_owner(category_id, current_user.id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        return category

    def update_category(
        self,
        category_id: int,
        payload: CategoryUpdate,
        current_user: User,
    ) -> Category:
        category = self.get_category(category_id, current_user)
        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(category, field_name, field_value)
        self.category_repository.save(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete_category(self, category_id: int, current_user: User) -> None:
        category = self.get_category(category_id, current_user)
        self.category_repository.delete(category)
        self.session.commit()
