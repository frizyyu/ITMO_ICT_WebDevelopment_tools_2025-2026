from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.daily_plan import DailyPlan
from models.daily_plan_task import DailyPlanTask
from models.enums import PlannedTaskStatus
from models.user import User
from repositories.daily_plan_repository import DailyPlanRepository
from repositories.daily_plan_task_repository import DailyPlanTaskRepository
from repositories.task_repository import TaskRepository
from schemas.daily_plan import DailyPlanCreate, DailyPlanTaskCreate, DailyPlanUpdate


class DailyPlanService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.daily_plan_repository = DailyPlanRepository(session)
        self.daily_plan_task_repository = DailyPlanTaskRepository(session)
        self.task_repository = TaskRepository(session)

    def _get_owned_task(self, task_id: int, current_user: User):
        task = self.task_repository.get_by_id_and_owner(task_id, current_user.id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return task

    def _build_plan_links(
        self,
        items: list[DailyPlanTaskCreate],
        current_user: User,
    ) -> list[DailyPlanTask]:
        links: list[DailyPlanTask] = []
        seen_task_ids: set[int] = set()
        for item in items:
            self._get_owned_task(item.task_id, current_user)
            if item.task_id in seen_task_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A task cannot be added to the same daily plan twice.",
                )
            seen_task_ids.add(item.task_id)
            links.append(
                DailyPlanTask(
                    task_id=item.task_id,
                    position=item.position,
                    status=item.status,
                    planned_minutes=item.planned_minutes,
                    comment=item.comment,
                )
            )
        return links

    def create_daily_plan(self, payload: DailyPlanCreate, current_user: User) -> DailyPlan:
        existing_plan = self.daily_plan_repository.get_by_date_and_user(payload.plan_date, current_user.id)
        if existing_plan is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Daily plan for this date already exists.",
            )

        plan = DailyPlan(
            user_id=current_user.id,
            plan_date=payload.plan_date,
            notes=payload.notes,
        )
        plan.planned_tasks = self._build_plan_links(payload.tasks, current_user)
        self.daily_plan_repository.create(plan)
        self.session.commit()
        plan_with_tasks = self.daily_plan_repository.get_with_tasks(plan.id, current_user.id)
        if plan_with_tasks is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan not found.")
        return plan_with_tasks

    def list_daily_plans(self, current_user: User, skip: int = 0, limit: int = 100) -> list[DailyPlan]:
        return self.daily_plan_repository.list_by_user(current_user.id, skip=skip, limit=limit)

    def get_daily_plan(self, plan_id: int, current_user: User) -> DailyPlan:
        plan = self.daily_plan_repository.get_by_id_and_user(plan_id, current_user.id)
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan not found.")
        return plan

    def get_daily_plan_with_tasks(self, plan_id: int, current_user: User) -> DailyPlan:
        plan = self.daily_plan_repository.get_with_tasks(plan_id, current_user.id)
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan not found.")
        return plan

    def update_daily_plan(self, plan_id: int, payload: DailyPlanUpdate, current_user: User) -> DailyPlan:
        plan = self.get_daily_plan(plan_id, current_user)
        data = payload.model_dump(exclude_unset=True)

        new_plan_date = data.get("plan_date")
        if new_plan_date is not None and new_plan_date != plan.plan_date:
            existing_plan = self.daily_plan_repository.get_by_date_and_user(new_plan_date, current_user.id)
            if existing_plan is not None and existing_plan.id != plan.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Daily plan for this date already exists.",
                )

        tasks_payload = data.pop("tasks", None)
        for field_name, field_value in data.items():
            setattr(plan, field_name, field_value)

        if tasks_payload is not None:
            plan.planned_tasks.clear()
            seen_task_ids: set[int] = set()
            for item in payload.tasks or []:
                if item.task_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Each daily plan task update item must include task_id.",
                    )
                self._get_owned_task(item.task_id, current_user)
                if item.task_id in seen_task_ids:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A task cannot be added to the same daily plan twice.",
                    )
                seen_task_ids.add(item.task_id)
                plan.planned_tasks.append(
                    DailyPlanTask(
                        task_id=item.task_id,
                        position=item.position or 0,
                        status=item.status or PlannedTaskStatus.PLANNED,
                        planned_minutes=item.planned_minutes,
                        comment=item.comment,
                    )
                )

        self.daily_plan_repository.save(plan)
        self.session.commit()
        plan_with_tasks = self.daily_plan_repository.get_with_tasks(plan.id, current_user.id)
        if plan_with_tasks is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan not found.")
        return plan_with_tasks

    def delete_daily_plan(self, plan_id: int, current_user: User) -> None:
        plan = self.get_daily_plan(plan_id, current_user)
        self.daily_plan_repository.delete(plan)
        self.session.commit()

    def add_task_to_plan(self, plan_id: int, task_id: int, current_user: User) -> DailyPlan:
        plan = self.get_daily_plan_with_tasks(plan_id, current_user)
        self._get_owned_task(task_id, current_user)
        existing_link = self.daily_plan_task_repository.get_link(plan.id, task_id)
        if existing_link is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task is already attached to this daily plan.",
            )

        self.daily_plan_task_repository.create(
            DailyPlanTask(
                daily_plan_id=plan.id,
                task_id=task_id,
                position=len(plan.planned_tasks),
            )
        )
        self.session.commit()
        plan_with_tasks = self.daily_plan_repository.get_with_tasks(plan.id, current_user.id)
        if plan_with_tasks is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan not found.")
        return plan_with_tasks

    def remove_task_from_plan(self, plan_id: int, task_id: int, current_user: User) -> None:
        self.get_daily_plan(plan_id, current_user)
        self._get_owned_task(task_id, current_user)
        link = self.daily_plan_task_repository.get_link(plan_id, task_id)
        if link is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task link not found for this daily plan.",
            )
        self.daily_plan_task_repository.delete(link)
        self.session.commit()
