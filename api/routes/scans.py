import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.repositories.scan_repo import ScanRepository
from services.scan_service import ScanService

router = APIRouter(prefix="/scans", tags=["scans"])


# --- Request / Response schemas ---


class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=32_000, description="Text to analyse")
    source: str | None = Field(None, max_length=255, description="Optional caller identifier")


class DetectionResponse(BaseModel):
    attack_type: str
    description: str
    confidence: float
    severity: str
    detection_method: str
    matched_pattern: str | None

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    id: uuid.UUID
    text: str
    risk_score: float
    risk_level: str
    llm_fallback_used: bool
    source: str | None
    detections: list[DetectionResponse]
    created_at: str

    class Config:
        from_attributes = True


# --- Endpoints ---


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(request: ScanRequest, db: AsyncSession = Depends(get_db)):
    repo = ScanRepository(db)
    service = ScanService(repo)
    scan = await service.run_scan(text=request.text, source=request.source)
    return _to_response(scan)


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ScanRepository(db)
    scan = await repo.get_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _to_response(scan)


@router.get("/", response_model=list[ScanResponse])
async def list_scans(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    repo = ScanRepository(db)
    scans = await repo.list(limit=limit, offset=offset)
    return [_to_response(s) for s in scans]


def _to_response(scan) -> dict:
    return {
        "id": scan.id,
        "text": scan.input_text,
        "risk_score": scan.risk_score,
        "risk_level": scan.risk_level,
        "llm_fallback_used": scan.llm_fallback_used,
        "source": scan.source,
        "created_at": scan.created_at.isoformat(),
        "detections": [
            {
                "attack_type": d.attack_type,
                "description": d.description,
                "confidence": d.confidence,
                "severity": d.severity,
                "detection_method": d.detection_method,
                "matched_pattern": d.matched_pattern,
            }
            for d in scan.detections
        ],
    }
