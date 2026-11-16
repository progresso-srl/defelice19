# -*- coding: utf-8 -*-

from odoo import fields, models


class GeneralLedgerReportWizard(models.TransientModel):
    _inherit = 'general.ledger.report.wizard'

    # Aggiungo date_range_id per evitare errori nella vista OCA
    date_range_id = fields.Many2one('date.range', string='Date Range', required=False)

    # field per controllare come voler calcolare i conti nei periodi
    set_to_zero = fields.Boolean(string="Saldo di periodo")

    def _prepare_report_general_ledger(self):
        # Prima il metodo era riscritto per intero con i campi di OCA 12
        # (show_analytic_tags, analytic_tag_ids, partner_ungrouped), che in
        # OCA 19 non esistono: il Mastro andava in errore. Ora i dati sono
        # quelli di OCA, piu' l'opzione del saldo di periodo.
        res = super()._prepare_report_general_ledger()
        res['set_to_zero'] = self.set_to_zero
        return res
