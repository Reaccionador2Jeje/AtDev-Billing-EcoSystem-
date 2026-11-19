import pytest
from fastapi.testclient import TestClient

from atdev_billing.api import app
from atdev_billing.service import grant_plan, resolve_entitlements


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("ATDEV_BILLING_DB", str(tmp_path / "billing.sqlite3"))
    yield


def test_free_fallback():
    result = resolve_entitlements("customer-1", "joynexa")
    assert result["source"]["plan_id"] == "free"
    assert result["entitlements"]["projects.max"] == 2


def test_active_plan_grants_entitlements():
    grant_plan("customer-1", "joynexa", "plus")
    result = resolve_entitlements("customer-1", "joynexa")
    assert result["source"]["plan_id"] == "plus"
    assert result["entitlements"]["projects.max"] == 15


def test_plan_product_restriction():
    with pytest.raises(ValueError, match="plan_not_available_for_product"):
        grant_plan("customer-1", "walletie", "starter")


def test_unknown_plan_rejected():
    with pytest.raises(ValueError, match="unknown_plan"):
        grant_plan("customer-1", "joynexa", "ultra")


def test_expired_plan_falls_back_to_free():
    grant_plan("customer-1", "joynexa", "plus", "2000-01-01T00:00:00+00:00")
    result = resolve_entitlements("customer-1", "joynexa")
    assert result["source"]["plan_id"] == "free"


def test_catalog_discloses_payments_disabled():
    client = TestClient(app)
    response = client.get("/v1/plans")
    assert response.status_code == 200
    assert response.json()["checkout_enabled"] is False


def test_entitlements_require_service_token(monkeypatch):
    monkeypatch.setenv("ATDEV_BILLING_SERVICE_TOKEN", "test-service-secret")
    client = TestClient(app)
    response = client.post("/v1/entitlements/check", json={
        "customer_id": "customer-1", "product_id": "joynexa"
    })
    assert response.status_code == 401
    response = client.post(
        "/v1/entitlements/check",
        headers={"Authorization": "Bearer test-service-secret"},
        json={"customer_id": "customer-1", "product_id": "joynexa"},
    )
    assert response.status_code == 200
