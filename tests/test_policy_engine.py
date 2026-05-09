from src.policy.policy_engine import evaluate_policy


def test_item_not_received_with_missing_proof_requests_more_evidence():
    case = {
        "case_id": "DSP-TEST-001",
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

    result = evaluate_policy(case)

    assert result.recommended_action == "request_more_evidence"
    assert "proof_of_delivery" in result.required_evidence
    assert "delivery_marked_delivered_but_proof_missing" in result.ambiguity_flags
    assert "final_denial_without_delivery_proof" in result.blocked_actions
    assert result.requires_escalation is False


def test_high_value_high_risk_buyer_case_requires_escalation():
    case = {
        "case_id": "DSP-TEST-002",
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

    result = evaluate_policy(case)

    assert result.recommended_action == "escalate"
    assert result.requires_escalation is True
    assert "high_value_order" in result.risk_flags
    assert "buyer_high_risk" in result.risk_flags
    assert "high_buyer_dispute_frequency" in result.risk_flags
    assert "direct_refund_without_escalation" in result.blocked_actions
    assert "direct_denial_without_escalation" in result.blocked_actions
    assert "auto_refund" in result.blocked_actions


def test_damaged_item_with_photo_evidence_allows_refund_options():
    case = {
        "case_id": "DSP-TEST-003",
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

    result = evaluate_policy(case)

    assert "partial_refund" in result.eligible_actions
    assert "refund_buyer" in result.eligible_actions
    assert result.recommended_action == "partial_refund"
    assert result.requires_escalation is False


def test_policy_ambiguous_return_requires_escalation():
    case = {
        "case_id": "DSP-TEST-004",
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

    result = evaluate_policy(case)

    assert result.recommended_action == "escalate"
    assert result.requires_escalation is True
    assert "category_policy_ambiguous" in result.ambiguity_flags
    assert "escalate" in result.eligible_actions


def test_late_delivery_allows_partial_refund():
    case = {
        "case_id": "DSP-TEST-005",
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

    result = evaluate_policy(case)

    assert "partial_refund" in result.eligible_actions
    assert "seller_warning" in result.eligible_actions
    assert result.recommended_action == "partial_refund"
    assert result.requires_escalation is False
