# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    unita_richiesta_linea = fields.Boolean(string="Unita richiesta", related='move_id.unita_richiesta')