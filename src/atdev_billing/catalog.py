"""Central, versioned plan catalog. Prices are proposals, not active charges."""
from copy import deepcopy

CATALOG_VERSION = "2026-11-19"

PLANS = {
    "free": {
        "name": "Free",
        "price_clp_monthly": 0,
        "currency": "CLP",
        "billing_interval": "month",
        "description": "Core product functionality remains free.",
        "products": ["*"],
        "entitlements": {
            "projects.max": 2,
            "storage.bytes": 104857600,
            "api.requests.monthly": 1000,
            "support.level": "community",
        },
    },
    "starter": {
        "name": "Starter",
        "price_clp_monthly": 490,
        "currency": "CLP",
        "billing_interval": "month",
        "description": "Entry-level optional hosted conveniences.",
        "products": ["joynexa", "memingo", "atdev_cloud"],
        "entitlements": {
            "projects.max": 5,
            "storage.bytes": 524288000,
            "api.requests.monthly": 5000,
            "support.level": "community",
        },
    },
    "plus": {
        "name": "Plus",
        "price_clp_monthly": 990,
        "currency": "CLP",
        "billing_interval": "month",
        "description": "Expanded limits for optional hosted services.",
        "products": ["joynexa", "memingo", "atdev_cloud", "file_radar"],
        "entitlements": {
            "projects.max": 15,
            "storage.bytes": 2147483648,
            "api.requests.monthly": 25000,
            "support.level": "standard",
        },
    },
    "pro": {
        "name": "Pro",
        "price_clp_monthly": 1990,
        "currency": "CLP",
        "billing_interval": "month",
        "description": "Higher quotas for supported hosted services.",
        "products": ["joynexa", "memingo", "atdev_cloud", "file_radar", "cloudforge"],
        "entitlements": {
            "projects.max": 50,
            "storage.bytes": 10737418240,
            "api.requests.monthly": 100000,
            "support.level": "priority",
        },
    },
}


def list_plans():
    """Return a copy so API consumers cannot mutate the in-process catalog."""
    return {
        "catalog_version": CATALOG_VERSION,
        "currency": "CLP",
        "prices_are_active": False,
        "checkout_enabled": False,
        "plans": [{"id": key, **deepcopy(value)} for key, value in PLANS.items()],
    }


def get_plan(plan_id: str):
    plan = PLANS.get(plan_id)
    return {"id": plan_id, **deepcopy(plan)} if plan else None
