# -*- coding: utf-8 -*-
from odoo import models, fields


class UlterioreRecapito(models.Model):
    _name = 'ey_base.ulteriore_recapito'
    _description = 'Ulteriore recapito nave'
    _rec_name = 'indirizzo'

    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    tipo_id = fields.Many2one('ey_base.tipo_recapito', string='Tipo recapito')
    indirizzo = fields.Char(string='Indirizzo', required=True)
    city = fields.Char(string='Città')
    zip = fields.Char(string='CAP', size=10)
    provincia = fields.Char(string='Provincia', size=5)
