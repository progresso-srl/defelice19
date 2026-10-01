# -*- coding: utf-8 -*-
from odoo import models, fields


class ContattoNave(models.Model):
    _name = 'ey_base.contatto_nave'
    _description = 'Contatto operativo nave'
    _rec_name = 'name'

    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', index=True)
    tipo_id = fields.Many2one('ey_base.tipo_contatto', string='Ruolo')
    name = fields.Char(string='Nome', required=True)
    phone = fields.Char(string='Telefono')
    cellulare = fields.Char(string='Cellulare')
    email = fields.Char(string='Email')
