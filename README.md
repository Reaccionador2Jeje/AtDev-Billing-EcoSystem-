# AtDev Billing EcoSystem

Central billing-plan catalog and entitlement service for the AtDev project family.

## Current status

**MVP foundation — payments disabled.** This service does not collect money, process cards, create payment-provider sessions, or perform automatic renewals. The CLP amounts in the catalog are planning references only and are not active offers.

The hybrid policy is simple:
- Core open-source software and local/self-hosted use stay free.
- Future paid plans may cover optional AtDev-hosted capacity and convenience services.
- A Billing outage must never remove access to core local functionality.
- Each product must enforce entitlements on its own trusted server, not from frontend plan labels.

## Included

- Central plan catalog with explicit CLP reference prices.
- Product-scoped plan availability and entitlement maps.
- SQLite subscription-grant persistence for development.
- Free-tier fallback when no active grant exists or a grant expires.
- Service-token protected entitlement checks.
- Separate admin-token protected grant and cancellation endpoints.
- Automated tests and GitHub Actions CI.

## Run locally

Python 3.11+ is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
export ATDEV_BILLING_SERVICE_TOKEN="local-service-token"
export ATDEV_BILLING_ADMIN_TOKEN="local-admin-token"
uvicorn atdev_billing.api:app --reload
```

OpenAPI docs are available at `/docs`.

## API

- `GET /health` — health check.
- `GET /v1/plans` — public plan catalog; explicitly reports that checkout is disabled.
- `POST /v1/entitlements/check` — service-token protected entitlement lookup.
- `POST /v1/admin/grants` — admin-token protected manual grant for development/testing.
- `POST /v1/admin/cancel` — admin-token protected cancellation.

Example entitlement request:

```http
POST /v1/entitlements/check
Authorization: Bearer YOUR_SERVICE_TOKEN
Content-Type: application/json

{"customer_id":"demo-user","product_id":"joynexa"}
```

Example admin grant:

```http
POST /v1/admin/grants
X-Admin-Token: YOUR_ADMIN_TOKEN
Content-Type: application/json

{"customer_id":"demo-user","product_id":"joynexa","plan_id":"plus"}
```

## Before production

This MVP is not production-ready. Before exposing it publicly:
1. Replace shared service tokens with per-service credentials, rotation, and audit logs.
2. Integrate AtDev Accounts identity and tenant-scoped authorization.
3. Add database migrations, backups, concurrency testing, and PostgreSQL support.
4. Add idempotency keys and signed webhook verification for a future payment provider.
5. Add rate limiting, monitoring, privacy/retention policy, and security review.
6. Have an adult account owner review payment-provider eligibility, legal/tax obligations, and financial administration before any real-money launch.

Never store card numbers, CVV, bank credentials, or raw payment credentials in this service.
