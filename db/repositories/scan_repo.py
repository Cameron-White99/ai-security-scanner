import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models.scan import Scan


class ScanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, scan: Scan) -> Scan:
        self.db.add(scan)
        await self.db.flush()
        await self.db.refresh(scan, ["detections"])
        return scan

    async def get_by_id(self, scan_id: uuid.UUID) -> Scan | None:
        result = await self.db.execute(
            select(Scan)
            .where(Scan.id == scan_id)
            .options(selectinload(Scan.detections))
        )
        return result.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Scan]:
        result = await self.db.execute(
            select(Scan)
            .options(selectinload(Scan.detections))
            .order_by(Scan.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
