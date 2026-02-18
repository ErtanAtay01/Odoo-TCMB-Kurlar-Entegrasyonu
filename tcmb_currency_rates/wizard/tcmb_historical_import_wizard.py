# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TCMBHistoricalImportWizard(models.TransientModel):
    _name = 'tcmb.historical.import.wizard'
    _description = 'Import Historical TCMB Rates'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.today)
    skip_holidays = fields.Boolean(
        string='Skip Weekends & Holidays',
        default=True,
        help='Skip weekends and Turkey public holidays (TCMB closed)',
    )
    sync_to_odoo = fields.Boolean(
        string='Sync to Odoo currencies',
        default=True,
        help='Push imported rates to Accounting currencies (only for currencies with TCMB Auto Update checked)',
    )
    skip_already_imported = fields.Boolean(
        string='Skip dates already imported',
        default=True,
        help='Do not fetch or overwrite dates that already have TCMB rates (saves requests, keeps existing data)',
    )

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for wizard in self:
            if wizard.start_date and wizard.end_date and wizard.start_date > wizard.end_date:
                raise UserError(_('Start date must be before or equal to end date.'))
            min_date = date(1996, 4, 16)
            if wizard.start_date and wizard.start_date < min_date:
                raise UserError(_('TCMB data is only available from 16 April 1996 onwards.'))

    def action_import(self):
        self.ensure_one()
        result = self.env['tcmb.currency.rate'].import_historical_range(
            self.start_date,
            self.end_date,
            skip_holidays=self.skip_holidays,
            sync_to_odoo=self.sync_to_odoo,
            skip_already_imported=self.skip_already_imported,
        )
        message = _(
            'Historical import completed:\n'
            '• %(created)d rates created\n'
            '• %(updated)d rates updated\n'
            '• %(skipped)d dates skipped'
        ) % result
        if result.get('skipped_dates'):
            message += _('\n\nSome skipped dates: %s') % ', '.join(result['skipped_dates'])
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Historical Import'),
                'message': message,
                'type': 'success',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
