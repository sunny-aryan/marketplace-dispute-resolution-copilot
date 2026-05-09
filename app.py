import json
from dataclasses import asdict
from pathlib import Path

import streamlit as st

from src.policy.policy_engine import evaluate_policy
from src.workflow.decision_service import validate_reviewer_action
from src.workflow.state_machine import get_allowed_actions


DATA_PATH = Path("data/seed_cases.json")


def load_cases():
    """Load synthetic dispute cases from local JSON seed data."""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def format_money(order):
    return f"{order['currency']} {order['order_value']:.2f}"


def build_queue_rows(cases):
    rows = []

    for case in cases:
        policy_result = evaluate_policy(case)

        rows.append(
            {
                "Case ID": case["case_id"],
                "Status": case["status"],
                "Claim Type": case["claim_type"],
                "Order Value": format_money(case["order"]),
                "Buyer Risk": case["buyer"]["risk_tier"],
                "Seller Response": case["seller"]["response_status"],
                "Delivery Status": case["delivery"]["delivery_status"],
                "Recommended Action": policy_result.recommended_action,
                "Escalation Required": policy_result.requires_escalation,
                "SLA Due": case["sla_due_at"],
            }
        )

    return rows


st.set_page_config(
    page_title="Marketplace Dispute Resolution Copilot",
    page_icon="⚖️",
    layout="wide",
)

st.title("Marketplace Dispute Resolution Copilot")

st.markdown(
    """
    A human-in-the-loop workflow prototype for resolving marketplace disputes
    using AI-assisted investigation, deterministic policy checks, lifecycle
    state management, and auditability.
    """
)

st.divider()

cases = load_cases()

st.subheader("Dispute Queue")

st.caption(
    "Synthetic marketplace dispute cases used to model incomplete evidence, "
    "buyer-seller disagreement, risk signals, and lifecycle states."
)

queue_rows = build_queue_rows(cases)
st.dataframe(queue_rows, use_container_width=True, hide_index=True)

st.divider()

selected_case_id = st.selectbox(
    "Select a case to review",
    options=[case["case_id"] for case in cases],
)

selected_case = next(case for case in cases if case["case_id"] == selected_case_id)
policy_result = evaluate_policy(selected_case)

st.subheader(f"Case Detail: {selected_case['case_id']}")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("### Order")
    st.json(selected_case["order"])

    st.markdown("### Buyer")
    st.json(selected_case["buyer"])

    st.markdown("### Seller")
    st.json(selected_case["seller"])

with right_col:
    st.markdown("### Claim")
    st.json(selected_case["claim"])

    st.markdown("### Delivery Evidence")
    st.json(selected_case["delivery"])

    st.markdown("### Current Workflow State")
    st.info(selected_case["status"])

    st.markdown("### Allowed Workflow Actions")
    allowed_actions = get_allowed_actions(selected_case["status"])

    if allowed_actions:
        st.json(allowed_actions)
    else:
        st.warning("No further workflow actions are available from this state.")

st.divider()

st.subheader("Deterministic Policy Evaluation")

policy_left, policy_right = st.columns(2)

with policy_left:
    st.markdown("### Recommended Action")
    st.success(policy_result.recommended_action)

    st.markdown("### Confidence")
    st.info(policy_result.confidence)

    st.markdown("### Escalation Required")
    if policy_result.requires_escalation:
        st.warning("Yes")
    else:
        st.success("No")

    st.markdown("### Eligible Actions")
    st.json(policy_result.eligible_actions)

with policy_right:
    st.markdown("### Blocked Actions")
    st.json(policy_result.blocked_actions)

    st.markdown("### Required Evidence")
    st.json(policy_result.required_evidence)

    st.markdown("### Ambiguity Flags")
    st.json(policy_result.ambiguity_flags)

    st.markdown("### Risk Flags")
    st.json(policy_result.risk_flags)

st.markdown("### Policy Rationale")
st.write(policy_result.policy_rationale)

with st.expander("Raw Policy Result"):
    st.json(asdict(policy_result))

st.divider()

st.subheader("Reviewer Action Validation")

st.caption(
    "This panel validates a proposed reviewer action against workflow state rules, "
    "deterministic policy constraints, and human rationale requirements. "
    "It does not persist state changes yet."
)

available_actions = get_allowed_actions(selected_case["status"])

if not available_actions:
    st.warning("This case has no available workflow actions from its current state.")
else:
    selected_action = st.selectbox(
        "Select proposed agent action",
        options=available_actions,
    )

    rationale = st.text_area(
        "Human rationale",
        placeholder=(
            "Explain why this action is appropriate. Required for resolution, "
            "escalation, and evidence-request actions."
        ),
    )

    if st.button("Validate Decision"):
        decision_result = validate_reviewer_action(
            case=selected_case,
            action=selected_action,
            rationale=rationale,
        )

        if decision_result.allowed:
            st.success(
                f"Decision allowed. Next state: {decision_result.next_state}"
            )
        else:
            st.error("Decision blocked.")

        st.markdown("### Validation Reasons")
        for reason in decision_result.reasons:
            st.write(f"- {reason}")

        with st.expander("Raw Decision Validation Result"):
            st.json(
                {
                    "case_id": decision_result.case_id,
                    "action": decision_result.action,
                    "current_state": decision_result.current_state,
                    "allowed": decision_result.allowed,
                    "next_state": decision_result.next_state,
                    "reasons": decision_result.reasons,
                }
            )

st.divider()

st.subheader("Core Product Principle")

st.markdown(
    """
    > **Automate preparation, not accountability.**

    The system will help agents investigate disputes and prepare recommendations,
    but final resolution decisions remain controlled by deterministic rules and
    human review.
    """
)