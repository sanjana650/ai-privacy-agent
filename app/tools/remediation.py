from app.models.schemas import PIIFinding


def redact_log(log: str, findings: list[PIIFinding]) -> str:
    redacted_log = log

    # We'll replace findings from the end of the string backwards.
    sorted_findings = sorted(
        findings,
        key=lambda finding: finding.start,
        reverse=True,
    )

    for finding in sorted_findings:
        replacement = f"[REDACTED-{finding.type}]"

        redacted_log = (
            redacted_log[:finding.start]
            + replacement
            + redacted_log[finding.end:]
        )

    return redacted_log