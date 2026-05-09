from src.workflow.decision_service import validate_reviewer_action


def base_case(status="agent_review"):
    return {
        "case_id": "DSP-TEST-DECISION",
        "status": status,
        "claim_type": "damaged_item",
        "order": {
            "order_value": 42.0,
        },
        "buyer": {
            "risk_tier": "low",
            "prior_disputes_90d": 0,
        },
        "seller": {
            "response_status": "responded",
        },
        "claim": {
            "submitted_evidence": ["buyer_message", "photo_evidence"],
        },
        "delivery": {
            "delivery_status": "delivered",
            "proof_of_delivery": "available",
        },
    }


def item_not_received_missing_proof_case(status="agent_review"):
    return {
        "case_id": "DSP-TEST-MISSING-PROOF",
        "status": status,
        "claim_type": "item_not_received",
        "order": {
            "order_value": 84.5,
        },
        "buyer": {
            "risk_tier": "low",
            "prior_disputes_90d": 1,
        },
        "seller": {
            "response_status": "responded",
        },
        "claim": {
            "submitted_evidence": ["buyer_message"],
        },
        "delivery": {
            "delivery_status": "delivered",
            "proof_of_delivery": "missing",
        },
    }


def high_value_high_risk_case(status="agent_review"):
    return {
        "case_id": "DSP-TEST-HIGH-RISK",
        "status": status,
        "claim_type": "item_not_received",
        "order": {
            "order_value": 420.0,
        },
        "buyer": {
            "risk_tier": "high",
            "prior_disputes_90d": 5,
        },
        "seller": {
            "response_status": "responded",
        },
        "claim": {
            "submitted_evidence": ["buyer_message"],
        },
        "delivery": {
            "delivery_status": "delivered",
            "proof_of_delivery": "available",
        },
    }


def test_valid_partial_refund_with_rationale_is_allowed():
    case = base_case(status="agent_review")

    result = validate_reviewer_action(
        case=case,
        action="partial_refund",
        rationale="Photo evidence confirms damaged item.",
    )

    assert result.allowed is True
    assert result.next_state == "resolved_partial_refund"


def test_resolution_action_without_rationale_is_blocked():
    case = base_case(status="agent_review")

    result = validate_reviewer_action(
        case=case,
        action="partial_refund",
        rationale="",
    )

    assert result.allowed is False
    assert result.next_state == "agent_review"
    assert "Human rationale is required for this action." in result.reasons


def test_refund_from_ready_for_review_is_blocked_by_state_machine():
    case = base_case(status="ready_for_review")

    result = validate_reviewer_action(
        case=case,
        action="refund_buyer",
        rationale="Buyer should be refunded.",
    )

    assert result.allowed is False
    assert result.next_state == "ready_for_review"
    assert any("not allowed" in reason for reason in result.reasons)


def test_denial_without_delivery_proof_is_blocked_by_policy():
    case = item_not_received_missing_proof_case(status="agent_review")

    result = validate_reviewer_action(
        case=case,
        action="deny_claim",
        rationale="Delivery was marked as completed.",
    )

    assert result.allowed is False
    assert result.next_state == "agent_review"
    assert "Final denial is blocked because delivery proof is missing." in result.reasons


def test_high_value_high_risk_case_requires_escalation_before_direct_refund():
    case = high_value_high_risk_case(status="agent_review")

    result = validate_reviewer_action(
        case=case,
        action="refund_buyer",
        rationale="Buyer requested refund.",
    )

    assert result.allowed is False
    assert result.next_state == "agent_review"
    assert any("requires escalation" in reason for reason in result.reasons)


def test_senior_reviewer_refund_after_escalation_is_allowed_when_policy_eligible():
    case = high_value_high_risk_case(status="escalated")

    result = validate_reviewer_action(
        case=case,
        action="senior_reviewer_refund",
        rationale="Senior reviewer approved refund after manual review.",
    )

    assert result.allowed is True
    assert result.next_state == "resolved_refund"


def test_run_policy_evaluation_from_ready_for_review_is_allowed_without_rationale():
    case = base_case(status="ready_for_review")

    result = validate_reviewer_action(
        case=case,
        action="run_policy_evaluation",
        rationale="",
    )

    assert result.allowed is True
    assert result.next_state == "policy_evaluated"

def late_delivery_evidence_pending_case(status="evidence_pending"):
    return {
        "case_id": "DSP-TEST-LATE-DELIVERY",
        "status": status,
        "claim_type": "late_delivery",
        "order": {
            "order_value": 65.99,
        },
        "buyer": {
            "risk_tier": "low",
            "prior_disputes_90d": 0,
        },
        "seller": {
            "response_status": "pending",
        },
        "claim": {
            "submitted_evidence": ["buyer_message"],
        },
        "delivery": {
            "delivery_status": "delivered_late",
            "proof_of_delivery": "available",
        },
    }


def test_escalation_from_evidence_pending_is_allowed_with_rationale():
    case = late_delivery_evidence_pending_case(status="evidence_pending")

    result = validate_reviewer_action(
        case=case,
        action="escalate",
        rationale="Seller response is still pending and SLA risk is increasing.",
    )

    assert result.allowed is True
    assert result.next_state == "escalated"

def escalated_policy_ambiguous_return_case(status="escalated"):
    return {
        "case_id": "DSP-TEST-AMBIGUOUS",
        "status": status,
        "claim_type": "policy_ambiguous_return",
        "order": {
            "order_value": 180.0,
        },
        "buyer": {
            "risk_tier": "medium",
            "prior_disputes_90d": 2,
        },
        "seller": {
            "response_status": "responded",
        },
        "claim": {
            "submitted_evidence": ["buyer_message", "seller_message"],
        },
        "delivery": {
            "delivery_status": "delivered",
            "proof_of_delivery": "available",
        },
    }

def test_senior_reviewer_can_resolve_escalated_ambiguous_return_with_denial():
    case = escalated_policy_ambiguous_return_case(status="escalated")

    result = validate_reviewer_action(
        case=case,
        action="senior_reviewer_deny",
        rationale="Senior reviewer confirmed special category policy does not allow return.",
    )

    assert result.allowed is True
    assert result.next_state == "resolved_denied"

def test_senior_reviewer_can_request_more_evidence_for_escalated_ambiguous_return():
    case = escalated_policy_ambiguous_return_case(status="escalated")

    result = validate_reviewer_action(
        case=case,
        action="request_more_evidence",
        rationale="Additional documentation is required to resolve category eligibility.",
    )

    assert result.allowed is True
    assert result.next_state == "evidence_pending"
