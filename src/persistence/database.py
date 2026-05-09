import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/disputes.db")


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection for the local dispute database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create database tables if they do not already exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                case_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                event_type TEXT NOT NULL,
                from_status TEXT,
                to_status TEXT,
                action TEXT,
                rationale TEXT,
                details_json TEXT,
                FOREIGN KEY(case_id) REFERENCES cases(case_id)
            )
            """
        )

        connection.commit()