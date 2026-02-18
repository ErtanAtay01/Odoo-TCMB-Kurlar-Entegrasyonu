# Changelog

All notable changes to the TCMB Currency Rates module are documented in this file.

## [19.0.1.0.13] - 2026-02-18

### Added

- **Run History (chatter)**: Every TCMB update (scheduled or manual) is logged in Accounting > Configuration > TCMB Rates > Run History. Each run has chatter with result (success/skipped/error, counts). Manager-only.
- **Sync to Odoo for historical import**: Import Historical wizard option "Sync to Odoo currencies" (default on) pushes imported rates to Accounting for currencies with TCMB Auto Update. Standalone "Sync Date to Odoo" wizard to sync one already-imported date.
- **Skip dates already imported**: Import Historical option to skip dates that already have TCMB data (saves requests, no overwrite).
- **Fix cron (log manual runs)**: Menu action to update the scheduled action code so manual/scheduled runs are logged (Odoo 18+ stores code on server action). Finds cron by name (15:15, 15:30) or TCMB%.
- **Import wizard**: Auto-close after success; "Close" button; result notification with next action to close.

### Changed

- **List "Update from TCMB"**: Now uses same logging as menu/Currencies; creates Run History entry.
- **Cron/post_init**: Update delegated ir.actions.server code when cron already exists; search by cron_name/name (15:15, 15:30) or TCMB%.

## [19.0.1.0.12] - 2026-02-18

### Added

- **Historical rates import**: Wizard (Accounting > Configuration > TCMB Rates > Import Historical) to import TCMB rates for a date range. Skips weekends and optionally Turkey holidays; TCMB URL format YYYYMM/DDMMYYYY; bulk create/update; manager-only access.

## [19.0.1.0.11] - 2026-02-18

### Added

- **Last TCMB Sync format**: Display as dd.mm.yyyy HH:mm (24h), user timezone
- **Optional holidays**: Module loads without `holidays`; holiday skip disabled until installed. `Dockerfile.odoo` and requirements.txt for Docker

### Changed

- **Last TCMB Sync**: Uses formatted Char field in list (dd.mm.yyyy HH:mm)

## [19.0.1.0.10] - 2026-02-18

### Added

- **Holiday skip configurable**: Setting to enable/disable Turkey holiday skip (default: on)

### Changed

- **Better error messages**: TCMB-specific hints for timeout, connection, HTTP 404/5xx, SSL, XML parse; retry failure mentions Settings

## [19.0.1.0.9] - 2026-02-18

### Added

- **Turkey holiday skip**: On Turkey public holidays, update is skipped (TCMB closed); manual and cron show "Skipped" message. Uses `holidays` package for Turkey (TR) calendar.

## [19.0.1.0.8] - 2026-02-18

### Added

- **Retry on error**: Configurable retry (Settings: retry count, delay in minutes). On TCMB fetch failure, retries up to X times with Y minutes between; shows error notification after all attempts fail. Default: 3 retries, 5 minutes.

## [19.0.1.0.7] - 2026-02-18

### Added

- **Auto Update from TCMB**: Per-currency checkbox; only currencies with "Auto Update from TCMB" checked are synced. Default: off; user toggles on for currencies to include.
- **TCMB Auto column**: Currencies list shows toggle; form view has TCMB group with the checkbox.

## [19.0.1.0.6] - 2026-02-18

### Changed

- **Last TCMB Sync column**: Visible by default in Currencies list; shows query date (when Update from TCMB was last run), distinct from Odoo "Last Update" (TCMB rate date)
- **Rate type display**: TCMB Exchange Rates list shows "Rate Type in Use" column (Forex Buying, etc.); Currencies list keeps original Odoo labels

## [19.0.1.0.5] - 2026-02-18
- **Immediate re-sync on rate type change**: When TCMB rate type is changed in Settings and saved, res.currency.rate is immediately updated from existing TCMB Exchange Rates data (no new fetch); Currencies list shows correct rates after Save
- **Validation fix**: Filter out TCMB records with zero for selected rate type (Banknote Buying/Selling often 0 for some currencies) before sync; prevents "currency rate must be strictly positive" error

## [19.0.1.0.4] - 2026-02-18

### Added

- **Last TCMB update display**: Currencies list now shows when TCMB rates were last fetched and synced
  - New column "Last TCMB Update" (optional, enable via column selector)
  - Stored in ir.config_parameter, updated on every successful sync (manual button, menu action, cron)
  - Computed field `tcmb_last_update` on res.currency

## [19.0.1.0.3] - 2026-02-18

### Fixed

- **Settings visibility**: TCMB rate type setting now appears in Accounting > Configuration > Settings (Invoicing section, after Currencies)
- **Odoo 19 settings view**: Replaced obsolete `//form/sheet` + `app_settings_block` with `<block>`/`<setting>` structure
- **ParseError**: Removed unused `action_tcmb_config_settings` and `tcmb_config_action.xml` that caused ParseError on load
- **Settings menuitem**: Removed Settings submenu under TCMB Rates (caused ParseError); settings accessible via Accounting config
- **Form view OwlError**: Replaced `widget="statusbar"` on Boolean `is_synced` with `widget="boolean"` – statusbar expects Selection fields

## [19.0.1.0.2] - 2026-02-18

### Added

- **Rate type selection**: Choose which TCMB rate to use for res.currency.rate sync
  - Forex Buying, Forex Selling (default), Banknote Buying, Banknote Selling
- **TCMB Settings**: Accounting > Configuration > Settings (Invoicing section)

## [19.0.1.0.1] - 2026-02-18

### Added

- **Cron at 15:15**: Daily scheduled action at 15:15 (created via `post_init_hook`, no XML)
- **Update from TCMB menu**: Configuration > TCMB Rates > Update from TCMB (Server Action)
- **Currencies list button**: "Update from TCMB" button in Accounting > Configuration > Currencies
- **TCMB date formats**: Support for dd.mm.yyyy, mm.dd.yyyy, mm/dd/yyyy from TCMB XML
- **Re-link currency on sync**: Newly added currencies (e.g. AUD) in res.currency get linked and synced during update

### Fixed

- **Rate format**: Corrected inverted rate – now stores forex_selling/unit (TRY per foreign currency) for Odoo res.currency.rate
- **Sync date mismatch**: Sync now uses TCMB XML rate_date instead of today() – fixes weekend/holiday updates
- **currency_id persistence**: Re-linking now uses write() to persist to DB
- **post_init_hook signature**: Odoo 19 uses `env` only, not (cr, registry)
- **numbercall removed**: Field removed in Odoo 18+
- **ParseError**: Cron and Server Action moved to Python/data to avoid XML RelaxNG validation errors
- **Migration**: Cron update migration uses ORM instead of raw SQL (Odoo 18+ schema)

### Removed

- Wizard and redundant manual update paths (server action duplicate, wizard)
- ir_cron_data.xml (ParseError; cron created in post_init_hook)
- nextcall eval from cron XML

### Changed

- **Simplified structure**: Single update path (update_from_tcmb + action_sync_all_to_odoo)
- **Odoo 19 compatibility**: list (not tree), post_init_hook(env), no numbercall

---

## [19.0.1.0.0] - Initial

- TCMB today.xml integration
- tcmb.currency.rate model with forex/banknote rates
- Sync to res.currency.rate
- Multi-company support
