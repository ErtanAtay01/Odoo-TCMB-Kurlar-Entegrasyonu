# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TCMBSyncDateWizard(models.TransientModel):
    _name = 'tcmb.sync.date.wizard'
    _description = 'Sync TCMB Date to Odoo Currencies'

    rate_date = fields.Date(
        string='Rate Date',
        required=True,
        default=fields.Date.today,
        help='Sync TCMB rates for this date to res.currency.rate (only currencies with TCMB Auto Update)',
    )

    def action_sync(self):
        self.ensure_one()
        return self.env['tcmb.currency.rate'].action_sync_all_to_odoo(rate_date=self.rate_date)
