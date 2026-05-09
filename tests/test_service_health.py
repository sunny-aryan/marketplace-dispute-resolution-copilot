import json

from src.services import service_health


def test_missing_service_health_file_defaults_to_healthy(tmp_path, monkeypatch):
    fake_path = tmp_path / "missing_service_health.json"

    monkeypatch.setattr(service_health, "SERVICE_HEALTH_PATH", fake_path)

    assert service_health.get_service_status("ai_investigation_service") == "healthy"
    assert service_health.is_service_degraded("ai_investigation_service") is False


def test_missing_service_key_defaults_to_healthy(tmp_path, monkeypatch):
    fake_path = tmp_path / "service_health.json"
    fake_path.write_text(json.dumps({}), encoding="utf-8")

    monkeypatch.setattr(service_health, "SERVICE_HEALTH_PATH", fake_path)

    assert service_health.get_service_status("ai_investigation_service") == "healthy"
    assert service_health.is_service_degraded("ai_investigation_service") is False


def test_degraded_service_is_detected(tmp_path, monkeypatch):
    fake_path = tmp_path / "service_health.json"
    fake_path.write_text(
        json.dumps({"ai_investigation_service": "degraded"}),
        encoding="utf-8",
    )

    monkeypatch.setattr(service_health, "SERVICE_HEALTH_PATH", fake_path)

    assert service_health.get_service_status("ai_investigation_service") == "degraded"
    assert service_health.is_service_degraded("ai_investigation_service") is True


def test_healthy_service_is_not_degraded(tmp_path, monkeypatch):
    fake_path = tmp_path / "service_health.json"
    fake_path.write_text(
        json.dumps({"ai_investigation_service": "healthy"}),
        encoding="utf-8",
    )

    monkeypatch.setattr(service_health, "SERVICE_HEALTH_PATH", fake_path)

    assert service_health.get_service_status("ai_investigation_service") == "healthy"
    assert service_health.is_service_degraded("ai_investigation_service") is False

def test_set_service_status_persists_value(tmp_path, monkeypatch):
    fake_path = tmp_path / "service_health.json"

    monkeypatch.setattr(service_health, "SERVICE_HEALTH_PATH", fake_path)

    service_health.set_service_status(
        "ai_investigation_service",
        "degraded",
    )

    assert service_health.get_service_status("ai_investigation_service") == "degraded"
    assert service_health.is_service_degraded("ai_investigation_service") is True

def test_invalid_service_status_raises_error(tmp_path, monkeypatch):
    fake_path = tmp_path / "service_health.json"

    monkeypatch.setattr(service_health, "SERVICE_HEALTH_PATH", fake_path)

    try:
        service_health.set_service_status(
            "ai_investigation_service",
            "offline",
        )
        assert False, "Expected ValueError for invalid service status."
    except ValueError as error:
        assert "Invalid service status" in str(error)

