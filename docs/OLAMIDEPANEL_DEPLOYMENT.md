# Effortless Smiles on Olamidepanel

This deployment pulls the GitHub source and runs a standalone **production Node server**, with SQLite data and local password accounts. It does not run Wrangler/Vite development servers or depend on Cloudflare D1 or ChatGPT authentication. The existing Sites build remains separate and keeps its platform-managed sign-in. Server and hosted accounts/data are separate; no automatic D1 data migration is performed.

The standalone runtime has been built and exercised locally. The playbook has not been run against your live server from this environment. Actual DNS, certificates, firewall reachability, existing virtual hosts and service ownership are verified during deployment; they cannot be certified in advance.

## Run on the Olamidepanel server

The domain's A record must resolve to this server. Remove stale AAAA records unless IPv6 is configured on this host. Allow inbound TCP 80 and 443 at the hosting provider/firewall. Keep Olamidepanel's own 8090 binding as it is. Do not open the application loopback port publicly.

As root:

```bash
git clone https://github.com/olamidebello/effortlesssmiles.git /opt/effortlesssmiles-installer
bash /opt/effortlesssmiles-installer/deploy/install-olamidepanel.sh
```

On later runs:

```bash
bash /opt/effortlesssmiles-installer/deploy/install-olamidepanel.sh
```

The helper installs only Git, Ansible and prerequisites, pulls with `--ff-only`, and invokes the playbook on localhost. It accepts normal Ansible arguments. For example:

```bash
bash /opt/effortlesssmiles-installer/deploy/install-olamidepanel.sh \
  -e es_domain=effortlesssmiles.afribulkhub.com \
  -e es_admin_email=dobcalldemo@gmail.com
```

From an Ansible control machine, use an edited `ansible/inventory.example.ini` outside the repository:

```bash
ansible-playbook -i /secure/path/olamidepanel.ini \
  ansible/deploy-olamidepanel.yml -e @/secure/path/effortlesssmiles-vars.yml
```

Ansible `--check` is not a complete deployment rehearsal: build files, runtime selection and HTTPS checks depend on earlier tasks. Use a disposable Debian host for a full staging rehearsal.

## Exact paths and ports

| Purpose | Default path or endpoint |
|---|---|
| Source checkout | `/opt/effortlesssmiles/source` |
| Immutable release directories | `/opt/effortlesssmiles/releases/<git-sha>` |
| Active application/document root | `/opt/effortlesssmiles/current` |
| Built public assets | `/opt/effortlesssmiles/current/dist/client` |
| Built server code | `/opt/effortlesssmiles/current/dist/server` |
| Node entrypoint | `/opt/effortlesssmiles/current/deploy/server.mjs` |
| Local Node installation | `/opt/effortlesssmiles/runtime/node-<version>-linux-<architecture>` |
| Private pnpm | `/opt/effortlesssmiles/runtime/pnpm` |
| Build cache | `/var/cache/effortlesssmiles-build` |
| Persistent database | `/var/lib/effortlesssmiles/studio.sqlite3` |
| SQLite WAL/SHM files | Beside `studio.sqlite3`; never delete while the app is running |
| Protected runtime environment | `/etc/effortlesssmiles/runtime.env` |
| Persisted selected port | `/etc/effortlesssmiles/port` |
| Initial owner credentials, root-only | `/etc/effortlesssmiles/bootstrap-admin.json` |
| Systemd unit | `/etc/systemd/system/effortlesssmiles.service` |
| Nginx virtual host | `/etc/nginx/sites-available/effortlesssmiles.conf` |
| Enabled virtual host link | `/etc/nginx/sites-enabled/effortlesssmiles.conf` |
| ACME challenge root | `/var/www/effortlesssmiles-acme` |
| Certificate | `/etc/letsencrypt/live/<domain>/fullchain.pem` and `privkey.pem` |
| Backups | `/var/backups/effortlesssmiles/<timestamp>` |
| Deployment status report | `/var/lib/effortlesssmiles/deploy-report.json` |
| Application log | `journalctl -u effortlesssmiles` |
| Maintenance flag | `/run/effortlesssmiles-maintenance` |
| This document on server | `/opt/effortlesssmiles/current/docs/OLAMIDEPANEL_DEPLOYMENT.md` |
| Application listener | `127.0.0.1:18773` initially; auto-selects 18773–18783 on a new installation if needed |
| Internal render engine | OS-assigned ephemeral **loopback** port, within the same service/process |
| Public website | `https://effortlesssmiles.afribulkhub.com/` |
| Local sign-in / registration | `/login` and `/register` |
| Local health check | `/healthz` |
| Role demos | `/demo?role=customer`, `/demo?role=staff`, `/demo?role=super_admin` |
| Install page / Android APK | `/install` and `/downloads/effortless-smiles-preview.apk` |
| Olamidepanel service | Existing port 8090; not modified |

The deployment uses Nginx reverse proxying. It does not configure a static `root` pointing at an empty repository, use the panel's document directory for private data, or expose SQL files, backups, `.env` files, source code or signing keys. All browser assets and downloads are served by the application production server.

## Administrator access

The initial administrator uses `es_admin_email`, default `dobcalldemo@gmail.com`. A randomly generated password is stored only in `/etc/effortlesssmiles/bootstrap-admin.json` with mode 0600. Read it privately as root on the server, then visit `/login`. Reruns preserve existing account passwords. Local registration always creates customers. Caller-supplied ChatGPT identity headers are stripped and never grant account access.

To change a local account password, run the management command as the service user and supply the email/password JSON through stdin, not shell arguments or repository files:

```bash
sudo -u effortlesssmiles env ES_DATA_DIR=/var/lib/effortlesssmiles \
  /opt/effortlesssmiles/runtime/node-<version>-linux-<architecture>/bin/node \
  /opt/effortlesssmiles/current/deploy/manage.mjs reset-password
```

Pass one JSON object on stdin and close stdin. This invalidates the account's existing sessions. Do not paste passwords into public support logs. No email verification or email-based password recovery is added by this deployment.

## Payment configuration

Add merchant credentials to `/etc/effortlesssmiles/runtime.env` using a root editor. Preserve owner `root`, group `effortlesssmiles`, and mode 0640:

```text
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_MODE=sandbox
```

Restart `effortlesssmiles`, then enable configured methods under Studio dashboard → Payments. Stripe webhook URL is `https://<domain>/api/stripe-webhook`. Validate merchant sandbox and live settings before accepting real payments. Demo checkout, capture and payment-resume operations stay blocked regardless of live gateway configuration. The standalone service intentionally ignores Cloudflare owner-bootstrap/email-role environment settings.

## DNS, routing and port diagnostics

```bash
cat /var/lib/effortlesssmiles/deploy-report.json
cat /etc/effortlesssmiles/port
systemctl status effortlesssmiles --no-pager
journalctl -u effortlesssmiles -n 80 --no-pager
nginx -t
ss -ltnp
```

- **Duplicate `server_name`:** preflight prints the exact conflicting active Nginx file paths. Back up those files and remove only this hostname from the obsolete vhost. The playbook never deletes a multi-domain configuration or disables another site automatically.
- **Wildcard or default vhost:** an exact-domain vhost is installed, then `/.es-deploy-check` is tested locally with the hostname. A wrong response aborts deployment.
- **Occupied application port:** the first install chooses an available reserved loopback port and records it. Later deploys reuse it. Existing service ports are not killed or reassigned.
- **SQLite permissions:** data belongs to `effortlesssmiles:effortlesssmiles`; the code is root-owned. Systemd allows writes only in the persistent data directory. Never move the database into a release directory.
- **Certificate failure:** check A/AAAA, inbound 80/443, existing Nginx validity, ACME limits and Certbot output. The previous application is restored when available. There is no insecure TLS fallback.
- **Build failure:** the current release remains active until the new build succeeds. The private Node installation avoids replacing the panel's system Node version.

## Backups and rollback

Builds happen before cutover. The managed vhost briefly places this application into maintenance mode, then the old service stops before the SQLite backup and migrations. Activation uses an atomic symlink rename. Failed activation restores prior managed config and a pre-migration database snapshot, when present, then restarts the previous release. First-install failure leaves the service disabled and removes its active site link. The report distinguishes `ready` from `failed` and records the backup path.

Existing custom vhosts that predate this maintenance mechanism must be reconciled before the first takeover. Backups remain on-server; arrange encrypted off-server copies separately. Rollback behavior has local logic/tests and syntax checks but has not been exercised against your live systemd/Nginx server. Do not delete old releases/backups until a verified deployment and recovery rehearsal.

## Mobile and Apps Store scope

The existing signed Android companion opens the previously published hosted preview. Moving the web server does not rewrite an already signed APK's target. The server's `/install` download remains that preview artifact; use the responsive server website or a browser home-screen shortcut for this standalone deployment until an APK targeting the server is rebuilt. No iOS App Store binary is included.

The African Apps Store has a separate update playbook in its repository: `ansible/deploy-effortlesssmiles-mobile.yml`. Running this platform deployment does not silently modify the store's database or another service.

## Validation

```bash
node node_modules/vite/bin/vite.js build --config deploy/node-vite.config.ts
node --test tests/standalone.test.mjs
node --test tests/demo.test.mjs tests/demo-api.test.mjs
ansible-playbook -i localhost, -c local --syntax-check ansible/deploy-olamidepanel.yml
```

The standalone integration test uses disposable local data and checks login, customer-only signup, forged identity headers, server-side role checks, conflicting bookings, cancellation, exact checkout totals, offline payment authority, idempotent stock deduction, demo transaction blocking and install/download endpoints. It never calls live payment providers.

### Automatic repair when the domain shows SprintForge or another site

Rerun `bash /tmp/effortless-install.sh` as root. The installer pulls the latest source, backs up foreign Nginx configuration files under `/var/backups/effortlesssmiles/<timestamp>/routing`, and removes only the exact Effortless Smiles hostname from their `server_name` lists. Other hostnames, upstream ports, services, databases and site contents remain intact. An otherwise empty name list becomes the inert `effortlesssmiles-detached.invalid` name. Nginx configuration is validated; edits are restored immediately if validation fails. No reload occurs at this repair step; the deployment later installs and validates the dedicated route before reloading.

The managed route includes IPv4 and IPv6 listeners, obtains HTTPS through Certbot and verifies the exact HTTPS sentinel as well as app health. Existing invalid Nginx configurations and unusual directives that cannot be safely edited stop deployment with diagnostics. This cannot repair DNS or a third-party proxy from the server; point both A and any AAAA records at this server, and purge any external cached wrong-site page. If a later build step fails, rerun after correcting the reported failure; routing backups remain available in the manifest.
