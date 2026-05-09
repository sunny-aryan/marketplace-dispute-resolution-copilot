import pytest

from src.workflow.state_machine import (
    InvalidStateTransition,
    get_allowed_actions,
    get_next_state,
    validate_transition,
)


def test_ready_for_review_can_move_to_policy_evaluated():
    next_state = get_next_state("ready_for_review", "run_policy_evaluation")

    assert next_state == "policy_evaluated"


def test_policy_evaluated_can_move_to_agent_review():
    next_state = get_next_state("policy_evaluated", "start_agent_review")

    assert next_state == "agent_review"


def test_agent_review_can_move_to_escalated():
    next_state = get_next_state("agent_review", "escalate")

    assert next_state == "escalated"


def test_agent_review_can_resolve_refund():
    next_state = get_next_state("agent_review", "refund_buyer")

    assert next_state == "resolved_refund"


def test_resolved_denied_can_be_reopened_by_buyer_appeal():
    next_state = get_next_state("resolved_denied", "buyer_appeal")

    assert next_state == "reopened"


def test_closed_case_has_no_allowed_actions():
    allowed_actions = get_allowed_actions("closed")

    assert allowed_actions == []


def test_invalid_transition_raises_exception():
    with pytest.raises(InvalidStateTransition):
        get_next_state("closed", "refund_buyer")


def test_validate_transition_returns_disallowed_result_for_invalid_action():
    result = validate_transition("ready_for_review", "refund_buyer")

    assert result.allowed is False
    assert result.to_state == "ready_for_review"
    assert "not allowed" in result.reason


def test_validate_transition_returns_allowed_result_for_valid_action():
    result = validate_transition("agent_review", "partial_refund")

    assert result.allowed is True
    assert result.from_state == "agent_review"
    assert result.to_state == "resolved_partial_refund"
