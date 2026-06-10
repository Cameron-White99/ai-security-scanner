import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.repositories.report_repo import ReportRepository
from services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


# --- Request / Response schemas ---


class ReportRequest(BaseModel):
    from_date: datetime
    to_date: datetime


class TopRiskItem(BaseModel):
    id: str
    risk_score: float
    risk_level: str
    created_at: str


class ReportResponse(BaseModel):
    id: uuid.UUID
    from_date: str
    to_date: str
    total_scans: int
    generated_at: str
    risk_distribution: dict[str, int]
    attack_type_breakdown: dict[str, int]
    top_risks: list[TopRiskItem]
    mitigations: dict[str, str]
    summary: str

    model_config = ConfigDict(from_attributes=True)


# --- Endpoints ---


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(request: ReportRequest, db: AsyncSession = Depends(get_db)):
    if request.from_date >= request.to_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_date must be before to_date",
        )
    service = ReportService(db)
    report = await service.generate(from_date=request.from_date, to_date=request.to_date)
    return _to_response(report)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ReportRepository(db)
    report = await repo.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return _to_response(report)


@router.get("/", response_model=list[ReportResponse])
async def list_reports(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)
    reports = await repo.list(limit=limit, offset=offset)
    return [_to_response(r) for r in reports]


def _to_response(report) -> dict:
    data = report.data
    return {
        "id": report.id,
        "from_date": report.from_date.isoformat(),
        "to_date": report.to_date.isoformat(),
        "total_scans": report.total_scans,
        "generated_at": report.created_at.isoformat(),
        "risk_distribution": data["risk_distribution"],
        "attack_type_breakdown": data["attack_type_breakdown"],
        "top_risks": data["top_risks"],
        "mitigations": data["mitigations"],
        "summary": data["summary"],
    }
