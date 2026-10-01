# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GeneralLedgerReport(models.AbstractModel):
    _inherit = 'report.account_financial_report.general_ledger'

    # field per controllare come voler calcore i conti nei periodi
    set_to_zero = fields.Boolean()
