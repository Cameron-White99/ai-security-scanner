import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.report import Report


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, report: Report) -> Report:
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def get_by_id(self, report_id: uuid.UUID) -> Report | None:
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Report]:
        result = await self.db.execute(
            select(Report).order_by(Report.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
