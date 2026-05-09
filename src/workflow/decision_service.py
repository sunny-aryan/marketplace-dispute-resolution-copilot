from dataclasses import dataclass, field

from src.policy.policy_engine import PolicyResult, evaluate_policy
from src.workflow.state_machine import TransitionResult, validate_transition


RESOLUTION_ACTIONS = {
    "refund_buyer",
    "partial_refund",
    "deny_claim",
    "senior_reviewer_refund",
    "senior_reviewer_partial_refund",
    "senior_reviewer_deny",
}

RATIONALE_REQUIRED_ACTIONS = {
    "refund_buyer",
    "partial_refund",
    "deny_claim",
    "senior_reviewer_refund",
    "senior_reviewer_partial_refund",
    "senior_reviewer_deny",
    "escalate",
    "request_more_evidence",
}

ACTION_TO_POLICY_ACTION = {
    "refund_buyer": "refund_buyer",
    "senior_reviewer_refund": "refund_buyer",
    "partial_refund": "partial_refund",
    "senior_reviewer_partial_refund": "partial_refund",
    "deny_claim": "deny_claim",
    "senior_reviewer_deny": "deny_claim",
    "request_more_evidence": "request_more_evidence",
}


@dataclass
class ActionValidationResult:
    case_id: str
    action: str
    current_state: str
    allowed: bool
    next_state: str
    reasons: list[str] = field(default_factory=list)
    policy_result: PolicyResult | None = None
    transition_result: TransitionResult | None = None


def validate_reviewer_action(
    case: dict,
    action: str,
    rationale: str = "",
) -> ActionValidationResult:
    """
    Validate whether an agent action is allowed for a dispute case.

    This combines:
    - workflow state transition rules
    - deterministic policy evaluation
    - human rationale requirements

    This function does not mutate or persist state.
    """
    current_state = case["status"]
    transition_result = validate_transition(current_state, action)
    policy_result = evaluate_policy(case)

    reasons: list[str] = []

    if not transition_result.allowed:
        reasons.append(transition_result.reason)

        return ActionValidationResult(
            case_id=case["case_id"],
            action=action,
            current_state=current_state,
            allowed=False,
            next_state=current_state,
            reasons=reasons,
            policy_result=policy_result,
            transition_result=transition_result,
        )

    if action in RATIONALE_REQUIRED_ACTIONS and not rationale.strip():
        reasons.append("Human rationale is required for this action.")

    mapped_policy_action = ACTION_TO_POLICY_ACTION.get(action)

    if mapped_policy_action:
        _validate_against_policy_action(
            action=action,
            mapped_policy_action=mapped_policy_action,
            current_state=current_state,
            policy_result=policy_result,
            reasons=reasons,
        )

    allowed = len(reasons) == 0

    if allowed:
        reasons.append("Decision is allowed by workflow and policy checks.")

    return ActionValidationResult(
        case_id=case["case_id"],
        action=action,
        current_state=current_state,
        allowed=allowed,
        next_state=transition_result.to_state if allowed else current_state,
        reasons=reasons,
        policy_result=policy_result,
        transition_result=transition_result,
    )


def _validate_against_policy_action(
    action: str,
    mapped_policy_action: str,
    current_state: str,
    policy_result: PolicyResult,
    reasons: list[str],
) -> None:
    if mapped_policy_action not in policy_result.eligible_actions:
        reasons.append(
            f"Action '{mapped_policy_action}' is not eligible under current policy rules."
        )

    if action in {"refund_buyer", "partial_refund", "deny_claim"}:
        if policy_result.requires_escalation and current_state != "escalated":
            reasons.append(
                "This case requires escalation before refund, partial refund, or denial."
            )

    if action == "refund_buyer":
        if "auto_refund" in policy_result.blocked_actions:
            reasons.append(
                "Direct refund is blocked because automated or non-escalated refund is not allowed."
            )

        if (
            "direct_refund_without_escalation" in policy_result.blocked_actions
            and current_state != "escalated"
        ):
            reasons.append("Direct refund is blocked before escalation.")

    if action == "senior_reviewer_refund":
        if current_state != "escalated":
            reasons.append("Senior reviewer refund is only allowed from escalated state.")

    if action in {"deny_claim", "senior_reviewer_deny"}:
        if "final_denial_without_delivery_proof" in policy_result.blocked_actions:
            reasons.append("Final denial is blocked because delivery proof is missing.")

        if (
            "direct_denial_without_escalation" in policy_result.blocked_actions
            and current_state != "escalated"
        ):
            reasons.append("Direct denial is blocked before escalation.")
