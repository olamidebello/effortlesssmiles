# Effortless Smiles

**Your smile. Your signature sparkle.**

Full-stack studio booking and marketplace application with the approved purple crystal branding and campaign artwork.

## Included

- Responsive storefront, service filtering and product marketplace with shopping bag.
- Appointment requests, hourly availability, race-safe slot protection, service add-ons, promotions, cancellations, deposit and balance payments.
- Persistent D1 customer, appointment, order, inventory, settings and audit records.
- Server-authorized customer, staff and super admin roles; account suspension and role management.
- Super admin catalog editor, inventory, appointment statuses, order fulfillment, CSV exports, settings, promotions and payment-method controls.
- Stripe hosted Checkout with signed webhook verification and server-side return verification.
- PayPal hosted approval and server-side capture verification, with sandbox/live environment selection.
- Offline payment requests with explicit manual reconciliation. Offline requests are never represented as paid automatically.
- Privacy and terms screens; editable provider-reviewed care and cancellation information.

## Runtime

Node 22+, Vinext/React, Cloudflare Workers and D1. The source preserves the Sites integration and ChatGPT sign-in boundary. Do not expose the raw Worker directly without an equivalent trusted authentication boundary that strips caller-supplied identity headers.

Install with `node scripts/install-ci.mjs` or the Sites dependency helper. Build with `npm run build`. Database SQL migrations live in `drizzle/`; apply in sequence. Production deployment through Sites applies migrations automatically. Follow `scripts/sites-env.mjs` and the starter workflow for local migration state.

## Administrator initialization

The initial publication is owner-private. `OWNER_BOOTSTRAP=private-owner-only` allows the first authenticated visitor, who must be the site owner under the platform's private access policy, to become super admin. Initialize the owner account while private; then remove OWNER_BOOTSTRAP and redeploy before expanding access. Alternatively set ADMIN_EMAIL securely to the verified owner email before first sign-in. Existing roles are never overwritten by bootstrap. Never enable owner bootstrap on a public site.

After sign-in, open **Studio dashboard**. Customers cannot assign their own roles or set payment statuses. Staff can manage appointments and view studio orders; super admins control catalog, settings, roles, and fulfillment.

## Payment configuration

Use secure production runtime secrets, not source files or browser storage:

- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
- PAYPAL_CLIENT_ID
- PAYPAL_CLIENT_SECRET
- PAYPAL_MODE (`sandbox`, default, or `live`)
- ADMIN_EMAIL (optional, verified owner email)

Enable configured gateways in **Studio dashboard → Payments**. Stripe remains disabled until both Stripe secrets are configured. Register `/api/stripe-webhook` for `checkout.session.completed`, `checkout.session.async_payment_succeeded`, and `checkout.session.expired`. Private Sites block unsolicited external webhooks; configure the appropriate authenticated/public provider endpoint before live payment use. Signed-in returns also reconcile Stripe payments by retrieving the session from Stripe. PayPal captures are verified against the provider, currency and exact amount. No live gateway credentials were available during development, so live payment processing has not been tested.

Online refunds/disputes are handled through the merchant provider dashboard. Pending online payments can be resumed or checked from My orders. Fulfillment deducts stock atomically and cannot run twice for the same order. Stock is not reserved during pending checkout; the studio must maintain sufficient inventory and resolve stock shortages before fulfillment.

## Business setup before customer launch

Set the studio address, contact email, service prices, opening hours (America/Chicago), care guidance, cancellation terms, deposits and promotion in Settings. The product prices are proposed prices from supplied references. Products start with zero stock and cannot be purchased until approved and stocked. The shop uses studio pickup; shipping calculation, sales-tax automation, automated email/SMS reminders, multi-seller payouts and native mobile applications are not included in this release. Confirm operational and product details before accepting customer payments.

This publication does not replace the existing effortlesssmiles.afribulkhub.com server or DNS configuration.

## Role demos and mobile companion (0.1.0)

Open `/demo?role=customer`, `/demo?role=staff` or `/demo?role=super_admin`. Each role sees its authorized surface with isolated fixtures; resets and refreshes discard simulated changes. The demo API never accesses the live database or payment providers, and refuses checkout, capture and payment-resume actions. Demo settings cannot connect real gateways. Production authorization remains separate. Demo records contain fictional contact information only.

The `/install` page provides the signed Android development APK, checksum, version, iPhone website-shortcut instructions, and role-demo links. The native Android companion displays the approved branding and opens authorized platform and demo URLs in the system browser/custom tab. This supports normal browser sign-in without sharing credentials with an embedded WebView. It is an internet-dependent companion, with no native offline transactions, background services or push notifications; no Apple App Store or Google Play publication is claimed. The platform remains owner-private until its audience is deliberately changed.

Build: `ANDROID_HOME=/path/to/sdk ECJ_JAR=/path/to/ecj.jar python3 mobile/android/build.py` with Android platform/build-tools 35.0.0 and Java/keytool installed. For compatible updates, restore the private preview keystore and set ES_KEYSTORE and ES_KEY_PASSWORD securely. Never commit keystores. Verify using `apksigner verify --verbose --print-certs`. `public/downloads/release.json` records the exact artifact and certificate hashes. `node --test tests/demo.test.mjs` exercises role boundaries and payment restrictions.

African Apps Store integration is published in its separate repository under `catalog/effortlesssmiles.json`, `static/effortlesssmiles`, and `ansible/deploy-effortlesssmiles-mobile.yml`. The deployment preserves existing catalog visibility and backs up changed store files and database state. A source update alone does not update the running server.

## Olamidepanel / standalone server deployment

Use [the complete deployment guide](docs/OLAMIDEPANEL_DEPLOYMENT.md) and `ansible/deploy-olamidepanel.yml`. The standalone build supplies SQLite and local account adapters instead of Cloudflare D1/ChatGPT sign-in. It installs a dedicated loopback service, private Node runtime, exact-domain Nginx routing, HTTPS, persistent data, release activation, backups, rollback and a JSON status report. It preserves the panel's 8090 port and stops on conflicting vhosts rather than deleting other domains. The hosted Sites build is unchanged. Live server deployment still requires running the playbook on a reachable host with working domain DNS.
