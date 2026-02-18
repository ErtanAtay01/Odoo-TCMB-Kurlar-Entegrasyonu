# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TCMBCronRun(models.Model):
    _name = 'tcmb.cron.run'
    _description = 'TCMB Update Run Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'run_date desc'

    run_date = fields.Datetime(string='Run Date', required=True, default=fields.Datetime.now, readonly=True)
    run_type = fields.Selection(
        [('cron', 'Scheduled'), ('manual', 'Manual')],
        string='Run Type',
        required=True,
        default='manual',
        readonly=True,
    )
    state = fields.Selection(
        [('success', 'Success'), ('skipped', 'Skipped'), ('error', 'Error')],
        string='Result',
        required=True,
        default='success',
        readonly=True,
    )
    created = fields.Integer(string='Rates Created', readonly=True, default=0)
    updated = fields.Integer(string='Rates Updated', readonly=True, default=0)
    rate_date = fields.Date(string='TCMB Rate Date', readonly=True)
    message = fields.Text(string='Details', readonly=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True,
    )

    def _post_result_message(self):
        """Post a chatter message with the run result."""
        self.ensure_one()
        if self.state == 'success':
            body = _(
                'TCMB update completed: %(created)d created, %(updated)d updated. '
                'Rate date: %(rate_date)s.'
            ) % {
                'created': self.created,
                'updated': self.updated,
                'rate_date': self.rate_date or '-',
            }
        elif self.state == 'skipped':
            body = _('TCMB update skipped. %s') % (self.message or _('Turkey public holiday (TCMB closed).'))
        else:
            body = _('TCMB update failed. %s') % (self.message or '')
        self.message_post(body=body, message_type='notification')
