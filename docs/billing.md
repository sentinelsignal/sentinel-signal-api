# Billing Flow (High Level)

Sentinel Signal uses usage-based billing for API scoring calls.

## Billing Unit

- Billable unit: successful scoring responses (`HTTP 2xx`) from scoring endpoints.
- Non-billable: rejected authentication requests, validation failures, and rate-limit rejections.

## Plans

- Free: monthly call allowance with rate limits.
- Paid usage: metered billing by call volume.
- Enterprise: custom limits and commercial terms.

## Flow

1. Customer obtains API credentials.
2. Client sends scoring requests.
3. Backend records usage by key and workflow.
4. Usage is reported to billing systems in batches.
5. Monthly usage is invoiced.

## Payment State Handling

- If billing is not active for a paid account, requests can be blocked until resolved.
- Rate limits and plan enforcement are applied per key.

## Reconciliation

Usage reconciliation compares metered usage with billing-reported usage and flags drift for operational review.

## Public Secret-Safety Policy

This repository never publishes real Stripe identifiers or secrets.
Use placeholders only in examples and docs:

- `STRIPE_PRODUCT_ID=prod_xxx`
- `STRIPE_PRICE_ID=price_live_xxx`
- `STRIPE_WEBHOOK_SECRET=whsec_xxx`
- `STRIPE_PUBLISHABLE_KEY=pk_live_xxx`
