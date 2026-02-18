import time
import requests
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    import holidays
except ImportError:
    holidays = None  # Optional: install with pip install holidays for Turkey holiday skip

RATE_TYPE_LABELS = {
    'forex_buying': _('Forex Buying'),
    'forex_selling': _('Forex Selling'),
    'banknote_buying': _('Banknote Buying'),
    'banknote_selling': _('Banknote Selling'),
}


class TCMBCurrencyRate(models.Model):
    _name = 'tcmb.currency.rate'
    _description = 'TCMB Daily Currency Rates'
    _order = 'date desc, currency_code'
    _rec_name = 'currency_code'
    
    # Basic fields
    currency_code = fields.Char('Currency Code', required=True, index=True)
    currency_name = fields.Char('Currency Name')
    date = fields.Date('Rate Date', required=True, index=True, default=fields.Date.today)
    unit = fields.Integer('Unit', default=1)
    
    # TCMB rate types
    forex_buying = fields.Float('Forex Buying', digits=(12, 4))
    forex_selling = fields.Float('Forex Selling', digits=(12, 4))
    banknote_buying = fields.Float('Banknote Buying', digits=(12, 4))
    banknote_selling = fields.Float('Banknote Selling', digits=(12, 4))
    
    # Computed
    effective_rate = fields.Float('Effective Rate (Odoo Format)', 
                                   compute='_compute_effective_rate', 
                                   store=True, digits=(12, 6), index=True)
    
    # Relations
    currency_id = fields.Many2one('res.currency', 'Odoo Currency', index=True)
    is_synced = fields.Boolean('Synced to Odoo', default=False, index=True)
    sync_date = fields.Datetime('Last Sync Date')
    company_id = fields.Many2one('res.company', 'Company', 
                                  default=lambda self: self.env.company, index=True)
    rate_type_label = fields.Char(
        string='Rate Type in Use',
        compute='_compute_rate_type_label',
        help='Currently selected TCMB rate type for Odoo sync',
    )

    @api.depends()
    def _compute_rate_type_label(self):
        rate_type = self.env['ir.config_parameter'].sudo().get_param(
            'tcmb_currency_rates.rate_type', 'forex_selling'
        )
        label = RATE_TYPE_LABELS.get(rate_type, RATE_TYPE_LABELS['forex_selling'])
        for record in self:
            record.rate_type_label = label

    _sql_constraints = [
        ('unique_currency_date', 
         'UNIQUE(currency_code, date, company_id)', 
         'Currency rate for this date already exists!')
    ]
    
    @api.depends('forex_selling', 'unit')
    def _compute_effective_rate(self):
        """Convert TCMB format to Odoo res.currency.rate format.
        Odoo: rate = company_currency per 1 unit of foreign currency.
        TCMB: 1 USD = forex_selling TRY → Odoo rate = forex_selling/unit (34.50 for unit=1)
        """
        for record in self:
            if record.forex_selling and record.unit and record.forex_selling != 0:
                record.effective_rate = record.forex_selling / record.unit
            else:
                record.effective_rate = 0.0
    
    def _fetch_tcmb_xml(self):
        """Fetch XML from TCMB"""
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        try:
            response = requests.get(url, timeout=15, verify=True)
            response.raise_for_status()
            return response.content
        except requests.exceptions.Timeout as e:
            _logger.error("TCMB fetch timeout: %s", e)
            raise UserError(
                _("TCMB request timed out. Check your internet connection; "
                  "TCMB may be slow or temporarily unreachable.")
            )
        except requests.exceptions.ConnectionError as e:
            _logger.error("TCMB connection error: %s", e)
            raise UserError(
                _("Could not connect to TCMB. Check your internet connection, "
                  "firewall, or proxy settings.")
            )
        except requests.exceptions.HTTPError as e:
            _logger.error("TCMB HTTP error: %s", e)
            if e.response is not None:
                if e.response.status_code == 404:
                    raise UserError(
                        _("TCMB URL not found (404). The service format may have changed.")
                    )
                if 500 <= e.response.status_code < 600:
                    raise UserError(
                        _("TCMB server error (%(code)s). Try again later.")
                        % {'code': e.response.status_code}
                    )
            raise UserError(_("TCMB HTTP error: %s") % str(e))
        except requests.exceptions.SSLError as e:
            _logger.error("TCMB SSL error: %s", e)
            raise UserError(
                _("SSL error connecting to TCMB. Check system date/time or proxy.")
            )
        except requests.exceptions.RequestException as e:
            _logger.error("TCMB fetch error: %s", e)
            raise UserError(_("Could not fetch TCMB rates: %s") % str(e))
        except Exception as e:
            _logger.error("Unexpected TCMB fetch error: %s", e)
            raise UserError(
                _("Unexpected error while fetching TCMB rates. Details: %s") % str(e)
            )

    def _fetch_tcmb_xml_by_date(self, target_date):
        """Fetch TCMB XML for a specific historical date.
        TCMB URL format: kurlar/YYYYMM/DDMMYYYY.xml
        Returns None on failure (no raise)."""
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        yyyymm = target_date.strftime('%Y%m')
        ddmmyyyy = target_date.strftime('%d%m%Y')
        url = f"https://www.tcmb.gov.tr/kurlar/{yyyymm}/{ddmmyyyy}.xml"
        try:
            response = requests.get(url, timeout=15, verify=True)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            _logger.warning("Could not fetch TCMB data for %s: %s", target_date, e)
            return None
        except Exception as e:
            _logger.warning("Unexpected error fetching TCMB for %s: %s", target_date, e)
            return None

    def _parse_tcmb_xml(self, xml_content):
        """Parse TCMB XML and return structured data"""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            _logger.error("TCMB XML parsing error: %s", e)
            raise UserError(
                _("Invalid XML from TCMB: %(err)s. TCMB response format may have changed.")
                % {'err': str(e)}
            )
        date_str = root.attrib.get('Date')
        if not date_str:
            raise UserError(
                _("No date in TCMB XML. Response format may have changed.")
            )
        
        # TCMB supports: dd.mm.yyyy, mm.dd.yyyy, mm/dd/yyyy
        date_formats = ('%d.%m.%Y', '%m.%d.%Y', '%m/%d/%Y')
        rate_date = None
        for fmt in date_formats:
            try:
                rate_date = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue
        if rate_date is None:
            raise UserError(
                _("Invalid date format in TCMB XML: %(val)s") % {'val': date_str}
            )
        
        rates = []
        for currency in root.findall('Currency'):
            code = currency.attrib.get('CurrencyCode')
            
            rate_data = {
                'currency_code': code,
                'currency_name': self._get_text(currency, 'CurrencyName'),
                'date': rate_date,
                'unit': int(self._get_text(currency, 'Unit', '1')),
            }
            
            # Parse all rate types
            rate_fields = {
                'ForexBuying': 'forex_buying',
                'ForexSelling': 'forex_selling',
                'BanknoteBuying': 'banknote_buying',
                'BanknoteSelling': 'banknote_selling',
            }
            
            for xml_field, model_field in rate_fields.items():
                value = self._get_text(currency, xml_field)
                if value:
                    try:
                        rate_data[model_field] = float(value.replace(',', '.'))
                    except ValueError:
                        _logger.warning(f"Invalid rate value for {code} {xml_field}: {value}")
                        rate_data[model_field] = 0.0
            
            rates.append(rate_data)
        
        return rate_date, rates
    
    def _get_text(self, element, tag, default=''):
        """Safely get text from XML element"""
        child = element.find(tag)
        return child.text if child is not None and child.text else default
    
    @api.model
    def update_from_tcmb(self):
        """Fetch and save rates from TCMB"""
        xml_content = self._fetch_tcmb_xml()
        rate_date, rates_data = self._parse_tcmb_xml(xml_content)
        
        created = 0
        updated = 0
        
        # Get all existing rates for today in one query
        existing_rates = self.search([
            ('date', '=', rate_date),
            ('company_id', '=', self.env.company.id),
        ])
        existing_dict = {(r.currency_code, r.company_id.id): r for r in existing_rates}
        
        # Get all currencies in one query
        all_currencies = self.env['res.currency'].search([('name', 'in', [r['currency_code'] for r in rates_data])])
        currency_dict = {c.name: c.id for c in all_currencies}
        
        rates_to_create = []
        rates_to_update = []
        
        for rate_info in rates_data:
            # Add currency_id if exists
            if rate_info['currency_code'] in currency_dict:
                rate_info['currency_id'] = currency_dict[rate_info['currency_code']]
            
            rate_info['company_id'] = self.env.company.id
            
            # Check if exists
            key = (rate_info['currency_code'], self.env.company.id)
            existing = existing_dict.get(key)
            
            if existing:
                # Prepare for bulk update
                rates_to_update.append((existing.id, rate_info))
                updated += 1
            else:
                # Prepare for bulk create
                rates_to_create.append(rate_info)
                created += 1
        
        # Bulk operations
        if rates_to_create:
            self.create(rates_to_create)
        
        for record_id, rate_data in rates_to_update:
            self.browse(record_id).write(rate_data)
        
        _logger.info(f"TCMB rates updated: {created} created, {updated} updated")
        return created, updated, rate_date

    @api.model
    def import_historical_range(self, start_date, end_date, skip_holidays=True, sync_to_odoo=False,
                                skip_already_imported=False):
        """Import TCMB rates for a date range. Skips weekends and optionally Turkey holidays.
        If sync_to_odoo True, syncs each imported date to res.currency.rate (only currencies with TCMB Auto Update).
        If skip_already_imported True, skips dates that already have TCMB data (no fetch, no overwrite).
        Returns dict: created, updated, skipped, skipped_dates (first 10)."""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if start_date > end_date:
            raise UserError(_("Start date must be before or equal to end date."))
        min_date = date(1996, 4, 16)
        if start_date < min_date:
            raise UserError(
                _("TCMB data is only available from 16 April 1996 onwards.")
            )
        tr_holidays = set()
        if skip_holidays and holidays is not None:
            for y in range(start_date.year, end_date.year + 1):
                tr_holidays |= set(holidays.country_holidays('TR', years=[y]))
        total_created = 0
        total_updated = 0
        skipped_dates = []
        current_date = start_date
        company_id = self.env.company.id
        while current_date <= end_date:
            if current_date.weekday() >= 5:
                skipped_dates.append(str(current_date))
                current_date += timedelta(days=1)
                continue
            if skip_holidays and current_date in tr_holidays:
                skipped_dates.append(str(current_date))
                current_date += timedelta(days=1)
                continue
            if skip_already_imported:
                has_rates = self.search_count([
                    ('date', '=', current_date),
                    ('company_id', '=', company_id),
                ]) > 0
                if has_rates:
                    skipped_dates.append(str(current_date))
                    current_date += timedelta(days=1)
                    continue
            xml_content = self._fetch_tcmb_xml_by_date(current_date)
            if not xml_content:
                skipped_dates.append(str(current_date))
                current_date += timedelta(days=1)
                continue
            try:
                rate_date, rates_data = self._parse_tcmb_xml(xml_content)
            except Exception as e:
                _logger.warning("Error parsing TCMB XML for %s: %s", current_date, e)
                skipped_dates.append(str(current_date))
                current_date += timedelta(days=1)
                continue
            existing_rates = self.search([
                ('date', '=', rate_date),
                ('company_id', '=', company_id),
            ])
            existing_dict = {(r.currency_code, company_id): r for r in existing_rates}
            all_currencies = self.env['res.currency'].search([
                ('name', 'in', [r['currency_code'] for r in rates_data])
            ])
            currency_dict = {c.name: c.id for c in all_currencies}
            rates_to_create = []
            rates_to_update = []
            for rate_info in rates_data:
                if rate_info['currency_code'] in currency_dict:
                    rate_info['currency_id'] = currency_dict[rate_info['currency_code']]
                rate_info['company_id'] = company_id
                key = (rate_info['currency_code'], company_id)
                existing = existing_dict.get(key)
                if existing:
                    rates_to_update.append((existing.id, rate_info))
                    total_updated += 1
                else:
                    rates_to_create.append(rate_info)
                    total_created += 1
            if rates_to_create:
                self.create(rates_to_create)
            for record_id, rate_data in rates_to_update:
                self.browse(record_id).write(rate_data)
            if sync_to_odoo:
                self.action_sync_all_to_odoo(rate_date=rate_date)
            _logger.info(
                "Historical import: %s → %d currencies",
                current_date,
                len(rates_data),
            )
            current_date += timedelta(days=1)
        return {
            'created': total_created,
            'updated': total_updated,
            'skipped': len(skipped_dates),
            'skipped_dates': skipped_dates[:10],
        }

    @api.model
    def _is_turkey_holiday(self, d=None):
        """Return True if d is a Turkey public holiday (TCMB closed).
        Returns False if holidays package is not installed (pip install holidays)."""
        if holidays is None:
            _logger.debug(
                "holidays package not installed; Turkey holiday skip disabled. "
                "Install with: pip install holidays"
            )
            return False
        if d is None:
            d = date.today()
        return d in holidays.country_holidays('TR')

    @api.model
    def update_from_tcmb_with_retry(self):
        """Fetch and save rates from TCMB with retry on failure.
        Skips on Turkey public holidays when enabled. Retries up to retry_count
        times, retry_delay_minutes between attempts. Returns None when skipped."""
        ICP = self.env['ir.config_parameter'].sudo()
        if ICP.get_param('tcmb_currency_rates.skip_on_holiday', 'True') == 'True':
            if self._is_turkey_holiday():
                _logger.info("TCMB update skipped: today is a Turkey public holiday")
                return None
        retry_count = int(ICP.get_param('tcmb_currency_rates.retry_count', '3'))
        retry_delay_minutes = int(ICP.get_param('tcmb_currency_rates.retry_delay_minutes', '5'))
        last_error = None
        for attempt in range(1 + retry_count):
            try:
                return self.update_from_tcmb()
            except Exception as e:
                last_error = e
                _logger.warning("TCMB update attempt %d/%d failed: %s", attempt + 1, 1 + retry_count, e)
                if attempt < retry_count:
                    delay_sec = retry_delay_minutes * 60
                    _logger.info("Retrying in %d minutes...", retry_delay_minutes)
                    time.sleep(delay_sec)
        raise UserError(
            _("TCMB update failed after %(n)d attempts. %(err)s "
              "Check Settings > TCMB Currency Rates for retry options.")
            % {'n': 1 + retry_count, 'err': str(last_error)}
        )

    @api.model
    def action_fix_cron_code_for_logging(self):
        """Update the TCMB scheduled action so manual/scheduled runs are logged to Run History.
        Call once if cron manual run does not create a log (Odoo 18+ stores code on server action)."""
        cron_code = "model.run_tcmb_update_and_log(run_type='cron')"
        Cron = self.env['ir.cron'].sudo()
        cron = self.env.ref('tcmb_currency_rates.ir_cron_tcmb_daily_update', raise_if_not_found=False)
        if not cron:
            for name in ('TCMB: Daily Rate Update (15:15)', 'TCMB: Daily Rate Update (15:30)'):
                cron = Cron.search([('cron_name', '=', name)], limit=1) or Cron.search([('name', '=', name)], limit=1)
                if cron:
                    break
        if not cron:
            cron = Cron.search([('cron_name', 'ilike', 'TCMB%')], limit=1) or Cron.search([('name', 'ilike', 'TCMB%')], limit=1)
        if not cron:
            model = self.env['ir.model'].sudo().search([('model', '=', 'tcmb.currency.rate')], limit=1)
            if model:
                cron = Cron.search([('model_id', '=', model.id)], limit=1)
        if not cron:
            raise UserError(_('TCMB scheduled action not found. Create it under Settings → Technical → Automation → Scheduled Actions, or reinstall the module.'))
        server = getattr(cron, 'ir_actions_server_id', None)
        if server and hasattr(server, 'code'):
            server.write({'code': cron_code})
        elif hasattr(cron, 'code'):
            cron.write({'code': cron_code})
        else:
            raise UserError(_('Could not update cron code (unexpected structure).'))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cron updated'),
                'message': _('Scheduled action code updated. Next manual or automatic run will be logged in Run History.'),
                'type': 'success',
            },
        }

    @api.model
    def run_tcmb_update_and_log(self, run_type='manual'):
        """Run TCMB update (with retry), sync to Odoo, log to tcmb.cron.run chatter.
        Returns (log_record, action_dict) for UI; action_dict is the notification to show."""
        RunLog = self.env['tcmb.cron.run'].sudo()
        try:
            result = self.update_from_tcmb_with_retry()
            if result is None:
                log = RunLog.create({
                    'run_type': run_type,
                    'state': 'skipped',
                    'message': _('Turkey public holiday - TCMB closed'),
                    'company_id': self.env.company.id,
                })
                log._post_result_message()
                action = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Skipped'),
                        'message': _('Today is a Turkey public holiday - TCMB closed'),
                        'type': 'warning',
                    },
                }
                return log, action
            created, updated, rate_date = result
            self.action_sync_all_to_odoo(rate_date=rate_date)
            log = RunLog.create({
                'run_type': run_type,
                'state': 'success',
                'created': created,
                'updated': updated,
                'rate_date': rate_date,
                'company_id': self.env.company.id,
            })
            log._post_result_message()
            action = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('TCMB rates updated (%d new, %d updated) and synced') % (created, updated),
                    'type': 'success',
                },
            }
            return log, action
        except Exception as e:
            log = RunLog.create({
                'run_type': run_type,
                'state': 'error',
                'message': str(e),
                'company_id': self.env.company.id,
            })
            log._post_result_message()
            action = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('TCMB update failed: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                },
            }
            return log, action

    def _get_rate_for_sync(self):
        """Get rate value for res.currency.rate based on configured rate type."""
        rate_type = self.env['ir.config_parameter'].sudo().get_param(
            'tcmb_currency_rates.rate_type', 'forex_selling'
        )
        rate_value = getattr(self, rate_type, None) or 0.0
        if rate_value and self.unit:
            return rate_value / self.unit
        return 0.0

    def action_sync_to_odoo(self):
        """Sync this rate to Odoo currency system"""
        for record in self:
            # Re-link currency_id if missing (e.g. currency added to res.currency after TCMB fetch)
            if not record.currency_id:
                currency = self.env['res.currency'].search(
                    [('name', '=', record.currency_code)], limit=1
                )
                if currency:
                    record.write({'currency_id': currency.id})  # persist to DB
                else:
                    continue
            if not record.currency_id.tcmb_auto_update:
                continue  # Skip: currency not set for auto update
            rate_obj = self.env['res.currency.rate']
            existing = rate_obj.search([
                ('currency_id', '=', record.currency_id.id),
                ('name', '=', record.date),
                ('company_id', '=', record.company_id.id),
            ], limit=1)
            
            rate_value = record._get_rate_for_sync()
            if not rate_value or rate_value <= 0:
                continue  # Skip: res.currency.rate requires strictly positive rate
            vals = {
                'currency_id': record.currency_id.id,
                'name': record.date,
                'rate': rate_value,
                'company_id': record.company_id.id,
            }
            if existing:
                existing.write(vals)
            else:
                rate_obj.create(vals)
            
            record.write({
                'is_synced': True,
                'sync_date': fields.Datetime.now(),
            })
    
    def action_update_and_sync(self):
        """Update from TCMB and sync to Odoo - for manual button; logs to Run History."""
        _log, action = self.run_tcmb_update_and_log(run_type='manual')
        return action

    def action_sync_all_to_odoo(self, rate_date=None):
        """Sync TCMB rates to res.currency.rate. Use rate_date from TCMB XML, not today()."""
        if rate_date is None:
            rate_date = fields.Date.today()
        rates_to_sync = self.search([
            ('date', '=', rate_date),
            ('company_id', '=', self.env.company.id),
        ])
        # Exclude currencies with 0 for selected rate type (TCMB doesn't buy/sell them)
        rate_type = self.env['ir.config_parameter'].sudo().get_param(
            'tcmb_currency_rates.rate_type', 'forex_selling'
        )
        rates_to_sync = rates_to_sync.filtered(
            lambda r: (getattr(r, rate_type, None) or 0) > 0
        )
        rates_to_sync.action_sync_to_odoo()
        # Store last update datetime for display on Currencies list
        self.env['ir.config_parameter'].sudo().set_param(
            'tcmb_currency_rates.last_update',
            fields.Datetime.to_string(fields.Datetime.now()),
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%d rates synced to Odoo currencies') % len(rates_to_sync),
                'type': 'success',
            }
        }