import streamlit as st


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

st.subheader("Project Status")

st.info(
    "Initial project scaffold is running. Next steps: add synthetic dispute cases, "
    "case queue, case detail view, and workflow state model."
)

st.subheader("Core Product Principle")

st.markdown(
    """
    > **Automate preparation, not accountability.**

    The system will help agents investigate disputes and prepare recommendations,
    but final resolution decisions remain controlled by deterministic rules and
    human review.
    """
)
