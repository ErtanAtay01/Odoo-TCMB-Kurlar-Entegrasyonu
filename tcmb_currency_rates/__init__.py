# -*- coding: utf-8 -*-
from . import models
from . import wizard


def post_init_hook(env):
    """Create TCMB cron job (daily 15:15) - done in Python to avoid XML ParseError."""
    from datetime import datetime, timedelta
    cron_code = "model.run_tcmb_update_and_log(run_type='cron')"
    Cron = env['ir.cron']
    for name in ('TCMB: Daily Rate Update (15:15)', 'TCMB: Daily Rate Update (15:30)'):
        existing = Cron.search([('cron_name', '=', name)], limit=1) or Cron.search([('name', '=', name)], limit=1)
        if existing:
            break
    if not existing:
        existing = Cron.search([('cron_name', 'ilike', 'TCMB%')], limit=1) or Cron.search([('name', 'ilike', 'TCMB%')], limit=1)
    if existing:
        # Odoo 18+: cron delegates to ir.actions.server; code is on the server action
        server = getattr(existing, 'ir_actions_server_id', existing)
        if hasattr(server, 'code'):
            server.write({'code': cron_code})
        elif hasattr(existing, 'code'):
            existing.write({'code': cron_code})
        return  # Already exists
    now = datetime.now()
    next_1515 = now.replace(hour=15, minute=15, second=0, microsecond=0)
    if now >= next_1515:
        next_1515 += timedelta(days=1)
    model = env['ir.model'].search([('model', '=', 'tcmb.currency.rate')], limit=1)
    if not model:
        return
    cron = env['ir.cron'].create({
        'name': 'TCMB: Daily Rate Update (15:15)',
        'model_id': model.id,
        'user_id': env.ref('base.user_root').id,
        'state': 'code',
        'code': cron_code,
        'interval_number': 1,
        'interval_type': 'days',
        'active': True,
        'nextcall': next_1515,
    })
    env['ir.model.data'].create({
        'name': 'ir_cron_tcmb_daily_update',
        'module': 'tcmb_currency_rates',
        'model': 'ir.cron',
        'res_id': cron.id,
        'noupdate': True,
    })
