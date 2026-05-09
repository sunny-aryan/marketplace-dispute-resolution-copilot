from dataclasses import dataclass, field

from src.audit.audit_repository import create_audit_event
from src.persistence.case_repository import update_case_status
from src.workflow.decision_service import ActionValidationResult, validate_reviewer_action


@dataclass
class ActionSubmissionResult:
    case_id: str
    action: str
    submitted: bool
    from_status: str
    to_status: str
    reasons: list[str] = field(default_factory=list)
    audit_event: dict | None = None
    validation_result: ActionValidationResult | None = None


def submit_reviewer_action(
    case: dict,
    action: str,
    rationale: str,
    actor: str = "reviewer_001",
) -> ActionSubmissionResult:
    """
    Validate and submit a reviewer action.

    If validation succeeds:
    - update case status
    - create audit event

    If validation fails:
    - do not mutate case state
    - return validation reasons
    """
    validation_result = validate_reviewer_action(
        case=case,
        action=action,
        rationale=rationale,
    )

    from_status = case["status"]

    if not validation_result.allowed:
        return ActionSubmissionResult(
            case_id=case["case_id"],
            action=action,
            submitted=False,
            from_status=from_status,
            to_status=from_status,
            reasons=validation_result.reasons,
            validation_result=validation_result,
        )

    updated_case = update_case_status(
        case_id=case["case_id"],
        new_status=validation_result.next_state,
    )

    audit_event = create_audit_event(
        case_id=case["case_id"],
        actor=actor,
        event_type="reviewer_action_submitted",
        from_status=from_status,
        to_status=updated_case["status"],
        action=action,
        rationale=rationale,
        details={
            "validation_reasons": validation_result.reasons,
            "policy_recommended_action": (
                validation_result.policy_result.recommended_action
                if validation_result.policy_result
                else None
            ),
            "policy_requires_escalation": (
                validation_result.policy_result.requires_escalation
                if validation_result.policy_result
                else None
            ),
        },
    )

    return ActionSubmissionResult(
        case_id=case["case_id"],
        action=action,
        submitted=True,
        from_status=from_status,
        to_status=updated_case["status"],
        reasons=validation_result.reasons,
        audit_event=audit_event,
        validation_result=validation_result,
    )