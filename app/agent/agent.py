import re

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import ToolMessage
from langchain_groq import ChatGroq

from app.agent.prompts import PRIVACY_AGENT_PROMPT
from app.agent.tools import (
    detect_pii_tool,
    search_policy_tool,
    redact_log_tool,
)
from app.config import settings
from app.models.schemas import InvestigationReport
from app.tools.pii import detect_pii
from app.tools.remediation import redact_log


def create_privacy_agent():
    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is required to run the privacy agent."
        )

    llm = ChatGroq(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        temperature=0,
    )

    return create_agent(
        model=llm,
        tools=[
            detect_pii_tool,
            search_policy_tool,
            redact_log_tool,
        ],
        system_prompt=PRIVACY_AGENT_PROMPT,
        response_format=ToolStrategy(
            InvestigationReport
        ),
    )


def extract_policy_sources(
    messages: list,
) -> list[str]:
    sources: set[str] = set()

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        if message.name != "search_policy_tool":
            continue

        content = str(message.content)

        matches = re.findall(
            r"Source:\s*([^\s]+\.txt)",
            content,
        )

        sources.update(matches)

    return sorted(sources)


def investigate_log(
    log: str,
) -> InvestigationReport:
    privacy_agent = create_privacy_agent()

    result = privacy_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Investigate this application log:\n\n"
                        f"{log}"
                    ),
                }
            ]
        }
    )

    report: InvestigationReport = result[
        "structured_response"
    ]

    findings = detect_pii(log)

    report.pii_detected = [
        finding.type
        for finding in findings
    ]

    report.policy_sources = extract_policy_sources(
        result["messages"]
    )

    if findings:
        report.redacted_log = redact_log(
            log,
            findings,
        )
    else:
        report.redacted_log = log

    return report