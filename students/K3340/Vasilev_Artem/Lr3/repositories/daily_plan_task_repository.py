from sqlalchemy import select
from sqlalchemy.orm import Session

from models.daily_plan_task import DailyPlanTask


class DailyPlanTaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_link(self, plan_id: int, task_id: int) -> DailyPlanTask | None:
        statement = select(DailyPlanTask).where(
            DailyPlanTask.daily_plan_id == plan_id,
            DailyPlanTask.task_id == task_id,
        )
        return self.session.scalar(statement)

    def create(self, link: DailyPlanTask) -> DailyPlanTask:
        self.session.add(link)
        self.session.flush()
        self.session.refresh(link)
        return link

    def delete(self, link: DailyPlanTask) -> None:
        self.session.delete(link)
        self.session.flush()
