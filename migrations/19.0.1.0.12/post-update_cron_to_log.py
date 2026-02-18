# Update cron to use run_tcmb_update_and_log (chatter logging)
# Odoo 18+: ir.cron delegates to ir.actions.server; code lives on the server action

def migrate(cr, version):
    try:
        from odoo import api, SUPERUSER_ID
        env = api.Environment(cr, SUPERUSER_ID, {})
        cron = env.ref('tcmb_currency_rates.ir_cron_tcmb_daily_update', raise_if_not_found=False)
        if not cron:
            return
        new_code = "model.run_tcmb_update_and_log(run_type='cron')"
        # Update delegated server action (Odoo 18+) or cron code
        server = getattr(cron, 'ir_actions_server_id', None)
        if server and hasattr(server, 'code'):
            server.write({'code': new_code})
        elif hasattr(cron, 'code'):
            cron.write({'code': new_code})
    except Exception:
        pass
