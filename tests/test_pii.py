from app.tools.pii import detect_pii


def test_detect_nric():
    log = "Payment failed for S1234567A"

    findings = detect_pii(log)

    assert len(findings) == 1
    assert findings[0].type == "NRIC"
    assert findings[0].value == "S1234567A"


def test_detect_email():
    log = "Contact alice@example.com"

    findings = detect_pii(log)

    assert len(findings) == 1
    assert findings[0].type == "EMAIL"


def test_detect_multiple_pii():
    log = "Customer S1234567A can be reached at alice@example.com"

    findings = detect_pii(log)

    types = [finding.type for finding in findings]
    print(types)

    assert "NRIC" in types
    assert "EMAIL" in types


def test_no_pii():
    log = "Application started successfully"

    findings = detect_pii(log)

    assert findings == []