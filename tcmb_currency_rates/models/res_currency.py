# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    tcmb_auto_update = fields.Boolean(
        string='Auto Update from TCMB',
        default=False,
        help='When checked, this currency is synced when Update from TCMB runs. Toggle on to include.',
    )
    tcmb_last_update = fields.Datetime(
        string='Last TCMB Sync',
        compute='_compute_tcmb_last_update',
        help='When Update from TCMB was last run (query date), not the rate date from TCMB',
    )
    tcmb_last_update_display = fields.Char(
        string='Last TCMB Sync',
        compute='_compute_tcmb_last_update',
        help='Formatted: dd.mm.yyyy HH:mm (24h)',
    )

    @api.depends()
    def _compute_tcmb_last_update(self):
        value = self.env['ir.config_parameter'].sudo().get_param(
            'tcmb_currency_rates.last_update'
        )
        try:
            dt = fields.Datetime.from_string(value) if value else False
        except (TypeError, ValueError):
            dt = False
        for record in self:
            record.tcmb_last_update = dt
            if dt:
                dt_local = fields.Datetime.context_timestamp(record, dt)
                record.tcmb_last_update_display = dt_local.strftime('%d.%m.%Y %H:%M')
            else:
                record.tcmb_last_update_display = ''

    def action_update_tcmb_rates(self):
        """Update all currency rates from TCMB and log to chatter."""
        tcmb_rate_model = self.env['tcmb.currency.rate']
        _log, action = tcmb_rate_model.run_tcmb_update_and_log(run_type='manual')
        return action
