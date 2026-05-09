from src.policy.policy_engine import PolicyResult
from src.workflow.state_machine import get_allowed_actions


def generate_fallback_investigation(case: dict, policy_result: PolicyResult) -> dict:
    """
    Generate a deterministic reviewer brief when the AI service is unavailable.

    This keeps the workflow usable even if OpenAI is not configured or fails.
    """
    allowed_workflow_actions = get_allowed_actions(case["status"])

    contradictions = []
    if "buyer_claim_conflicts_with_delivery_status" in policy_result.ambiguity_flags:
        contradictions.append(
            "Buyer claim conflicts with delivery status."
        )

    missing_evidence = list(policy_result.required_evidence)

    risk_considerations = list(policy_result.risk_flags)

    recommended_action = _choose_bounded_recommendation(
        policy_result=policy_result,
        allowed_workflow_actions=allowed_workflow_actions,
    )

    return {
        "source": "fallback",
        "case_summary": (
            f"Case {case['case_id']} is a {case['claim_type']} dispute. "
            f"The buyer requested {case['claim']['requested_outcome']}. "
            f"The current workflow state is {case['status']}."
        ),
        "key_evidence": [
            f"Order value: {case['order']['currency']} {case['order']['order_value']}",
            f"Buyer risk tier: {case['buyer']['risk_tier']}",
            f"Seller response status: {case['seller']['response_status']}",
            f"Delivery status: {case['delivery']['delivery_status']}",
            f"Proof of delivery: {case['delivery']['proof_of_delivery']}",
        ],
        "contradictions": contradictions,
        "missing_evidence": missing_evidence,
        "risk_considerations": risk_considerations,
        "recommended_next_action": recommended_action,
        "confidence": policy_result.confidence,
        "reviewer_brief": policy_result.policy_rationale,
        "human_review_required": True,
    }


def _choose_bounded_recommendation(
    policy_result: PolicyResult,
    allowed_workflow_actions: list[str],
) -> str:
    """
    Choose a recommendation that is valid within workflow boundaries.

    This is intentionally conservative.
    """
    if policy_result.requires_escalation and "escalate" in allowed_workflow_actions:
        return "escalate"

    if (
        policy_result.recommended_action in allowed_workflow_actions
        or policy_result.recommended_action in policy_result.eligible_actions
    ):
        return policy_result.recommended_action

    if "request_more_evidence" in allowed_workflow_actions:
        return "request_more_evidence"

    if allowed_workflow_actions:
        return allowed_workflow_actions[0]

    return "manual_review"