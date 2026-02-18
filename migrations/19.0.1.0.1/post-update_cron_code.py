# Update cron code to use rate_date (fix sync when TCMB date differs from today)
# Odoo 18+: ir.cron delegates to ir.actions.server; use ORM to avoid schema changes

def migrate(cr, version):
    try:
        from odoo import api, SUPERUSER_ID
        env = api.Environment(cr, SUPERUSER_ID, {})
        cron = env.ref('tcmb_currency_rates.ir_cron_tcmb_daily_update', raise_if_not_found=False)
        if cron:
            cron.code = 'created, updated, rate_date = model.update_from_tcmb(); model.action_sync_all_to_odoo(rate_date=rate_date)'
    except Exception:
        pass  # Cron may not exist or model structure differs
