# Product Notes

## Project Summary

Marketplace Dispute Resolution Copilot is a human-in-the-loop workflow prototype for resolving buyer-seller marketplace disputes.

The system helps reviewers investigate disputes, understand evidence, apply policy, validate actions, escalate ambiguous cases, and preserve audit history.

The project is designed to demonstrate how AI-enabled workflow automation can be introduced into an operational decision workflow without giving AI unchecked decision authority.

---

## Product Thesis

Marketplace dispute resolution is not just a classification problem or a refund decision problem.

It is a workflow problem involving:

- incomplete evidence
- contradictory signals
- buyer and seller trust
- refund cost
- fraud risk
- SLA pressure
- reviewer judgment
- escalation paths
- auditability
- policy ambiguity

The product thesis is:

> AI should reduce reviewer cognitive load, while deterministic systems preserve control, consistency, and accountability.

---

## Target Users

### 1. Frontline Support Reviewer

A support reviewer handles standard disputes and needs to quickly understand:

- what the buyer is claiming
- what the seller has provided
- what delivery evidence exists
- what actions are allowed
- what actions are blocked
- whether escalation is required

Primary need:

> Resolve common disputes quickly and consistently without missing important evidence or policy constraints.

---

### 2. Senior Reviewer

A senior reviewer handles complex or escalated cases.

These may include:

- high-value orders
- high-risk buyer behavior
- seller-buyer evidence conflict
- policy ambiguous categories
- repeated appeals
- missing evidence
- edge cases requiring exception judgment

Primary need:

> Make defensible decisions in ambiguous cases with clear evidence, rationale, and audit history.

---

### 3. Operations Manager

An operations manager cares about the health and consistency of the dispute workflow.

They need visibility into:

- dispute volume
- escalation rate
- SLA risk
- refund leakage
- reviewer override patterns
- reopened cases
- AI fallback frequency
- policy exception patterns

Primary need:

> Improve dispute operations while maintaining fairness, consistency, and accountability.

---

## Jobs To Be Done

### Reviewer Job

When I open a dispute case,  
I want to quickly understand the evidence, risk signals, policy constraints, and recommended next action,  
so that I can resolve or escalate the case confidently.

### Senior Reviewer Job

When a case is escalated,  
I want to understand why it was escalated, what evidence is conflicting or missing, and what resolution paths remain available,  
so that I can make a defensible decision.

### Operations Manager Job

When dispute outcomes vary across reviewers or case types,  
I want to understand where ambiguity, escalation, AI fallback, or policy exceptions occur,  
so that I can improve workflow quality and reduce inconsistent decisions.

---

## Core Product Principles

### 1. Automate preparation, not accountability

The system helps prepare cases for review, but final outcomes require human rationale and deterministic validation.

### 2. Policy defines the decision space

The policy engine defines eligible actions, blocked actions, required evidence, ambiguity flags, and escalation requirements before AI investigation runs.

### 3. AI operates inside boundaries

The investigation agent can summarize, interpret, and recommend, but only within the boundaries defined by policy and workflow state.

### 4. Escalation should increase control, not create dead ends

Escalated cases should unlock senior-reviewer paths instead of trapping cases in unresolved states.

### 5. Every meaningful action should be auditable

Investigation runs, reviewer actions, state transitions, and rationale should be recorded for later review.

### 6. Degraded mode is part of the product

The workflow should remain usable when the AI service is unavailable or intentionally degraded.

---

## MVP Scope

The MVP includes:

- synthetic dispute cases
- dispute queue
- case detail view
- deterministic policy evaluation
- lifecycle state machine
- reviewer action validation
- SQLite persistence
- audit trail
- OpenAI-powered bounded investigation agent
- deterministic fallback investigation
- UI-based AI service degradation controls
- README screenshots and walkthrough
- trade-off documentation

---

## Out of Scope

The MVP intentionally does not include:

- real payment or refund execution
- real buyer or seller messaging
- real courier or tracking API integration
- role-based authentication
- reviewer assignment queues
- production-grade UI
- real fraud model
- policy versioning
- real marketplace backend integration
- analytics dashboard

These are excluded to keep the project focused on the workflow and governance model.

---

## Workflow Assumptions

The project assumes that:

- dispute cases already exist in the system
- buyer, seller, order, and delivery evidence are available as structured data
- policy rules are deterministic and testable
- reviewers are responsible for final outcomes
- high-risk and high-value cases require stronger human review
- AI service availability is not guaranteed
- audit history matters for buyer/seller trust and operational review

---

## Key Workflow Stages

```text
Case intake
   ↓
Evidence review
   ↓
Deterministic policy evaluation
   ↓
AI-assisted investigation
   ↓
Reviewer action validation
   ↓
State transition
   ↓
Audit event creation
   ↓
Escalation, resolution, or evidence request
```

## Success Metrics

### Workflow Efficiency

| Metric | Why it matters |
|---|---|
| Average resolution time | Measures whether reviewers can resolve disputes faster |
| First-touch resolution rate | Measures how often cases are resolved without repeated back-and-forth |
| Escalation rate | Indicates how often cases require senior review |
| SLA breach rate | Measures operational timeliness |
| Reopen / appeal rate | Indicates potential quality issues in initial decisions |

---

### Decision Quality

| Metric | Why it matters |
|---|---|
| Reviewer override rate | Shows whether recommendations are trusted or frequently corrected |
| Wrong denial rate | Measures customer harm from overly strict decisions |
| Refund leakage | Measures unnecessary refund cost |
| Seller dispute satisfaction | Captures fairness to sellers |
| Buyer dispute satisfaction | Captures customer trust |
| Policy exception rate | Highlights where rules may be unclear or incomplete |

---

### AI Assistance Quality

| Metric | Why it matters |
|---|---|
| Investigation brief usefulness rating | Measures whether AI reduces reviewer cognitive load |
| Missing evidence detection accuracy | Measures whether the system identifies evidence gaps correctly |
| Contradiction detection accuracy | Measures quality of evidence interpretation |
| Recommendation acceptance rate | Indicates reviewer trust in AI-assisted recommendations |
| AI fallback frequency | Tracks dependency reliability and degraded-mode usage |
| Average reviewer time saved | Measures operational value of AI assistance |

---

### Governance and Auditability

| Metric | Why it matters |
|---|---|
| Actions submitted without rationale | Should be near zero |
| Invalid transition attempts | Indicates workflow confusion or UI issues |
| Escalation-to-resolution completion rate | Measures whether escalated cases have viable paths |
| Audit event completeness | Ensures decisions can be reconstructed later |
| Policy-blocked action rate | Shows how often deterministic controls prevent unsafe actions |

---

## Product Risks

### 1. Over-trusting AI recommendations

Reviewers may trust AI-generated summaries too much, especially when the case is complex.

**Mitigation:**

- Label AI output as assistive
- Preserve policy evaluation separately
- Require human rationale
- Audit investigation source and recommendation

---

### 2. Policy rules may be too rigid

A deterministic policy engine can block reasonable edge-case actions if rules are incomplete.

**Mitigation:**

- Support escalation
- Allow senior-reviewer paths
- Capture blocked action attempts
- Review policy exception patterns

---

### 3. Synthetic data may hide real-world complexity

Synthetic cases can demonstrate workflow patterns, but real disputes are messier.

**Mitigation:**

- Include edge cases intentionally
- Document synthetic data limitations
- Design service boundaries for future real integrations

---

### 4. Reviewer workload may shift, not reduce

AI may reduce summarization effort but create extra review or validation overhead.

**Mitigation:**

- Track reviewer time saved
- Monitor recommendation acceptance
- Simplify UI hierarchy
- Reduce unnecessary AI output

---

### 5. Escalation can become a bottleneck

If too many cases are escalated, senior reviewers become overloaded.

**Mitigation:**

- Track escalation rate
- Distinguish mandatory vs optional escalation
- Improve frontline policy clarity
- Add queue prioritization in future versions

---

## Adoption Considerations

For a real marketplace operations team, adoption would depend on:

- Reviewer trust in the system
- Clarity of AI vs policy roles
- Ease of understanding evidence
- Speed compared to existing tools
- Quality of audit trail
- Ability to handle exceptions
- Integration with refund, delivery, and messaging systems
- Alignment with marketplace fairness policies

A rollout should start with decision-support mode, not automated outcomes.

---

## Rollout Approach

### Phase 1: Shadow Mode

Run the copilot alongside existing reviewer workflows.

**Goals:**

- Compare recommendations with reviewer decisions
- Measure summary usefulness
- Identify policy gaps
- Validate missing evidence detection

No customer-impacting actions are automated.

---

### Phase 2: Assisted Review

Allow reviewers to use the system for investigation summaries, policy checks, and rationale support.

**Goals:**

- Reduce handling time
- Improve decision consistency
- Preserve human approval
- Track override reasons

---

### Phase 3: Controlled Workflow Automation

Automate low-risk administrative workflow steps, such as:

- Moving cases to evidence pending
- Generating reviewer briefs
- Logging audit events
- Routing mandatory escalations

Final outcomes still require human approval.

---

## Portfolio Progression: Project 2 vs Project 1

This project is Project 2 in my GitHub product portfolio.

[Project 1: Safe Treasury Copilot](https://github.com/sunny-aryan/safe-treasury-copilot) demonstrated strong deterministic controls around AI-assisted financial proposals.

This project intentionally improves on the main weakness from Project 1: limited workflow depth after proposal generation.

### Improvement areas

| Dimension | Project 1: Safe Treasury Copilot | Project 2: Marketplace Dispute Resolution Copilot |
|---|---|---|
| Workflow depth | Request to proposal | Full case lifecycle |
| Human role | Proposal approver | Active reviewer with rationale and escalation |
| State handling | Limited | Explicit state machine |
| Persistence | Lightweight | SQLite-backed case state and audit trail |
| Ambiguity | Mostly clarification | Evidence ambiguity and policy ambiguity |
| Escalation | Risk-based approval | Senior reviewer workflow path |
| AI role | Parse and assist | Bounded investigation agent |
| Degraded mode | Simulated service fallback | UI-controlled degraded AI mode |
| Auditability | Proposal/audit events | Investigation, action, transition, rationale history |
| Product realism | Strong control model | Richer operational workflow |

The goal of Project 2 is not to be more technically complex for its own sake. The goal is to demonstrate stronger product judgment around messy human workflows, incomplete evidence, handoffs, and accountability.

---

## Open Questions

These questions would need deeper product discovery in a real implementation:

- What evidence do reviewers actually trust most?
- Which dispute types create the most cost or trust damage?
- How often do reviewers override policy recommendations today?
- What is the acceptable balance between buyer protection and seller fairness?
- Which actions can safely be automated, and which require human judgment?
- How should policy exceptions be governed?
- How should AI recommendation quality be monitored over time?
- What level of explanation is sufficient for buyers, sellers, reviewers, and auditors?