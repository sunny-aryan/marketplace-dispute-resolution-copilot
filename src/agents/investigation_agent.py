import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from src.audit.audit_repository import create_audit_event
from src.policy.policy_engine import PolicyResult, evaluate_policy
from src.services.fallback_investigation_service import generate_fallback_investigation
from src.workflow.state_machine import get_allowed_actions


load_dotenv()


class InvestigationResult(BaseModel):
    source: str = Field(description="openai or fallback")
    case_summary: str
    key_evidence: list[str]
    contradictions: list[str]
    missing_evidence: list[str]
    risk_considerations: list[str]
    recommended_next_action: str
    confidence: str
    reviewer_brief: str
    human_review_required: bool


def run_investigation(case: dict, actor: str = "reviewer_001") -> dict:
    """
    Run a bounded investigation for a dispute case.

    Policy is evaluated first. The AI receives the policy-defined boundaries and
    must recommend within eligible or workflow-valid actions.
    """
    policy_result = evaluate_policy(case)
    allowed_workflow_actions = get_allowed_actions(case["status"])

    try:
        investigation = _run_openai_investigation(
            case=case,
            policy_result=policy_result,
            allowed_workflow_actions=allowed_workflow_actions,
        )
    except Exception as error:
        investigation = generate_fallback_investigation(
            case=case,
            policy_result=policy_result,
        )
        investigation["fallback_reason"] = str(error)

    create_audit_event(
        case_id=case["case_id"],
        actor=actor,
        event_type="investigation_run",
        from_status=case["status"],
        to_status=case["status"],
        action="run_investigation",
        rationale="Investigation package generated for reviewer.",
        details={
            "source": investigation["source"],
            "recommended_next_action": investigation["recommended_next_action"],
            "confidence": investigation["confidence"],
        },
    )

    return investigation


def _run_openai_investigation(
    case: dict,
    policy_result: PolicyResult,
    allowed_workflow_actions: list[str],
) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=api_key)

    allowed_recommendations = _build_allowed_recommendations(
        policy_result=policy_result,
        allowed_workflow_actions=allowed_workflow_actions,
    )

    prompt_payload = {
        "case": case,
        "policy_boundaries": {
            "eligible_actions": policy_result.eligible_actions,
            "blocked_actions": policy_result.blocked_actions,
            "required_evidence": policy_result.required_evidence,
            "ambiguity_flags": policy_result.ambiguity_flags,
            "risk_flags": policy_result.risk_flags,
            "requires_escalation": policy_result.requires_escalation,
            "policy_recommended_action": policy_result.recommended_action,
            "policy_rationale": policy_result.policy_rationale,
        },
        "workflow_boundaries": {
            "current_state": case["status"],
            "allowed_workflow_actions": allowed_workflow_actions,
        },
        "allowed_recommendations": allowed_recommendations,
    }

    response = client.responses.parse(
        model=os.environ.get("OPENAI_MODEL", "gpt-5.4-mini"),
        input=[
            {
                "role": "developer",
                "content": (
                    "You are a bounded marketplace dispute investigation assistant. "
                    "You help human reviewers understand dispute evidence. "
                    "You must not make final decisions. "
                    "Your recommended_next_action must be one of the allowed_recommendations. "
                    "If evidence is ambiguous, prefer escalation or more evidence over final outcomes. "
                    "Always set human_review_required to true."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(prompt_payload),
            },
        ],
        text_format=InvestigationResult,
    )

    result = response.output_parsed.model_dump()
    result["source"] = "openai"

    if result["recommended_next_action"] not in allowed_recommendations:
        result["recommended_next_action"] = _safe_default_recommendation(
            allowed_recommendations
        )
        result["reviewer_brief"] = (
            result["reviewer_brief"]
            + " The original recommendation was replaced because it was outside allowed system boundaries."
        )

    result["human_review_required"] = True

    return result


def _build_allowed_recommendations(
    policy_result: PolicyResult,
    allowed_workflow_actions: list[str],
) -> list[str]:
    allowed = set()

    for action in policy_result.eligible_actions:
        allowed.add(action)

    for action in allowed_workflow_actions:
        allowed.add(action)

    for action in policy_result.blocked_actions:
        allowed.discard(action)

    if policy_result.requires_escalation:
        allowed.add("escalate")

    if not allowed:
        allowed.add("manual_review")

    return sorted(allowed)


def _safe_default_recommendation(allowed_recommendations: list[str]) -> str:
    if "escalate" in allowed_recommendations:
        return "escalate"

    if "request_more_evidence" in allowed_recommendations:
        return "request_more_evidence"

    if "manual_review" in allowed_recommendations:
        return "manual_review"

    return allowed_recommendations[0]