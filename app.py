import json
from pathlib import Path

import streamlit as st


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
        rows.append(
            {
                "Case ID": case["case_id"],
                "Status": case["status"],
                "Claim Type": case["claim_type"],
                "Order Value": format_money(case["order"]),
                "Buyer Risk": case["buyer"]["risk_tier"],
                "Seller Response": case["seller"]["response_status"],
                "Delivery Status": case["delivery"]["delivery_status"],
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
