from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizCollegaLineaSpesaNave(models.TransientModel):
    _name = "ey_contabilita_navi.wiz_collega_linea_spesa_nave"
    _description = "Wiz collega linea spesa nave"

    @api.onchange('unita_id')
    def get_previsionali(self):    
        if self.unita_id:
            contratto_id = self.env['ey_contabilita_navi.contratto_nave'].search([('nave_id', '=', self.unita_id.id)])
            previsionali = self.env['ey_contabilita_navi.previsionale_contratto'].search([('contratto_id', 'in', contratto_id.ids)])
            if len(previsionali) > 0 :
                ids = previsionali.ids
                result = {'domain': {
                            'previsionali_id': [('id', 'in', ids)]
                        }}
                
                return result
            else:
                result = {'domain': {
                    'previsionali_id': [('id', 'in', [])]
                }}

                return result
        else:
            result = {'domain': {
                'previsionali_id': [('id', 'in', [])]
            }}

            return result
            
    @api.onchange('previsionali_id')
    def get_spese(self):    
        if self.previsionali_id:
            spese = self.env['ey_contabilita_navi.spesa_previsionale'].search([('previsionale_id', '=', self.previsionali_id.id)])
            if len(spese) > 0 :
                ids = spese.ids
                result = {'domain': {
                            'spese_id': [
                                ('id', 'in', ids),
                                ('previsionale_id.state', '!=', 'Previsionale')
                                ]
                        }}
                
                return result
            else:
                result = {'domain': {
                    'spese_id': [('id', 'in', [])]
                }}

                return result
        else:
            result = {'domain': {
                'spese_id': [('id', 'in', [])]
            }}

            return result
            
    def button_collega_linea_spesa_nave(self):
        self.ensure_one()
        if self.account_move_id:
            account_move_related = self.env['account.move'].search([('id', '=', self.account_move_id.id)])
            account_move_related.spesa_previsionale_id = self.spese_id.id
        return

    unita_id = fields.Many2one("ey_base.unita", string="Nave", required=True)
    previsionali_id = fields.Many2one("ey_contabilita_navi.previsionale_contratto", string="Previsionale", required=True)
    spese_id = fields.Many2one("ey_contabilita_navi.spesa_previsionale", string="Spesa", required=True)
    account_move_id = fields.Many2one("account.move", required=True)


class WizCollegaLineaSpesaArmatore(models.TransientModel):
    _name = "ey_contabilita_navi.wiz_collega_linea_spesa_armatore"
    _description = "Wiz collega linea spesa armatore"

    @api.onchange('unita_id')
    def get_previsionali(self):    
        if self.unita_id:
            contratto_id = self.env['ey_contabilita_navi.contratto_nave'].search([('nave_id', '=', self.unita_id.id)])
            previsionali = self.env['ey_contabilita_navi.previsionale_contratto'].search([('contratto_id', 'in', contratto_id.ids)])
            if len(previsionali) > 0 :
                ids = previsionali.ids
                result = {'domain': {
                            'previsionali_id': [('id', 'in', ids)]
                        }}
                
                return result
            else:
                result = {'domain': {
                    'previsionali_id': [('id', 'in', [])]
                }}

                return result
        else:
            result = {'domain': {
                'previsionali_id': [('id', 'in', [])]
            }}

            return result
            
    @api.onchange('previsionali_id')
    def get_anticipi(self):    
        if self.previsionali_id:
            anticipi = self.env['ey_contabilita_navi.anticipi_armatore'].search([('previsionale_id', '=', self.previsionali_id.id)])
            if len(anticipi) > 0 :
                ids = anticipi.ids
                result = {'domain': {
                            'anticipi_id': [
                                ('id', 'in', ids),
                                ('previsionale_id.state', '!=', 'Previsionale')
                                ]
                        }}
                
                return result
            else:
                result = {'domain': {
                    'anticipi_id': [('id', 'in', [])]
                }}

                return result
        else:
            result = {'domain': {
                'anticipi_id': [('id', 'in', [])]
            }}

            return result
            
    def button_collega_linea_spesa_armatore(self):
        self.ensure_one()
        if self.account_move_id:
            account_move_related = self.env['account.move'].search([('id', '=', self.account_move_id.id)])
            account_move_related.anticipi_armatore_id = self.anticipi_id.id
        return

    unita_id = fields.Many2one("ey_base.unita", string="Nave", required=True)
    previsionali_id = fields.Many2one("ey_contabilita_navi.previsionale_contratto", string="Previsionale", required=True)
    anticipi_id = fields.Many2one("ey_contabilita_navi.anticipi_armatore", string="Anticipo", required=True)
    account_move_id = fields.Many2one("account.move", required=True)
