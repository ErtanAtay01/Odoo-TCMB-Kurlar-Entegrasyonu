# TCMB Currency Rates

Turkey Central Bank (TCMB) daily currency rates integration for Odoo 19.

## Overview

Fetches exchange rates from TCMB API (`today.xml` and historical `YYYYMM/DDMMYYYY.xml`), stores them in `tcmb.currency.rate`, and syncs to Odoo `res.currency.rate` for accounting use.

## Features

- **TCMB integration**: Daily XML (today.xml) and historical by date
- **Rate types**: Forex buying/selling, banknote buying/selling – configurable in Settings
- **Scheduled update**: Daily cron (default 15:15; time editable in Scheduled Actions)
- **Manual update**: Currencies list button, TCMB menu "Update from TCMB", or TCMB Exchange Rates list button
- **Run History**: Every run (scheduled or manual) logged with chatter; see Accounting > Configuration > TCMB Rates > Run History
- **Last TCMB Sync**: Currencies list column (dd.mm.yyyy HH:mm, 24h)
- **Per-currency auto update**: Only currencies with "TCMB Auto" checked are synced to Odoo; default off
- **Retry on error**: Configurable retries and delay (Settings)
- **Turkey holiday skip**: Configurable; when on, no fetch on Turkey public holidays
- **Historical import**: Date-range wizard (from 16 April 1996); optional sync to Odoo; skip already-imported dates
- **Sync Date to Odoo**: Push one already-imported date to Accounting currencies (manager)
- **Fix cron (log manual runs)**: One-click fix so scheduled/manual cron runs appear in Run History (Odoo 18+)
- **Multi-company**: Rates stored per company

## Installation

1. Copy the module to your Odoo addons directory
2. Restart Odoo
3. Install from Apps menu

**Dependencies**: `requests`, `holidays` (Python). For Docker: use `Dockerfile.odoo` at project root, or `pip install holidays --break-system-packages` in the container.

## Menu (Accounting > Configuration > TCMB Rates)

| Menu item | Description |
|-----------|-------------|
| **Fix cron (log manual runs)** | Update scheduled action so manual/scheduled runs are logged in Run History (run once if needed) |
| **Update from TCMB** | Fetch today’s rates from TCMB and sync to Odoo (logged in Run History) |
| **Exchange Rates** | List of TCMB rates; "Update from TCMB" in header; filter by date/sync |
| **Sync Date to Odoo** | Wizard: pick one date to sync from TCMB data to Accounting (manager) |
| **Import Historical** | Wizard: import TCMB rates for a date range (manager) |
| **Run History** | Log of all TCMB runs with chatter (manager) |

Also: **Accounting > Configuration > Currencies** – "Update from TCMB" button, "TCMB Auto" and "Last TCMB Sync" columns.

## Configuration

- **Settings**: Accounting > Configuration > Settings → Invoicing → TCMB Currency Rates (rate type, retry, holiday skip)
- **Scheduled Action**: Settings > Technical > Automation > Scheduled Actions → TCMB Daily Rate Update (edit time/interval)

## Supported Currencies

All TCMB currencies (USD, EUR, GBP, AUD, CHF, etc.). Only currencies in Odoo `res.currency` with **TCMB Auto** checked are synced to `res.currency.rate`.

## Rate Format

TCMB: 1 USD = X TRY. Odoo `res.currency.rate`: `rate` = TRY per 1 USD (e.g. forex_selling/unit).

## Documentation

- **User manual (EN)**: `docs/USER_MANUAL_EN.md`
- **User manual (TR)**: `docs/USER_MANUAL_TR.md`

## Author

Ertan Atay, 2026

## License

LGPL-3

## Version

19.0.1.0.13
