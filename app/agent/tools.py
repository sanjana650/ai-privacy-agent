from langchain.tools import tool

from app.tools.pii import detect_pii
from app.tools.policy import search_policy
from app.tools.remediation import redact_log


@tool
def detect_pii_tool(log: str) -> str:
    """
    Detect personally identifiable information in an application log.

    Use this when you need to determine whether a log contains
    sensitive information such as NRICs, emails, phone numbers,
    or credit card numbers.
    """

    findings = detect_pii(log)

    if not findings:
        return "No PII detected."

    return "\n".join(
        f"{finding.type}: {finding.value}"
        for finding in findings
    )


@tool
def search_policy_tool(query: str) -> str:
    """
    Search organizational privacy and logging policies.

    Use this when you need to determine whether detected information
    violates company policy or what remediation is required.
    """

    results = search_policy(query)

    if not results:
        return "No relevant policy found."

    return "\n\n".join(
    f"Source: {result.source}\n"
    f"Policy: {result.content}"
    for result in results
)


@tool
def redact_log_tool(log: str) -> str:
    """
    Detect and redact PII from an application log.

    Use this when sensitive information must be removed from the log.
    """

    findings = detect_pii(log)

    if not findings:
        return log

    return redact_log(log, findings)