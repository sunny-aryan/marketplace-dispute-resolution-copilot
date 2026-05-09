from dataclasses import dataclass, field


HIGH_VALUE_THRESHOLD = 250.0
MEDIUM_VALUE_THRESHOLD = 75.0
HIGH_BUYER_DISPUTE_THRESHOLD = 4
SELLER_RESPONSE_REQUIRED_CLAIMS = {
    "item_not_received",
    "damaged_item",
    "policy_ambiguous_return",
}


@dataclass
class PolicyResult:
    case_id: str
    eligible_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    ambiguity_flags: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    requires_escalation: bool = False
    recommended_action: str = "manual_review"
    confidence: str = "low"
    policy_rationale: str = ""


def evaluate_policy(case: dict) -> PolicyResult:
    """
    Evaluate deterministic dispute policy rules for a marketplace case.

    This function intentionally does not use AI.
    It produces allowed actions, blocked actions, escalation requirements,
    and policy rationale based on structured case data.
    """
    result = PolicyResult(case_id=case["case_id"])

    claim_type = case["claim_type"]
    order_value = case["order"]["order_value"]
    buyer = case["buyer"]
    seller = case["seller"]
    delivery = case["delivery"]

    _evaluate_order_value(order_value, result)
    _evaluate_buyer_risk(buyer, result)
    _evaluate_seller_response(claim_type, seller, result)
    _evaluate_delivery_evidence(claim_type, delivery, result)
    _evaluate_claim_type(claim_type, case, result)
    _derive_recommendation(result)

    result.policy_rationale = _build_policy_rationale(result)

    return result


def _evaluate_order_value(order_value: float, result: PolicyResult) -> None:
    if order_value >= HIGH_VALUE_THRESHOLD:
        result.risk_flags.append("high_value_order")
        result.requires_escalation = True
        result.blocked_actions.append("direct_refund_without_escalation")
        result.blocked_actions.append("direct_denial_without_escalation")
    elif order_value >= MEDIUM_VALUE_THRESHOLD:
        result.risk_flags.append("medium_value_order")


def _evaluate_buyer_risk(buyer: dict, result: PolicyResult) -> None:
    if buyer["risk_tier"] == "high":
        result.risk_flags.append("buyer_high_risk")
        result.requires_escalation = True
        result.blocked_actions.append("auto_refund")

    if buyer["prior_disputes_90d"] >= HIGH_BUYER_DISPUTE_THRESHOLD:
        result.risk_flags.append("high_buyer_dispute_frequency")
        result.requires_escalation = True


def _evaluate_seller_response(
    claim_type: str,
    seller: dict,
    result: PolicyResult,
) -> None:
    if (
        claim_type in SELLER_RESPONSE_REQUIRED_CLAIMS
        and seller["response_status"] == "pending"
    ):
        result.required_evidence.append("seller_response")
        result.ambiguity_flags.append("seller_response_missing")
        result.eligible_actions.append("request_more_evidence")


def _evaluate_delivery_evidence(
    claim_type: str,
    delivery: dict,
    result: PolicyResult,
) -> None:
    if claim_type != "item_not_received":
        return

    if (
        delivery["delivery_status"] == "delivered"
        and delivery["proof_of_delivery"] == "missing"
    ):
        result.required_evidence.append("proof_of_delivery")
        result.ambiguity_flags.append("delivery_marked_delivered_but_proof_missing")
        result.ambiguity_flags.append("buyer_claim_conflicts_with_delivery_status")
        result.eligible_actions.append("request_more_evidence")
        result.blocked_actions.append("final_denial_without_delivery_proof")

    if (
        delivery["delivery_status"] == "delivered"
        and delivery["proof_of_delivery"] == "available"
    ):
        result.ambiguity_flags.append("buyer_claim_conflicts_with_delivery_status")


def _evaluate_claim_type(claim_type: str, case: dict, result: PolicyResult) -> None:
    if claim_type == "damaged_item":
        submitted_evidence = case["claim"]["submitted_evidence"]

        if "photo_evidence" in submitted_evidence:
            result.eligible_actions.append("partial_refund")
            result.eligible_actions.append("refund_buyer")
        else:
            result.required_evidence.append("photo_evidence")
            result.eligible_actions.append("request_more_evidence")

    elif claim_type == "late_delivery":
        result.eligible_actions.append("partial_refund")
        result.eligible_actions.append("seller_warning")

    elif claim_type == "policy_ambiguous_return":
        result.ambiguity_flags.append("category_policy_ambiguous")

        case_status = case.get("status", "ready_for_review")

        if case_status == "escalated":
            result.eligible_actions.append("request_more_evidence")
            result.eligible_actions.append("partial_refund")
            result.eligible_actions.append("deny_claim")
            result.confidence = "low"
        else:
            result.requires_escalation = True
            result.eligible_actions.append("escalate")

    elif claim_type == "item_not_received":
        result.eligible_actions.append("refund_buyer")
        result.eligible_actions.append("deny_claim")
        result.eligible_actions.append("escalate")


def _derive_recommendation(result: PolicyResult) -> None:
    if result.requires_escalation:
        result.recommended_action = "escalate"
        result.confidence = "high"
        return

    if result.required_evidence:
        result.recommended_action = "request_more_evidence"
        result.confidence = "medium"
        return

    if "category_policy_ambiguous" in result.ambiguity_flags:
        if "request_more_evidence" in result.eligible_actions:
            result.recommended_action = "request_more_evidence"
            result.confidence = "low"
            return

    if "partial_refund" in result.eligible_actions:
        result.recommended_action = "partial_refund"
        result.confidence = "medium"
        return

    if "refund_buyer" in result.eligible_actions:
        result.recommended_action = "refund_buyer"
        result.confidence = "medium"
        return

    result.recommended_action = "manual_review"
    result.confidence = "low"


def _build_policy_rationale(result: PolicyResult) -> str:
    rationale_parts = []

    if result.requires_escalation:
        rationale_parts.append(
            "This case requires escalation due to risk, value, or policy ambiguity."
        )

    if result.required_evidence:
        rationale_parts.append(
            "The case is missing required evidence: "
            + ", ".join(result.required_evidence)
            + "."
        )

    if result.ambiguity_flags:
        rationale_parts.append(
            "Ambiguity flags detected: "
            + ", ".join(result.ambiguity_flags)
            + "."
        )

    if result.risk_flags:
        rationale_parts.append(
            "Risk flags detected: "
            + ", ".join(result.risk_flags)
            + "."
        )

    if not rationale_parts:
        rationale_parts.append(
            "No blocking risk or missing evidence was detected by deterministic policy rules."
        )

    return " ".join(rationale_parts)
