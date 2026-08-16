import json
from pathlib import Path

from app.agent.agent import investigate_log
from app.tools.pii import detect_pii
from app.tools.remediation import redact_log


CASES_PATH = Path("evaluation/cases.json")


def evaluate():
    cases = json.loads(
        CASES_PATH.read_text(encoding="utf-8")
    )

    total = len(cases)

    pii_correct = 0
    risk_correct = 0
    structured_valid = 0
    redaction_correct = 0
    policy_correct = 0

    successful_cases = 0
    failed_cases = 0

    for case in cases:
        print(f"\n{'=' * 60}")
        print(f"CASE: {case['id']}")
        print(f"LOG: {case['log']}")

        # ---------------------------------
        # Run agent
        # ---------------------------------
        try:
            report = investigate_log(case["log"])

            successful_cases += 1
            structured_valid += 1

        except Exception as error:
            failed_cases += 1

            print()
            print(f"EVALUATION ERROR: {error}")

            continue

        # ---------------------------------
        # PII evaluation
        # ---------------------------------
        expected_pii = set(case["expected_pii"])
        actual_pii = set(report.pii_detected)

        pii_match = expected_pii == actual_pii

        if pii_match:
            pii_correct += 1

        # ---------------------------------
        # Risk evaluation
        # ---------------------------------
        expected_risk = case["expected_risk"]
        actual_risk = report.risk_level

        risk_match = expected_risk == actual_risk

        if risk_match:
            risk_correct += 1

        # ---------------------------------
        # Redaction evaluation
        # ---------------------------------
        findings = detect_pii(case["log"])

        if case["should_redact"]:
            expected_redacted_log = redact_log(
                case["log"],
                findings,
            )

            redaction_match = (
                report.redacted_log
                == expected_redacted_log
            )

        else:
            expected_redacted_log = case["log"]

            redaction_match = (
                report.redacted_log == case["log"]
                or report.redacted_log is None
            )

        if redaction_match:
            redaction_correct += 1

        # ---------------------------------
        # Policy grounding evaluation
        # ---------------------------------
        expected_policy_sources = set(
            case.get(
                "expected_policy_sources",
                [],
            )
        )

        actual_policy_sources = set(
            report.policy_sources
        )

        if expected_policy_sources:
            # At least one valid expected policy
            # source must have been used.
            policy_match = bool(
                expected_policy_sources
                & actual_policy_sources
            )

        else:
            # Clean logs should not require
            # policy grounding.
            policy_match = (
                len(actual_policy_sources) == 0
            )

        if policy_match:
            policy_correct += 1

        # ---------------------------------
        # Print case results
        # ---------------------------------
        print()
        print(f"Expected PII: {expected_pii}")
        print(f"Actual PII:   {actual_pii}")
        print(f"PII correct:  {pii_match}")

        print()
        print(f"Expected risk: {expected_risk}")
        print(f"Actual risk:   {actual_risk}")
        print(f"Risk correct:  {risk_match}")

        print()
        print(
            "Expected policy sources: "
            f"{expected_policy_sources}"
        )

        print(
            "Actual policy sources:   "
            f"{actual_policy_sources}"
        )

        print(
            "Policy grounding correct: "
            f"{policy_match}"
        )

        print()
        print(
            "Policy violations: "
            f"{report.policy_violations}"
        )

        print()
        print(
            "Expected redacted log: "
            f"{expected_redacted_log}"
        )

        print(
            "Actual redacted log:   "
            f"{report.redacted_log}"
        )

        print(
            "Redaction correct: "
            f"{redaction_match}"
        )

    # ---------------------------------
    # Summary
    # ---------------------------------
    print(f"\n{'=' * 60}")
    print("EVALUATION SUMMARY")
    print(f"{'=' * 60}")

    print(f"Total cases: {total}")
    print(
        f"Successfully evaluated: "
        f"{successful_cases}"
    )
    print(
        f"Evaluation errors: "
        f"{failed_cases}"
    )

    if successful_cases == 0:
        print(
            "No cases were successfully evaluated."
        )
        return

    print(
        f"PII accuracy: "
        f"{pii_correct / successful_cases:.2%}"
    )

    print(
        f"Risk accuracy: "
        f"{risk_correct / successful_cases:.2%}"
    )

    print(
        f"Policy grounding: "
        f"{policy_correct / successful_cases:.2%}"
    )

    print(
        f"Structured output success: "
        f"{structured_valid / successful_cases:.2%}"
    )

    print(
        f"Redaction accuracy: "
        f"{redaction_correct / successful_cases:.2%}"
    )


if __name__ == "__main__":
    evaluate()