import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.audit.audit_repository import create_audit_event
from src.persistence.case_repository import upsert_case
from src.persistence.database import DATABASE_PATH, initialize_database


SEED_CASES_PATH = Path("data/seed_cases.json")


def load_seed_cases() -> list[dict]:
    with SEED_CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def reset_database() -> None:
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()


def main() -> None:
    reset_database()
    initialize_database()

    cases = load_seed_cases()

    for case in cases:
        upsert_case(case)
        create_audit_event(
            case_id=case["case_id"],
            actor="system",
            event_type="case_seeded",
            from_status=None,
            to_status=case["status"],
            action="seed_case",
            rationale="Case initialized from synthetic seed data.",
            details={
                "source": str(SEED_CASES_PATH),
                "claim_type": case["claim_type"],
            },
        )

    print(f"Initialized database at {DATABASE_PATH}")
    print(f"Seeded {len(cases)} cases.")


if __name__ == "__main__":
    main()