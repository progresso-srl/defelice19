# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from datetime import datetime
_logger =logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    stati_linea_spesa = [
        ('contabilita_nave', 'Contabilità nave'),
        ('anticipi_armatore', 'Anticipi armatore'),
        ('no_collegamento', 'No collegamento'),
    ]

    def button_collega_linea_spesa_nave(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ey_contabilita_navi.wiz_collega_linea_spesa_nave',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_account_move_id': self.id}
            }
        
    def button_collega_linea_spesa_armatore(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ey_contabilita_navi.wiz_collega_linea_spesa_armatore',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_account_move_id': self.id}
            }
        
    def action_post(self):
        _logger.info("begin overwritten action_post()")
        res = super(AccountMove, self).action_post()
        if self.collegamento_linea_spesa == 'contabilita_nave':
            # controlla se il campo spesa_previsionale_id è settato
            if self.spesa_previsionale_id:
               spesa_collegata = self.env['ey_contabilita_navi.spesa_previsionale'].search([('id', '=', self.spesa_previsionale_id.id)], limit=1)
               spesa_collegata.effettivo = self.amount
               spesa_collegata.confermata = True
               spesa_collegata.data_conferma = datetime.today().strftime("%Y-%m-%d")
            else:
                raise ValidationError("Il campo Contabilità nave non può essere vuoto")
        elif self.collegamento_linea_spesa == 'anticipi_armatore':
            # controlla se il campo spesa_previsionale_id è settato
            if self.anticipi_armatore_id:
               anticipo_collegato = self.env['ey_contabilita_navi.anticipi_armatore'].search([('id', '=', self.anticipi_armatore_id.id)], limit=1)
               anticipo_collegato.cifra = self.amount
               #anticipo_collegato.data = self.date
            else:
                raise ValidationError("Il campo Anticipi armatore non può essere vuoto")
        return res
    
    def button_cancel(self):
        _logger.info("begin overwritten button_cancel()")
        res = super(AccountMove, self).button_cancel()
        for move in self:
            if move.collegamento_linea_spesa == 'contabilita_nave':
                # controlla se il campo spesa_previsionale_id è settato
                if move.spesa_previsionale_id:
                    spesa_collegata = self.env['ey_contabilita_navi.spesa_previsionale'].search([('id', '=', move.spesa_previsionale_id.id)], limit=1)
                    spesa_collegata.confermata = False
            elif move.collegamento_linea_spesa == 'anticipi_armatore':
                if move.anticipi_armatore_id:
                    anticipo_collegato = self.env['ey_contabilita_navi.anticipi_armatore'].search([('id', '=', move.anticipi_armatore_id.id)], limit=1)
        return res

    @api.onchange('collegamento_linea_spesa')
    def onchange_collegamento_linea_spesa(self):
        self.ensure_one()
        if self.collegamento_linea_spesa == 'contabilita_nave' :
            self.unita_richiesta = True
        else :
            self.unita_richiesta = False

    unita_richiesta = fields.Boolean(string="Unita richiesta", index=True, default=False)
    collegamento_linea_spesa = fields.Selection(stati_linea_spesa, string='Collegamento linea spesa')

    # CAMPI MANY2ONE
    spesa_previsionale_id = fields.Many2one("ey_contabilita_navi.spesa_previsionale", index=True, domain="[('previsionale_id.state', '!=', 'Previsionale')]")
    anticipi_armatore_id = fields.Many2one("ey_contabilita_navi.anticipi_armatore", index=True, domain="[('previsionale_id.state', '!=', 'Previsionale')]")
