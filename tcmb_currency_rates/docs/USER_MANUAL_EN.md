# TCMB Currency Rates – User Manual (English)

## 1. Introduction

The **TCMB Currency Rates** module connects Odoo 19 to the Turkish Central Bank (TCMB) daily exchange rate service. It downloads official rates, stores them in the module’s own table, and can sync selected rates into Odoo’s accounting currencies. You can update today’s rates manually or on a schedule, and you can import historical rates for past dates.

---

## 2. Where to Find TCMB

- **Main menu**: **Accounting** → **Configuration** → **TCMB Rates**
- **Currencies**: **Accounting** → **Configuration** → **Currencies** (button and columns for TCMB)
- **Settings**: **Accounting** → **Configuration** → **Settings** → Invoicing section → **TCMB Currency Rates**
- **Scheduled action**: **Settings** → **Technical** → **Automation** → **Scheduled Actions** → TCMB Daily Rate Update

---

## 3. TCMB Rates Menu (Accounting > Configuration > TCMB Rates)

### 3.1 Fix cron (log manual runs)

- **What it does**: Updates the scheduled action’s code so that when you run the TCMB cron manually (or when it runs automatically), each run is recorded in **Run History** with chatter.
- **When to use**: Run **once** if manual runs of the scheduled action do not appear in Run History (typical after upgrading or on Odoo 18+ where the code is stored on the server action).
- **Access**: Manager (Accounting).
- **Result**: A success message; the next manual or automatic cron run will create an entry in Run History.

---

### 3.2 Update from TCMB

- **What it does**: Fetches **today’s** rates from TCMB, saves them in **Exchange Rates**, syncs them to Odoo **Currencies** for those with **TCMB Auto** enabled, and creates a **Run History** entry with chatter.
- **When to use**: Whenever you want to refresh today’s rates without waiting for the scheduled run.
- **Access**: Users with access to the TCMB menu.
- **Result**: A notification (Success / Skipped on Turkey holiday / Error). Run is visible in **Run History**.

---

### 3.3 Exchange Rates

- **What it does**: Opens the list of **TCMB exchange rates** (all fetched rates: date, currency, forex/banknote rates, sync status).
- **Header button**: **Update from TCMB** – same as the menu item above; run is logged in Run History.
- **Columns**: Rate Type in Use, Date, Currency Code/Name, Unit, Forex Buying/Selling, Banknote rates, Effective Rate, Synced to Odoo.
- **Filters**: By currency, date, Synced / Not Synced.
- **Form**: View details of one rate; **Sync to Odoo** appears if that rate is not yet synced (for currencies with TCMB Auto).
- **Note**: You cannot create or edit rates from the list; they come from TCMB or the Import Historical wizard.

---

### 3.4 Sync Date to Odoo

- **What it does**: Wizard to sync **one chosen date** from existing TCMB data into Odoo **Currencies**. Only currencies with **TCMB Auto** checked are updated.
- **When to use**: After you have imported historical data and want to push a specific date (e.g. 1 February) to Accounting.
- **Access**: Manager.
- **Steps**: Open the wizard → choose **Rate Date** → **Sync**.
- **Note**: TCMB data for that date must already exist (e.g. from **Import Historical**).

---

### 3.5 Import Historical

- **What it does**: Imports TCMB rates for a **date range**. Data is taken from TCMB’s historical URLs (`YYYYMM/DDMMYYYY.xml`). You can skip weekends and Turkey holidays, skip dates already imported, and optionally sync imported dates to Odoo.
- **When to use**: To backfill past rates (e.g. for reporting or past invoices).
- **Access**: Manager.
- **Fields**:
  - **Start Date** / **End Date**: Range to import (from 16 April 1996 onward).
  - **Skip Weekends & Holidays**: If checked, weekends and Turkey public holidays are not fetched (default: on).
  - **Skip dates already imported**: If checked, dates that already have TCMB data are not fetched again (default: on).
  - **Sync to Odoo currencies**: If checked, after importing each date, rates are pushed to Odoo Currencies for currencies with **TCMB Auto** (default: on).
- **Actions**: **Import** (starts import; wizard closes on success), **Close** (cancel).
- **Result**: Notification with created/updated/skipped counts; data in **Exchange Rates** and optionally in **Currencies**.

---

### 3.6 Run History

- **What it does**: Shows a **log of every TCMB update run** (scheduled or manual). Each record has chatter with the result (success/skipped/error and details).
- **Columns**: Run Date, Run Type (Scheduled / Manual), Result (Success / Skipped / Error), Rates Created, Rates Updated, TCMB Rate Date, Details.
- **Form**: Full details and chatter (messages with run outcome).
- **Access**: Read for Accounting users; full access for managers.
- **Use**: Audit trail and troubleshooting (e.g. why a run was skipped or failed).

---

## 4. Currencies (Accounting > Configuration > Currencies)

- **Update from TCMB** (button): Same as **TCMB Rates** → **Update from TCMB**; run is logged in Run History.
- **TCMB Auto** (column): Check to include this currency in TCMB sync. Only checked currencies get their Odoo rate updated from TCMB. Default: unchecked.
- **Last TCMB Sync** (column): Last time an “Update from TCMB” (or equivalent) run completed, in **dd.mm.yyyy HH:mm** (24h), in your timezone.
- **Form**: In the TCMB group, **Auto Update from TCMB** is the same as the list toggle.

---

## 5. Settings (Accounting > Configuration > Settings)

In the **Invoicing** section, block **TCMB Currency Rates**:

- **TCMB rate for Odoo sync**: Which TCMB rate to use when syncing to Currencies – **Forex Buying**, **Forex Selling** (default), **Banknote Buying**, **Banknote Selling**.
- **Retry on error**: **Retry count** (e.g. 3) and **Retry delay (minutes)** (e.g. 5). After a failed fetch, the module retries this many times with this delay; if all fail, an error is shown.
- **Turkey holiday skip**: If checked, no TCMB fetch is performed on Turkey public holidays (TCMB closed). Manual/cron runs show “Skipped”.

Saving Settings re-syncs Odoo Currencies from **existing** TCMB data (no new fetch) when the rate type is changed.

---

## 6. Scheduled Action (Cron)

- **Where**: **Settings** → **Technical** → **Automation** → **Scheduled Actions**.
- **Name**: e.g. “TCMB: Daily Rate Update (15:15)” or “(15:30)” if you changed it.
- **What it does**: Runs the same logic as **Update from TCMB** (fetch today, sync to Odoo, create Run History entry). Run type is **Scheduled** in Run History.
- **Manual run**: Open the scheduled action → **Run Manually**. After using **Fix cron (log manual runs)** once, this will appear in Run History.
- **Edit**: You can change execution time (e.g. 15:30), interval, or deactivate it.

---

## 7. Feature Summary

| Feature | Description |
|--------|-------------|
| **Daily update** | Fetch today’s TCMB rates; sync to Odoo for currencies with TCMB Auto. |
| **Historical import** | Import a date range (from 16 Apr 1996); optional sync to Odoo; skip weekends/holidays and already-imported dates. |
| **Sync one date** | Push one already-imported date to Odoo Currencies (Sync Date to Odoo wizard). |
| **Run History** | All runs (scheduled and manual) logged with chatter. |
| **Fix cron** | One-click update so scheduled/manual cron runs are logged (menu: Fix cron (log manual runs)). |
| **Rate type** | Choose which TCMB rate (forex/banknote buy/sell) is used for Odoo. |
| **Per-currency** | Only currencies with TCMB Auto are synced to Odoo. |
| **Retry** | Configurable retries and delay on fetch failure. |
| **Holiday skip** | Optional skip on Turkey public holidays. |
| **Multi-company** | TCMB rates and Run History are per company where applicable. |

---

## 8. Typical Workflows

1. **First use**: Enable **TCMB Auto** on the currencies you need (e.g. USD, EUR) in Currencies. Optionally set **Turkey holiday skip** and **Retry** in Settings. Run **Update from TCMB** once (from menu or Currencies). Check **Run History** and **Exchange Rates**.
2. **Daily**: Rely on the scheduled action, or run **Update from TCMB** manually. Check **Last TCMB Sync** and **Run History** if needed.
3. **Historical**: Open **Import Historical**, set date range, keep **Sync to Odoo currencies** and **Skip dates already imported** as needed, run **Import**. Use **Sync Date to Odoo** for a single date if you did not sync during import.
4. **Cron not logging**: Run **Fix cron (log manual runs)** once from the TCMB menu, then run the scheduled action manually and confirm an entry in Run History.

---

## 9. Troubleshooting

- **No Run History for manual cron run**: Use **Fix cron (log manual runs)** once (Odoo 18+).
- **“TCMB cron not found”**: Ensure the TCMB scheduled action exists (install/upgrade module). Fix cron finds by name (15:15, 15:30) or “TCMB%”.
- **Rates not in Currencies**: Enable **TCMB Auto** for that currency; run **Update from TCMB** or **Sync Date to Odoo** for the relevant date.
- **Holiday / skip**: On Turkey public holidays, runs show “Skipped” when **Turkey holiday skip** is on. No fetch is made.
- **Errors**: Check Run History chatter and the on-screen message; adjust **Retry** and **Retry delay** in Settings if the problem is temporary (e.g. network).

---

*TCMB Currency Rates for Odoo 19 – User Manual (English). Version 19.0.1.0.13.*
