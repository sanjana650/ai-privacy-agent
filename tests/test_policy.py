from app.tools.policy import search_policy


def get_sources(results):
    """Extract source filenames from retrieved policy results."""
    return {
        result.source
        for result in results
    }


def test_search_nric_policy():
    results = search_policy(
        "What is the policy for NRIC in application logs?"
    )

    assert len(results) > 0

    sources = get_sources(results)

    assert (
        "pii_policy.txt" in sources
        or "incident_policy.txt" in sources
    )


def test_search_email_policy():
    results = search_policy(
        "Can email addresses appear in application logs?"
    )

    assert len(results) > 0

    sources = get_sources(results)

    assert (
        "pii_policy.txt" in sources
        or "logging_policy.txt" in sources
    )


def test_search_phone_policy():
    results = search_policy(
        "What is the policy for logging phone numbers?"
    )

    assert len(results) > 0

    sources = get_sources(results)

    assert (
        "pii_policy.txt" in sources
        or "logging_policy.txt" in sources
    )


def test_search_credit_card_policy():
    results = search_policy(
        "What is the policy for credit card numbers in logs?"
    )

    assert len(results) > 0

    sources = get_sources(results)

    assert (
        "pii_policy.txt" in sources
        or "incident_policy.txt" in sources
    )


def test_search_incident_risk_policy():
    results = search_policy(
        "How should privacy incidents involving "
        "sensitive information be classified?"
    )

    assert len(results) > 0

    sources = get_sources(results)

    assert "incident_policy.txt" in sources


def test_search_retention_policy():
    results = search_policy(
        "How long should application logs containing "
        "personal information be retained?"
    )

    assert len(results) > 0

    sources = get_sources(results)

    assert "retention_policy.txt" in sources