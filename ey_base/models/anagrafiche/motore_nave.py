# -*- coding: utf-8 -*-
from odoo import models, fields


class MotoreNave(models.Model):
    _name = 'ey_base.motore_nave'
    _description = 'Motore installato su nave'

    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    modello = fields.Char(string='Modello')
    numero_serie = fields.Char(string='Numero di serie', index=True)
    anno_costr = fields.Integer(string='Anno fabbricazione', index=True)
