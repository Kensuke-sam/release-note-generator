from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_protected_route_requires_api_key(client: TestClient) -> None:
    payload = {
        "service_name": "checkout-api",
        "environment": "production",
        "change_summary": "Improved payment retry behavior and added dashboard alerts for "
        "failed authorizations.",
        "issue_refs": ["PAY-123", "OPS-88"],
    }
    response = client.post("/deployments", json=payload)
    assert response.status_code == 401
