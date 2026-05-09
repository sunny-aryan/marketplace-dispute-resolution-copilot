from dataclasses import dataclass


class InvalidStateTransition(Exception):
    """Raised when a requested workflow transition is not allowed."""


@dataclass(frozen=True)
class TransitionResult:
    from_state: str
    action: str
    to_state: str
    allowed: bool
    reason: str


TRANSITIONS = {
    "new": {
        "load_evidence": "ready_for_review",
    },
    "evidence_pending": {
        "evidence_received": "ready_for_review",
        "escalate": "escalated",
    },
    "ready_for_review": {
        "run_policy_evaluation": "policy_evaluated",
        "escalate": "escalated",
    },
    "policy_evaluated": {
        "start_agent_review": "agent_review",
        "request_more_evidence": "evidence_pending",
        "escalate": "escalated",
    },
    "agent_review": {
        "request_more_evidence": "evidence_pending",
        "escalate": "escalated",
        "refund_buyer": "resolved_refund",
        "partial_refund": "resolved_partial_refund",
        "deny_claim": "resolved_denied",
    },
    "escalated": {
        "senior_reviewer_refund": "resolved_refund",
        "senior_reviewer_partial_refund": "resolved_partial_refund",
        "senior_reviewer_deny": "resolved_denied",
        "request_more_evidence": "evidence_pending",
    },
    "resolved_refund": {
        "close_case": "closed",
    },
    "resolved_partial_refund": {
        "close_case": "closed",
    },
    "resolved_denied": {
        "close_case": "closed",
        "buyer_appeal": "reopened",
    },
    "reopened": {
        "add_new_evidence": "ready_for_review",
        "escalate": "escalated",
    },
    "closed": {},
}


def get_allowed_actions(current_state: str) -> list[str]:
    """Return workflow actions allowed from the current state."""
    return list(TRANSITIONS.get(current_state, {}).keys())


def get_next_state(current_state: str, action: str) -> str:
    """Return the next state for a valid action."""
    allowed_actions = TRANSITIONS.get(current_state, {})

    if action not in allowed_actions:
        raise InvalidStateTransition(
            f"Action '{action}' is not allowed from state '{current_state}'."
        )

    return allowed_actions[action]


def validate_transition(current_state: str, action: str) -> TransitionResult:
    """Validate a workflow transition without mutating state."""
    try:
        next_state = get_next_state(current_state, action)
        return TransitionResult(
            from_state=current_state,
            action=action,
            to_state=next_state,
            allowed=True,
            reason="Transition is allowed.",
        )
    except InvalidStateTransition as error:
        return TransitionResult(
            from_state=current_state,
            action=action,
            to_state=current_state,
            allowed=False,
            reason=str(error),
        )
