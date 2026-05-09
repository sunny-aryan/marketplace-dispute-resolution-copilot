# Marketplace Dispute Resolution Copilot

A human-in-the-loop workflow prototype for marketplace dispute resolution.

This project explores how AI-enabled workflow automation can support support agents and trust & safety reviewers in resolving buyer-seller disputes with incomplete, conflicting, or ambiguous evidence.

## Product Goal

The goal is not to build an autonomous AI dispute resolver.

The goal is to build a workflow system where AI helps with investigation, summarization, missing evidence detection, reviewer brief generation, and recommendation drafting, while deterministic policy checks, lifecycle states, and human review govern final decisions.

## Why This Project Exists

Marketplace disputes are operationally complex. Agents often need to review fragmented evidence across buyer claims, seller responses, delivery events, order history, and marketplace policy.

Poor dispute resolution can lead to:

- inconsistent outcomes
- unnecessary refunds
- unfair seller treatment
- poor buyer experience
- weak auditability
- high support cost

This prototype demonstrates how a product leader might design an AI-assisted dispute workflow with real-world constraints.

## Initial Scope

The first version will include:

- Streamlit-based internal operations UI
- synthetic dispute cases
- case queue
- case detail view
- AI-assisted investigation
- deterministic policy checks
- lifecycle states
- human review and override
- audit trail
- service degradation handling

## Product Principle

> Automate preparation, not accountability.

AI can help prepare the case for review, but final dispute outcomes require human approval and deterministic guardrails.

## Planned Architecture

```text
Streamlit UI
   ↓
Case Orchestrator
   ↓
Dispute Investigation Agent
   ↓
Tool Registry
   ├── Evidence Service
   ├── Buyer History Service
   ├── Seller History Service
   ├── Delivery Evidence Service
   ├── Policy Engine
   ├── Recommendation Service
   └── Audit Service
   ↓
Persistence Layer
```

## How to Run Locally

1. Clone the repository.

```bash
git clone https://github.com/sunny-aryan/marketplace-dispute-resolution-copilot.git
cd marketplace-dispute-resolution-copilot
```

2. Create a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Run the Streamlit app.

```bash
streamlit run app.py
```

5. Open the local app.
Streamlit will print a local URL in the terminal, usually:

```bash
http://localhost:8501
```
