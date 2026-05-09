import json
from datetime import datetime, timezone

from src.persistence.database import get_connection


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_case(case: dict) -> None:
    """Insert or update a case in SQLite."""
    now = _now_iso()

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT case_id FROM cases WHERE case_id = ?",
            (case["case_id"],),
        ).fetchone()

        if existing:
            connection.execute(
                """
                UPDATE cases
                SET status = ?, case_json = ?, updated_at = ?
                WHERE case_id = ?
                """,
                (
                    case["status"],
                    json.dumps(case),
                    now,
                    case["case_id"],
                ),
            )
        else:
            connection.execute(
                """
                INSERT INTO cases (
                    case_id,
                    status,
                    case_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    case["case_id"],
                    case["status"],
                    json.dumps(case),
                    now,
                    now,
                ),
            )

        connection.commit()


def get_all_cases() -> list[dict]:
    """Return all cases from SQLite."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT case_json
            FROM cases
            ORDER BY case_id
            """
        ).fetchall()

    return [json.loads(row["case_json"]) for row in rows]


def get_case_by_id(case_id: str) -> dict | None:
    """Return one case by ID."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT case_json
            FROM cases
            WHERE case_id = ?
            """,
            (case_id,),
        ).fetchone()

    if row is None:
        return None

    return json.loads(row["case_json"])


def update_case_status(case_id: str, new_status: str) -> dict:
    """
    Update case status in both the status column and JSON blob.

    Returns the updated case.
    """
    case = get_case_by_id(case_id)

    if case is None:
        raise ValueError(f"Case '{case_id}' was not found.")

    case["status"] = new_status

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE cases
            SET status = ?, case_json = ?, updated_at = ?
            WHERE case_id = ?
            """,
            (
                new_status,
                json.dumps(case),
                _now_iso(),
                case_id,
            ),
        )

        connection.commit()

    return case