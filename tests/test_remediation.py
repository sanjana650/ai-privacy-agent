from app.tools.pii import detect_pii
from app.tools.remediation import redact_log


def test_redact_nric():
    log = "Payment failed for S1234567A"

    findings = detect_pii(log)
    redacted = redact_log(log, findings)

    assert redacted == "Payment failed for [REDACTED-NRIC]"


def test_redact_email():
    log = "Contact alice@example.com"

    findings = detect_pii(log)
    redacted = redact_log(log, findings)

    assert redacted == "Contact [REDACTED-EMAIL]"


def test_redact_multiple_pii():
    log = "Customer S1234567A can be reached at alice@example.com"

    findings = detect_pii(log)
    redacted = redact_log(log, findings)

    assert redacted == (
        "Customer [REDACTED-NRIC] can be reached at [REDACTED-EMAIL]"
    )


def test_no_pii():
    log = "Application started successfully"

    findings = detect_pii(log)
    redacted = redact_log(log, findings)

    assert redacted == log