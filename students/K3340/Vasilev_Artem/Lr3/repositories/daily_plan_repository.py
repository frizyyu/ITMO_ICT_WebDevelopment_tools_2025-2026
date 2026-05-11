from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.daily_plan import DailyPlan
from models.daily_plan_task import DailyPlanTask


class DailyPlanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, plan: DailyPlan) -> DailyPlan:
        self.session.add(plan)
        self.session.flush()
        self.session.refresh(plan)
        return plan

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[DailyPlan]:
        statement = (
            select(DailyPlan)
            .where(DailyPlan.user_id == user_id)
            .order_by(DailyPlan.plan_date.desc(), DailyPlan.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def get_by_id_and_user(self, plan_id: int, user_id: int) -> DailyPlan | None:
        statement = select(DailyPlan).where(DailyPlan.id == plan_id, DailyPlan.user_id == user_id)
        return self.session.scalar(statement)

    def get_by_date_and_user(self, plan_date: date, user_id: int) -> DailyPlan | None:
        statement = select(DailyPlan).where(DailyPlan.plan_date == plan_date, DailyPlan.user_id == user_id)
        return self.session.scalar(statement)

    def get_with_tasks(self, plan_id: int, user_id: int) -> DailyPlan | None:
        statement = (
            select(DailyPlan)
            .where(DailyPlan.id == plan_id, DailyPlan.user_id == user_id)
            .options(selectinload(DailyPlan.planned_tasks).selectinload(DailyPlanTask.task))
        )
        return self.session.scalar(statement)

    def save(self, plan: DailyPlan) -> DailyPlan:
        self.session.add(plan)
        self.session.flush()
        self.session.refresh(plan)
        return plan

    def delete(self, plan: DailyPlan) -> None:
        self.session.delete(plan)
        self.session.flush()
