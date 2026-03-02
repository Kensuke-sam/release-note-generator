from __future__ import annotations

from fastapi.testclient import TestClient


def test_workflow(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "service_name": "checkout-api",
        "environment": "production",
        "change_summary": "Improved payment retry behavior and added dashboard alerts for "
        "failed authorizations.",
        "issue_refs": ["PAY-123", "OPS-88"],
    }
    create_response = client.post(
        "/deployments",
        json=payload,
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    record_id = create_response.json()["id"]
    analysis_response = client.post(
        f"/deployments/{record_id}/draft-note",
        headers=auth_headers,
    )
    assert analysis_response.status_code == 200
    assert analysis_response.json()["risk_level"] == "medium"

    get_response = client.get(
        f"/deployments/{record_id}/note",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
