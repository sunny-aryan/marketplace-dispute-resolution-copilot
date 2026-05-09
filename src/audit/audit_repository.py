import json
import uuid
from datetime import datetime, timezone

from src.persistence.database import get_connection


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_audit_event(
    case_id: str,
    actor: str,
    event_type: str,
    from_status: str | None = None,
    to_status: str | None = None,
    action: str | None = None,
    rationale: str | None = None,
    details: dict | None = None,
) -> dict:
    """Create and persist an audit event."""
    event = {
        "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
        "case_id": case_id,
        "timestamp": _now_iso(),
        "actor": actor,
        "event_type": event_type,
        "from_status": from_status,
        "to_status": to_status,
        "action": action,
        "rationale": rationale,
        "details": details or {},
    }

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO audit_events (
                event_id,
                case_id,
                timestamp,
                actor,
                event_type,
                from_status,
                to_status,
                action,
                rationale,
                details_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["case_id"],
                event["timestamp"],
                event["actor"],
                event["event_type"],
                event["from_status"],
                event["to_status"],
                event["action"],
                event["rationale"],
                json.dumps(event["details"]),
            ),
        )

        connection.commit()

    return event


def get_audit_events_for_case(case_id: str) -> list[dict]:
    """Return audit events for a case, oldest first."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                event_id,
                case_id,
                timestamp,
                actor,
                event_type,
                from_status,
                to_status,
                action,
                rationale,
                details_json
            FROM audit_events
            WHERE case_id = ?
            ORDER BY timestamp ASC
            """,
            (case_id,),
        ).fetchall()

    events = []

    for row in rows:
        events.append(
            {
                "event_id": row["event_id"],
                "case_id": row["case_id"],
                "timestamp": row["timestamp"],
                "actor": row["actor"],
                "event_type": row["event_type"],
                "from_status": row["from_status"],
                "to_status": row["to_status"],
                "action": row["action"],
                "rationale": row["rationale"],
                "details": json.loads(row["details_json"] or "{}"),
            }
        )

    return events