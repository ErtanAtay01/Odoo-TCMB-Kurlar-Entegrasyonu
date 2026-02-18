# -*- coding: utf-8 -*-
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

RATE_TYPE_SELECTION = [
    ('forex_buying', 'Forex Buying'),
    ('forex_selling', 'Forex Selling'),
    ('banknote_buying', 'Banknote Buying'),
    ('banknote_selling', 'Banknote Selling'),
]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_values(self):
        super().set_values()
        # Re-sync res.currency.rate from existing TCMB data with the NEW rate type
        # (tcmb.currency.rate has all 4 types; we just re-apply using selected one)
        self._resync_tcmb_rates_on_setting_change()
        # Invalidate cache so list view label and rate values refresh
        self.env.registry.clear_cache()

    def _resync_tcmb_rates_on_setting_change(self):
        """Re-sync TCMB rates to res.currency.rate when rate type changes.
        Uses existing tcmb.currency.rate data (no new fetch)."""
        try:
            tcmb = self.env['tcmb.currency.rate'].sudo()
            latest = tcmb.search([
                ('company_id', '=', self.env.company.id),
            ], order='date desc', limit=1)
            if latest:
                tcmb.action_sync_all_to_odoo(rate_date=latest.date)
                _logger.info(
                    "TCMB rates re-synced to res.currency.rate (rate type changed, date=%s)",
                    latest.date,
                )
        except Exception as e:
            _logger.warning(
                "TCMB re-sync on setting change failed (setting saved): %s", e
            )

    tcmb_rate_type = fields.Selection(
        RATE_TYPE_SELECTION,
        string='TCMB Rate Type for Odoo',
        default='forex_selling',
        config_parameter='tcmb_currency_rates.rate_type',
        help='Which TCMB rate to use when syncing to res.currency.rate',
    )
    tcmb_retry_count = fields.Integer(
        string='Retry Count',
        default=3,
        config_parameter='tcmb_currency_rates.retry_count',
        help='Number of retries after first failure (e.g. 3 = 4 attempts total)',
    )
    tcmb_retry_delay_minutes = fields.Integer(
        string='Retry Delay (minutes)',
        default=5,
        config_parameter='tcmb_currency_rates.retry_delay_minutes',
        help='Minutes to wait between retry attempts',
    )
    tcmb_skip_on_holiday = fields.Boolean(
        string='Skip on Turkey public holidays',
        default=True,
        config_parameter='tcmb_currency_rates.skip_on_holiday',
        help='When enabled, no fetch on Turkey public holidays (TCMB closed)',
    )
