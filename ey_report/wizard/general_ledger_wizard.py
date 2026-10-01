# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import ValidationError
import time

class GeneralLedgerReportWizard(models.TransientModel):
    _inherit = 'general.ledger.report.wizard'

    # Aggiungo date_range_id per evitare errori nella vista OCA
    date_range_id = fields.Many2one('date.range', string='Date Range', required=False)
    
    # field per controllare come voler calcore i conti nei periodi
    set_to_zero = fields.Boolean(string="Saldo di periodo")

    @api.model
    def _prepare_report_general_ledger(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'only_posted_moves': self.target_move == 'posted',
            'hide_account_at_0': self.hide_account_at_0,
            'foreign_currency': self.foreign_currency,
            'show_analytic_tags': self.show_analytic_tags,
            'set_to_zero': self.set_to_zero,
            'company_id': self.company_id.id,
            'filter_account_ids': [(6, 0, self.account_ids.ids)],
            'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
            'filter_cost_center_ids': [(6, 0, self.cost_center_ids.ids)],
            'filter_analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'filter_journal_ids': [(6, 0, self.account_journal_ids.ids)],
            'centralize': self.centralize,
            'fy_start_date': self.fy_start_date,
            'partner_ungrouped': self.partner_ungrouped,
        }
        return data
