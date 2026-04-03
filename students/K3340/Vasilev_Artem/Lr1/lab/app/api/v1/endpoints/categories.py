from fastapi import APIRouter, Query, status

from core.dependencies import CurrentUser, DbSession
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, summary="Create category")
def create_category(
    payload: CategoryCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> CategoryRead:
    category = CategoryService(session).create_category(payload, current_user)
    return CategoryRead.model_validate(category)


@router.get("", response_model=list[CategoryRead], summary="List current user categories")
def list_categories(
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of categories to skip."),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of categories to return."),
) -> list[CategoryRead]:
    categories = CategoryService(session).list_categories(current_user, skip=skip, limit=limit)
    return [CategoryRead.model_validate(category) for category in categories]


@router.get("/{category_id}", response_model=CategoryRead, summary="Get category by id")
def get_category(category_id: int, session: DbSession, current_user: CurrentUser) -> CategoryRead:
    category = CategoryService(session).get_category(category_id, current_user)
    return CategoryRead.model_validate(category)


@router.put("/{category_id}", response_model=CategoryRead, summary="Update category")
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> CategoryRead:
    category = CategoryService(session).update_category(category_id, payload, current_user)
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete category")
def delete_category(category_id: int, session: DbSession, current_user: CurrentUser) -> None:
    CategoryService(session).delete_category(category_id, current_user)
