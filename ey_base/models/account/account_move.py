# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # fields Many2one
    unita_id = fields.Many2one(comodel_name='ey_base.unita', string='Unità')

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        """
        Aggiungo l'unita_id alla move_line che a "Dare" uguale al totale della fattura
        """
        lines_vals_list = super()._stock_account_prepare_anglo_saxon_out_lines_vals()
        
        for line_vals in lines_vals_list:
            if line_vals.get('debit') == self.amount_total:
                line_vals['unita_id'] = self.unita_id.id
        
        return lines_vals_list

    def action_post(self):
        """Validazione prima della conferma della fattura"""
        for rec in self:
            if rec.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
                empty_lines = rec.invoice_line_ids.filtered(lambda r: not r.name or not r.name.strip())
                if empty_lines:
                    raise ValidationError("Le righe della fattura devono avere la Descrizione")
        
        return super().action_post()
