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

## AI-Assisted Investigation

The project includes a bounded investigation agent that prepares dispute cases for human review.

The investigation agent receives deterministic policy outputs before generating its reviewer brief. This means the agent sees:

- eligible actions
- blocked actions
- required evidence
- ambiguity flags
- risk flags
- escalation requirements
- current workflow state
- allowed workflow actions

The agent can summarize evidence, identify contradictions, highlight missing information, and recommend a next action within system boundaries.

It cannot finalize a refund, denial, case closure, or seller compensation. Final outcomes still require reviewer submission, workflow validation, deterministic policy checks, and audit logging.

If the OpenAI API is unavailable or not configured, the app falls back to a deterministic reviewer brief so the workflow remains usable.

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

4. Create a `.env` file.

```bash
cp .env.example .env
```

Add your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key_here
```

5. Initialize the local SQLite database.

```bash
python scripts/init_db.py
```

6. Run the Streamlit app.

```bash
streamlit run app.py
```

7. Open the local app.
Streamlit will print a local URL in the terminal, usually:

```bash
http://localhost:8501
```

The app uses SQLite for local persistence. The generated database is ignored by Git and can be recreated from `data/seed_cases.json`.