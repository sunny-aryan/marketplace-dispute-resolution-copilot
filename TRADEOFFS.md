# Product and Architecture Trade-offs

This document explains the main product and architecture decisions behind the Marketplace Dispute Resolution Copilot.

The goal of this project is not to build a production-ready dispute platform. The goal is to demonstrate how an AI-enabled, human-in-the-loop workflow could be designed with realistic constraints: incomplete evidence, policy ambiguity, escalation, reviewer judgment, lifecycle state, auditability, external AI dependency risk, and operational resilience.

---

## 1. AI Assistance vs Automated Decisioning

### Decision

The system uses AI to assist investigation, not to make final dispute decisions.

The AI investigation agent can:

- summarize dispute evidence
- identify contradictions
- highlight missing evidence
- prepare reviewer briefs
- recommend a next action within system boundaries

The AI cannot:

- issue a refund
- deny a claim
- close a case
- compensate a seller
- bypass escalation
- override policy
- delete or rewrite audit history

### Why

Marketplace dispute decisions affect buyer trust, seller trust, refund cost, fraud exposure, and operational accountability. Fully automating final decisions would be risky because evidence may be incomplete or contradictory.

A human reviewer remains accountable for final actions, while deterministic systems validate whether the selected action is allowed.

### Alternative Considered

Allow the AI agent to directly decide outcomes such as refund, denial, or escalation.

### Why Rejected

This would make the system look like an unsafe automation demo rather than a realistic operations product. It would also weaken auditability and make it harder to explain why a decision was made.

### Production Consideration

In production, the AI layer could be used for decision support, reviewer productivity, evidence summarization, and draft communication, but final authority should depend on risk tier, claim type, policy, and reviewer permissions.

---

## 2. Policy Before AI Recommendation

### Decision

The deterministic policy engine evaluates the case before the AI investigation agent generates its recommendation.

The AI receives:

- eligible actions
- blocked actions
- required evidence
- ambiguity flags
- risk flags
- escalation requirements
- current workflow state
- allowed workflow actions

### Why

This ensures that the AI does not invent the decision space. The system defines what is allowed first, and the AI reasons inside those boundaries.

### Alternative Considered

Let the AI analyze the case first, then validate the recommendation afterward.

### Why Rejected

This is less safe because the AI could recommend actions that sound reasonable but violate policy. Even if later blocked, the user experience would be weaker because reviewers may see misleading recommendations.

### Production Consideration

A production system should treat policy and permissions as hard constraints. AI-generated recommendations should be checked both before and after generation, especially in high-risk workflows.

---

## 3. Deterministic Policy Engine vs ML-Based Risk Model

### Decision

The MVP uses deterministic policy rules and simple risk signals rather than a machine learning fraud or risk model.

### Why

The project uses synthetic data, so training or simulating a real ML model would not be credible. Deterministic rules are easier to explain, easier to test, and better suited to governance-heavy workflows.

### Alternative Considered

Build a machine learning model to predict fraud risk or refund likelihood.

### Why Rejected

A model trained on synthetic data would create false sophistication. It would also distract from the main product goal: demonstrating workflow design, human review, escalation, policy control, and auditability.

### Production Consideration

In production, a risk model could be useful, but it should be treated as one signal among many. It should not replace policy, evidence completeness checks, reviewer judgment, or audit requirements.

---

## 4. Workflow State Machine vs Free-form Reviewer Actions

### Decision

The system uses a workflow state machine to control case lifecycle transitions.

Examples:

- `ready_for_review` → `policy_evaluated`
- `policy_evaluated` → `agent_review`
- `agent_review` → `escalated`
- `agent_review` → `resolved_refund`
- `resolved_denied` → `reopened`

### Why

A real dispute workflow cannot allow any action at any time. For example, a case should not move directly from `ready_for_review` to `resolved_refund` without policy evaluation, reviewer validation, and rationale.

The state machine makes the workflow predictable, testable, and auditable.

### Alternative Considered

Let the UI expose all actions and rely on reviewers to choose correctly.

### Why Rejected

That would be unrealistic and unsafe. It would also make the system harder to reason about because workflow constraints would be implicit rather than explicit.

### Production Consideration

A production system would likely include more states, role-based permissions, SLA timers, assignment logic, and appeal-specific transitions.

---

## 5. Reviewer Action Validation vs Direct State Mutation

### Decision

Reviewer actions are validated before they update case state.

The validation layer checks:

- whether the workflow transition is valid
- whether the action is eligible under policy
- whether the action is blocked
- whether escalation is required
- whether human rationale is present

### Why

This prevents invalid or unsafe actions from mutating the case lifecycle. It also creates a natural enforcement point for future AI-generated recommendations.

### Alternative Considered

Allow the UI to directly update case state after a button click.

### Why Rejected

Direct mutation would make the app feel like a demo rather than a controlled workflow system. It would also bypass important product constraints such as rationale, escalation, and policy eligibility.

### Production Consideration

In production, this validation layer would likely also check reviewer role, region, policy version, refund limits, and fraud-risk thresholds.

---

## 6. SQLite Persistence vs Cloud Database

### Decision

The project uses SQLite for local persistence.

SQLite stores:

- case status
- full case JSON
- audit events
- reviewer actions
- investigation events

### Why

SQLite is free, local, easy to run, and sufficient to demonstrate durable workflow state. It avoids unnecessary infrastructure setup while still showing that the product is not a stateless demo.

### Alternative Considered

Use Postgres, Firebase, Supabase, or a managed cloud database.

### Why Rejected

A cloud database would add setup complexity without materially improving the portfolio signal at this stage. The main product value is the workflow model, not database infrastructure.

### Production Consideration

A production system should use a managed relational database such as Postgres, with normalized tables, access control, migrations, backups, and observability.

---

## 7. JSON Blob Case Storage vs Fully Normalized Schema

### Decision

The MVP stores the full case object as a JSON blob in SQLite, while keeping status as a separate column.

### Why

The dispute case object includes nested order, buyer, seller, claim, and delivery evidence. Storing it as JSON keeps the MVP simple and flexible while still allowing persistent state updates.

### Alternative Considered

Normalize case data into separate tables such as orders, buyers, sellers, claims, delivery events, and evidence records.

### Why Rejected

A fully normalized schema would be more realistic but would slow down the project and shift attention toward database modeling rather than workflow/product design.

### Production Consideration

A production version should normalize important entities, especially if teams need analytics, search, reporting, permissions, evidence provenance, or policy-versioned decisions.

---

## 8. Synthetic Data vs Real Marketplace APIs

### Decision

The project uses synthetic dispute cases rather than real marketplace data.

### Why

Real dispute data is private, sensitive, and not publicly available. Synthetic data allows the project to model specific edge cases:

- missing proof of delivery
- buyer-seller disagreement
- high-value orders
- high-risk buyer history
- seller non-response
- late delivery
- policy ambiguity
- escalation and senior review

### Alternative Considered

Use public e-commerce APIs or scraped marketplace data.

### Why Rejected

Public APIs would not provide realistic dispute lifecycle data. Scraped data would create privacy and quality concerns. Neither would improve the core workflow signal.

### Production Consideration

A production system would integrate with order management, seller systems, buyer support messages, delivery tracking, payment/refund systems, and fraud/risk services.

---

## 9. OpenAI Integration vs Fully Deterministic Summaries

### Decision

The system uses OpenAI for bounded investigation when available, with deterministic fallback when unavailable or degraded.

### Why

OpenAI adds realistic AI-enabled workflow behavior: summarization, contradiction detection, missing evidence explanation, and reviewer brief generation.

The fallback ensures the workflow remains usable when the AI service is unavailable.

### Alternative Considered

Use only deterministic summaries.

### Why Rejected

A purely deterministic version would miss the agentic AI / AI-assisted workflow dimension that this project is meant to demonstrate.

### Alternative Considered

Use only OpenAI without fallback.

### Why Rejected

That would make the workflow too dependent on an external AI service and would not demonstrate operational resilience.

### Production Consideration

A production system would need observability, latency controls, cost controls, prompt/version management, structured output validation, retry behavior, and monitoring of AI recommendation quality.

---

## 10. UI-Based Service Degradation Controls vs Manual Config Editing

### Decision

The app exposes AI service health controls in the Streamlit sidebar.

The selected state is persisted in `data/service_health.json`.

### Why

UI controls make degraded behavior easy to demo and screenshot. They also make the dependency boundary visible to reviewers.

### Alternative Considered

Manually edit `data/service_health.json` to simulate degradation.

### Why Rejected

Manual editing works technically but is weaker for a product demo. A reviewer should be able to see and trigger degraded behavior from the app.

### Production Consideration

In production, service health would come from monitoring systems, circuit breakers, status pages, or runtime dependency checks, not manual UI controls.

---

## 11. Escalation as a Safe Workflow Action

### Decision

Escalation is treated differently from refund or denial.

Refund and denial are outcome actions that require stricter policy eligibility. Escalation is a safe workflow-routing action that can be allowed when the state machine permits it and a reviewer provides rationale.

### Why

Escalation increases human oversight and reduces risk. It should not be blocked merely because a specific claim-type policy did not explicitly list escalation as an eligible outcome.

### Alternative Considered

Require escalation to be explicitly eligible under every claim-type policy.

### Why Rejected

That created unrealistic dead ends during testing. Some cases may need escalation because of uncertainty, SLA risk, or reviewer judgment even when escalation is not the default policy recommendation.

### Production Consideration

Production systems should allow escalation paths for ambiguity, risk, customer sensitivity, SLA risk, reviewer uncertainty, and policy exceptions.

---

## 12. Escalated Case Resolution Policy

### Decision

Escalated cases can unlock senior-reviewer resolution paths that frontline reviewers do not have.

For example, an ambiguous return case may initially require escalation. Once escalated, a senior reviewer can request more evidence, deny the claim, or approve partial compensation depending on policy and rationale.

### Why

Escalation should not become a dead-end state. It should move the case to a higher-authority review path with controlled resolution options.

### Alternative Considered

Keep the same policy options regardless of lifecycle state.

### Why Rejected

This made some escalated cases impossible to resolve, which is not realistic for an operations workflow.

### Production Consideration

A production workflow should include role-aware permissions, monetary thresholds, exception handling, and senior-reviewer-specific policy constraints.

---

## 13. Stripe and Shippo as Future Integrations

### Decision

Stripe test mode and carrier/tracking APIs are not included in the core MVP.

### Why

The project’s main goal is to demonstrate dispute workflow design, not payment or logistics integration. Adding too many external APIs too early would increase implementation complexity and distract from the core product signal.

### Alternative Considered

Integrate Stripe test-mode refunds and Shippo tracking immediately.

### Why Rejected

Stripe is useful as a future refund execution boundary, but the current workflow already demonstrates validated reviewer outcomes. Shippo or carrier tracking would add realism for delivery evidence, but synthetic delivery data is sufficient for controlled edge cases.

### Production Consideration

Future versions could add:

- Stripe test-mode refund execution after reviewer approval
- carrier tracking provider abstraction
- refund failure handling
- idempotency keys
- payment audit events
- delivery webhook ingestion

---

## 14. Streamlit UI vs Production Operations Console

### Decision

The project uses Streamlit for the UI.

### Why

Streamlit is fast to build, easy to run locally, and sufficient to demonstrate workflow concepts: queues, case detail, policy evaluation, investigation, reviewer actions, service degradation, and audit trail.

### Alternative Considered

Build a custom React frontend and backend API.

### Why Rejected

A full frontend/backend stack would add engineering overhead without materially increasing the product portfolio signal at this stage.

### Production Consideration

A production version would likely use a dedicated frontend, backend APIs, authentication, role-based permissions, pagination, filters, assignment queues, and observability.

---

## 15. Known Limitations

This prototype intentionally simplifies several areas:

- no authentication or role-based access control
- no real payment/refund execution
- no real carrier API integration
- no real customer or seller messaging
- no policy versioning
- no reviewer assignment or workload routing
- no SLA timers beyond static timestamps
- no real fraud model
- limited synthetic dataset
- Streamlit UI is functional but not a production-grade operations console

These limitations are acceptable for the MVP because the project is designed to demonstrate product architecture, workflow realism, AI boundaries, and trade-off thinking rather than production completeness.