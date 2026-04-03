from sqlalchemy import select
from sqlalchemy.orm import Session

from models.time_log import TimeLog


class TimeLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, time_log: TimeLog) -> TimeLog:
        self.session.add(time_log)
        self.session.flush()
        self.session.refresh(time_log)
        return time_log

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[TimeLog]:
        statement = (
            select(TimeLog)
            .where(TimeLog.user_id == user_id)
            .order_by(TimeLog.started_at.desc(), TimeLog.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def get_by_id_and_user(self, log_id: int, user_id: int) -> TimeLog | None:
        statement = select(TimeLog).where(TimeLog.id == log_id, TimeLog.user_id == user_id)
        return self.session.scalar(statement)

    def save(self, time_log: TimeLog) -> TimeLog:
        self.session.add(time_log)
        self.session.flush()
        self.session.refresh(time_log)
        return time_log

    def delete(self, time_log: TimeLog) -> None:
        self.session.delete(time_log)
        self.session.flush()
