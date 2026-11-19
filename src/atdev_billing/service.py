"""Business rules for plan resolution and subscription entitlements."""
from datetime import datetime, timezone
from uuid import uuid4

from .catalog import get_plan
from .storage import cancel_subscription, find_subscription, save_subscription


def utc_now():
    return datetime.now(timezone.utc)


def grant_plan(customer_id: str, product_id: str, plan_id: str, expires_at=None):
    plan = get_plan(plan_id)
    if not plan:
        raise ValueError("unknown_plan")
    if product_id not in plan["products"] and "*" not in plan["products"]:
        raise ValueError("plan_not_available_for_product")
    now = utc_now().isoformat()
    record = {
        "id": str(uuid4()),
        "customer_id": customer_id,
        "product_id": product_id,
        "plan_id": plan_id,
        "status": "active",
        "starts_at": now,
        "expires_at": expires_at,
        "created_at": now,
    }
    save_subscription(record)
    return record


def resolve_entitlements(customer_id: str, product_id: str):
    record = find_subscription(customer_id, product_id)
    now = utc_now()
    if record and record["expires_at"]:
        expiry = datetime.fromisoformat(record["expires_at"])
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry <= now:
            cancel_subscription(record["id"])
            record = None

    if record:
        plan = get_plan(record["plan_id"])
        source = {"plan_id": record["plan_id"], "subscription_id": record["id"]}
    else:
        plan = get_plan("free")
        source = {"plan_id": "free", "subscription_id": None}

    return {
        "customer_id": customer_id,
        "product_id": product_id,
        "source": source,
        "entitlements": plan["entitlements"],
    }
