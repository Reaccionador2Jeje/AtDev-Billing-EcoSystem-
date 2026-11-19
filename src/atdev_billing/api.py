"""HTTP API. No checkout or payment-card handling is implemented."""
import os
import secrets
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .catalog import list_plans
from .service import grant_plan, resolve_entitlements
from .storage import cancel_subscription

app = FastAPI(
    title="AtDev Billing API",
    version="0.1.0",
    description="Central plan catalog and server-side entitlement service. Payments are disabled.",
)


class EntitlementRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=128)
    product_id: str = Field(min_length=1, max_length=64)


class GrantRequest(EntitlementRequest):
    plan_id: str = Field(min_length=1, max_length=32)
    expires_at: Optional[datetime] = None


class CancelRequest(BaseModel):
    subscription_id: str = Field(min_length=1, max_length=64)


def require_service_token(authorization: str | None = Header(default=None)):
    expected = os.getenv("ATDEV_BILLING_SERVICE_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="service_auth_not_configured")
    supplied = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid_service_token")


def require_admin_token(x_admin_token: str | None = Header(default=None)):
    expected = os.getenv("ATDEV_BILLING_ADMIN_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="admin_auth_not_configured")
    if not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=401, detail="invalid_admin_token")


@app.get("/health")
def health():
    return {"status": "ok", "service": "atdev-billing", "version": app.version}


@app.get("/v1/plans")
def plans():
    return list_plans()


@app.post("/v1/entitlements/check", dependencies=[Depends(require_service_token)])
def check_entitlements(request: EntitlementRequest):
    return resolve_entitlements(request.customer_id, request.product_id)


@app.post("/v1/admin/grants", dependencies=[Depends(require_admin_token)])
def create_grant(request: GrantRequest):
    try:
        return grant_plan(
            request.customer_id,
            request.product_id,
            request.plan_id,
            request.expires_at.isoformat() if request.expires_at else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/admin/cancel", dependencies=[Depends(require_admin_token)])
def cancel_grant(request: CancelRequest):
    if not cancel_subscription(request.subscription_id):
        raise HTTPException(status_code=404, detail="active_subscription_not_found")
    return {"cancelled": True, "subscription_id": request.subscription_id}
