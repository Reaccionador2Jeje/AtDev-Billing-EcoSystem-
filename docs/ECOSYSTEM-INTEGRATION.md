# AtDev Billing Ecosystem — Integration Boundaries

Status: planning document. This repository needs a defined product and data model before billing features can be safely implemented.

## Decisions required
- Define whether this project handles real-money billing, invoices, subscriptions or internal virtual credits.
- Keep Walletie virtual credits separate from real-money billing and accounting.
- Identify the authoritative customer and product records.
- Document jurisdiction, tax, refund, privacy and provider requirements before processing payments.
- Never store raw payment-card data; use a compliant payment provider if real payments are introduced.

## Safe first milestones
1. Write a product scope and glossary.
2. Define entities and lifecycle states without connecting a live payment provider.
3. Add threat and data-retention review.
4. Create test fixtures using fake transactions only.
5. Require explicit review before any live payment integration.