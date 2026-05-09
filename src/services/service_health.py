import json
from pathlib import Path


SERVICE_HEALTH_PATH = Path("data/service_health.json")
VALID_SERVICE_STATUSES = {"healthy", "degraded"}


def load_service_health() -> dict:
    """Load service health configuration from local JSON."""
    if not SERVICE_HEALTH_PATH.exists():
        return {}

    with SERVICE_HEALTH_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_service_health(service_health: dict) -> None:
    """Persist service health configuration to local JSON."""
    SERVICE_HEALTH_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SERVICE_HEALTH_PATH.open("w", encoding="utf-8") as file:
        json.dump(service_health, file, indent=2)


def get_service_status(service_name: str) -> str:
    """
    Return the configured status for a service.

    Supported status values:
    - healthy
    - degraded

    If the service health file or service key is missing, default to healthy.
    """
    service_health = load_service_health()
    return service_health.get(service_name, "healthy")


def set_service_status(service_name: str, status: str) -> None:
    """Set and persist service health status for a service."""
    if status not in VALID_SERVICE_STATUSES:
        raise ValueError(
            f"Invalid service status '{status}'. "
            f"Expected one of: {sorted(VALID_SERVICE_STATUSES)}"
        )

    service_health = load_service_health()
    service_health[service_name] = status
    save_service_health(service_health)


def is_service_degraded(service_name: str) -> bool:
    """Return True if the service is explicitly configured as degraded."""
    return get_service_status(service_name) == "degraded"