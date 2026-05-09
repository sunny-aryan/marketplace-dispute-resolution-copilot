import json
from dataclasses import asdict
from pathlib import Path
from src.agents.investigation_agent import run_investigation

import streamlit as st

from src.audit.audit_repository import get_audit_events_for_case
from src.persistence.case_repository import get_all_cases
from src.persistence.database import DATABASE_PATH
from src.policy.policy_engine import evaluate_policy
from src.workflow.action_service import submit_reviewer_action
from src.workflow.decision_service import validate_reviewer_action
from src.workflow.state_machine import get_allowed_actions


SEED_DATA_PATH = Path("data/seed_cases.json")


def load_cases():
    """Load dispute cases from SQLite."""
    return get_all_cases()


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

if not DATABASE_PATH.exists():
    st.error(
        "Local database not found. Run `python scripts/init_db.py` from the "
        "project root, then restart the Streamlit app."
    )
    st.stop()

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

st.divider()

st.subheader("AI-Assisted Investigation")

st.caption(
    "Runs a bounded investigation after deterministic policy evaluation. "
    "The investigation can summarize evidence, identify contradictions, "
    "highlight missing information, and recommend a next action within system boundaries."
)

if st.button("Run Investigation"):
    investigation_result = run_investigation(selected_case)

    if investigation_result["source"] == "openai":
        st.success("Investigation generated using OpenAI.")
    else:
        st.warning("OpenAI unavailable or not configured. Fallback investigation generated.")

    st.markdown("### Case Summary")
    st.write(investigation_result["case_summary"])

    st.markdown("### Key Evidence")
    for item in investigation_result["key_evidence"]:
        st.write(f"- {item}")

    st.markdown("### Contradictions")
    if investigation_result["contradictions"]:
        for item in investigation_result["contradictions"]:
            st.write(f"- {item}")
    else:
        st.write("No major contradictions identified.")

    st.markdown("### Missing Evidence")
    if investigation_result["missing_evidence"]:
        for item in investigation_result["missing_evidence"]:
            st.write(f"- {item}")
    else:
        st.write("No required evidence gaps identified.")

    st.markdown("### Risk Considerations")
    if investigation_result["risk_considerations"]:
        for item in investigation_result["risk_considerations"]:
            st.write(f"- {item}")
    else:
        st.write("No major risk flags identified.")

    st.markdown("### Recommended Next Action")
    st.info(investigation_result["recommended_next_action"])

    st.markdown("### Confidence")
    st.info(investigation_result["confidence"])

    st.markdown("### Reviewer Brief")
    st.write(investigation_result["reviewer_brief"])

    st.markdown("### Human Review Required")
    st.warning(str(investigation_result["human_review_required"]))

    with st.expander("Raw Investigation Result"):
        st.json(investigation_result)

st.subheader("Reviewer Action Validation")

st.caption(
    "This panel validates a proposed reviewer action against workflow state rules, "
    "deterministic policy constraints, and human rationale requirements. "
    "Validated actions can be submitted to update case state and create an audit event."
)

available_actions = get_allowed_actions(selected_case["status"])

if not available_actions:
    st.warning("This case has no available workflow actions from its current state.")
else:
    selected_action = st.selectbox(
        "Select proposed reviewer action",
        options=available_actions,
    )

    rationale = st.text_area(
        "Human rationale",
        placeholder=(
            "Explain why this action is appropriate. Required for resolution, "
            "escalation, and evidence-request actions."
        ),
    )

    validate_clicked = st.button("Validate Action")

    if validate_clicked:
        validation_result = validate_reviewer_action(
            case=selected_case,
            action=selected_action,
            rationale=rationale,
        )

        if validation_result.allowed:
            st.success(
                f"Action allowed. Next state: {validation_result.next_state}"
            )
        else:
            st.error("Action blocked.")

        st.markdown("### Validation Reasons")
        for reason in validation_result.reasons:
            st.write(f"- {reason}")

        with st.expander("Raw Action Validation Result"):
            st.json(
                {
                    "case_id": validation_result.case_id,
                    "action": validation_result.action,
                    "current_state": validation_result.current_state,
                    "allowed": validation_result.allowed,
                    "next_state": validation_result.next_state,
                    "reasons": validation_result.reasons,
                }
            )

    submit_clicked = st.button("Submit Action")

    if submit_clicked:
        submission_result = submit_reviewer_action(
            case=selected_case,
            action=selected_action,
            rationale=rationale,
        )

        if submission_result.submitted:
            st.success(
                f"Action submitted. Case moved from "
                f"{submission_result.from_status} to {submission_result.to_status}."
            )
            st.info("Refresh or reselect the case to view updated state.")
        else:
            st.error("Action was not submitted.")

        st.markdown("### Submission Reasons")
        for reason in submission_result.reasons:
            st.write(f"- {reason}")

        if submission_result.audit_event:
            with st.expander("Created Audit Event"):
                st.json(submission_result.audit_event)

st.divider()

st.subheader("Audit Trail")

audit_events = get_audit_events_for_case(selected_case["case_id"])

if not audit_events:
    st.info("No audit events recorded for this case yet.")
else:
    for event in audit_events:
        st.markdown(
            f"**{event['event_type']}** — {event['timestamp']}  \n"
            f"Actor: `{event['actor']}`  \n"
            f"Action: `{event['action']}`  \n"
            f"State: `{event['from_status']}` → `{event['to_status']}`"
        )

        if event["rationale"]:
            st.write(f"Rationale: {event['rationale']}")

        with st.expander(f"Audit details: {event['event_id']}"):
            st.json(event)

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