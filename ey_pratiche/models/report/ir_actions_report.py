# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"
    
    documento_pratica_id = fields.Many2one('ey_pratiche.documento_tpl', string="Documento per pratica collegato")     
    tpl_pratica_id = fields.Many2one('ey_pratiche.tpl', string="Template pratica collegato", related="documento_pratica_id.tpl_id")
    # documento_corso_id = fields.Many2one("ey_corsi.documento_tpl_corso", string="Documento per corso collegato")#
    # tpl_corso_id = fields.Many2one('ey_corsi.template_corso', string="Template corso collegato", related="documento_corso_id.tpl_id")#
    # documento_esame_id = fields.Many2one("ey_corsi.documento_tpl_esame", string="Documento per esame collegato")#
    # tpl_esame_id = fields.Many2one('ey_corsi.template_esame', string="Template esame collegato", related="documento_esame_id.tpl_id")#
    
    #TODO fare in modo che se i record hanno questi due campi, essi non siano modificabili, neppure il report_name e non sia eliminabile il record
    
    # @api.multi
    # def _get_tpl_pratiche_context(self):
    #     self.ensure_one()
    #     return self
   
    def unlink(self):
        # L'unico modo per eliminare un report collegato a un documento di una pratica è durante l unlink del tpl a cui è associato il documento, durante il quale viene settato documento_pratica_id a null 
        for rec in self.filtered(lambda r:r.documento_pratica_id):
            tpl_pratica_name = rec.tpl_pratica_id.name
            id_tpl_pratica = str(rec.tpl_pratica_id.id)
            raise ValidationError("Questo report è collegato al seguente template di pratica: " + tpl_pratica_name + " (ID " + id_tpl_pratica + ")")       
        
        return super(IrActionsReport, self).unlink()
    
    
    #TODO Constrains che non ci siano due record con lo stesso documento_pratica_id o con lo stesso py3o template 
   
    