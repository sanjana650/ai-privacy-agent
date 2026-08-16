import re

from app.models.schemas import PIIFinding, PIIType


PII_PATTERNS: dict[PIIType, str] = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "PHONE": r"(?:\+65[\s-]?)?[689]\d{3}[\s-]?\d{4}",
    "NRIC": r"\b[STFGM]\d{7}[A-Z]\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
}


def detect_pii(log: str) -> list[PIIFinding]:
    findings: list[PIIFinding] = []

    for pii_type, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, log, re.IGNORECASE):
            findings.append(
                PIIFinding(
                    type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                )
            )

    return findings

