from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models.scan import Scan
from db.models.report import Report
from db.repositories.report_repo import ReportRepository


MITIGATIONS = {
    "direct_injection": (
        "Validate and sanitise all user inputs before passing to LLM. Implement strict system "
        "prompt boundaries and use a separate privileged context for system instructions."
    ),
    "indirect_injection": (
        "Treat all external content (web pages, documents, tool outputs) as untrusted. Apply "
        "content filtering before including in LLM context."
    ),
    "jailbreak": (
        "Implement output filtering and behavioural guardrails. Monitor for unusual response "
        "patterns and apply rate limiting on high-risk inputs."
    ),
    "data_exfiltration": (
        "Restrict LLM access to sensitive data. Audit all outputs for sensitive content patterns "
        "and implement output validation before returning responses."
    ),
    "obfuscation": (
        "Apply decoding and normalisation to inputs before analysis. Detect and flag encoded or "
        "obfuscated content for additional scrutiny."
    ),
}


class ReportService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._repo = ReportRepository(db)

    async def generate(self, from_date: datetime, to_date: datetime) -> Report:
        result = await self._db.execute(
            select(Scan)
            .where(Scan.created_at >= from_date, Scan.created_at <= to_date)
            .options(selectinload(Scan.detections))
            .order_by(Scan.risk_score.desc())
        )
        scans = list(result.scalars().all())

        risk_distribution: dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        attack_type_breakdown: dict[str, int] = {}

        for scan in scans:
            level = scan.risk_level
            if level in risk_distribution:
                risk_distribution[level] += 1
            for attack_type in {d.attack_type for d in scan.detections}:
                attack_type_breakdown[attack_type] = attack_type_breakdown.get(attack_type, 0) + 1

        top_risks = [
            {
                "id": str(scan.id),
                "risk_score": scan.risk_score,
                "risk_level": scan.risk_level,
                "created_at": scan.created_at.isoformat(),
            }
            for scan in scans[:5]
        ]

        mitigations = {
            attack_type: MITIGATIONS[attack_type]
            for attack_type in attack_type_breakdown
            if attack_type in MITIGATIONS
        }

        summary = _build_summary(
            from_date, to_date, len(scans), risk_distribution, attack_type_breakdown
        )

        report = Report(
            from_date=from_date,
            to_date=to_date,
            total_scans=len(scans),
            data={
                "risk_distribution": risk_distribution,
                "attack_type_breakdown": attack_type_breakdown,
                "top_risks": top_risks,
                "mitigations": mitigations,
                "summary": summary,
            },
        )
        return await self._repo.create(report)


def _build_summary(
    from_date: datetime,
    to_date: datetime,
    total_scans: int,
    risk_distribution: dict[str, int],
    attack_type_breakdown: dict[str, int],
) -> str:
    start = from_date.date()
    end = to_date.date()

    if total_scans == 0:
        return f"No scans were recorded between {start} and {end}."

    dominant_level = max(risk_distribution, key=lambda k: risk_distribution[k])
    high_risk_count = risk_distribution.get("HIGH", 0) + risk_distribution.get("CRITICAL", 0)

    attack_sentence = ""
    if attack_type_breakdown:
        top_attack = max(attack_type_breakdown, key=lambda k: attack_type_breakdown[k])
        attack_sentence = (
            f" The most frequently detected attack type was {top_attack.replace('_', ' ')}."
        )

    severity_sentence = ""
    if high_risk_count:
        severity_sentence = f" {high_risk_count} scan(s) were rated HIGH or CRITICAL severity, requiring immediate attention."

    return (
        f"Between {start} and {end}, {total_scans} scan(s) were analysed. "
        f"The majority of scans were rated {dominant_level} risk."
        f"{severity_sentence}"
        f"{attack_sentence}"
    )
