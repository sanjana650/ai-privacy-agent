from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import InvestigationReport


client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("app.main.investigate_log")
def test_create_investigation(mock_investigate):
    mock_investigate.return_value = InvestigationReport(
        risk_level="HIGH",
        pii_detected=["NRIC"],
        policy_violations=[
            "NRIC exposure violates logging policy"
        ],
        policy_sources=[
            "pii_policy.txt",
            "incident_policy.txt",
        ],
        explanation="NRIC detected in application log.",
        recommended_action="Redact the NRIC.",
        redacted_log=(
            "Payment failed for customer "
            "[REDACTED-NRIC]"
        ),
    )

    response = client.post(
        "/api/v1/investigations",
        json={
            "log": "Payment failed for customer S1234567A"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["risk_level"] == "HIGH"
    assert body["pii_detected"] == ["NRIC"]
    assert "investigation_id" in body


@patch("app.main.investigate_log")
def test_get_investigation(mock_investigate):
    mock_investigate.return_value = InvestigationReport(
        risk_level="LOW",
        pii_detected=[],
        policy_violations=[],
        policy_sources=[],
        explanation="No PII detected.",
        recommended_action="No remediation required.",
        redacted_log="Application started successfully",
    )

    create_response = client.post(
        "/api/v1/investigations",
        json={
            "log": "Application started successfully"
        },
    )

    investigation_id = create_response.json()[
        "investigation_id"
    ]

    response = client.get(
        f"/api/v1/investigations/{investigation_id}"
    )

    assert response.status_code == 200
    assert (
        response.json()["investigation_id"]
        == investigation_id
    )


def test_get_missing_investigation():
    response = client.get(
        "/api/v1/investigations/not-real"
    )

    assert response.status_code == 404


def test_empty_log_rejected():
    response = client.post(
        "/api/v1/investigations",
        json={"log": ""},
    )

    assert response.status_code == 422