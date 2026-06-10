from core.detection.engine import DetectionEngine, ScanResult
from db.models.scan import Scan
from db.models.detection import Detection
from db.repositories.scan_repo import ScanRepository


class ScanService:

    def __init__(self, db_repo: ScanRepository):
        self._engine = DetectionEngine()
        self._repo = db_repo

    async def run_scan(self, text: str, source: str | None = None) -> Scan:
        result: ScanResult = await self._engine.scan(text)

        scan = Scan(
            input_text=text,
            risk_score=result.score.score,
            risk_level=result.score.risk_level,
            llm_fallback_used=result.llm_fallback_used,
            source=source,
        )

        scan.detections = [
            Detection(
                attack_type=d.attack_type,
                description=d.description,
                confidence=d.confidence,
                matched_pattern=d.matched_pattern,
                severity=d.severity,
                detection_method=d.detection_method,
            )
            for d in result.detections
        ]

        return await self._repo.create(scan)
