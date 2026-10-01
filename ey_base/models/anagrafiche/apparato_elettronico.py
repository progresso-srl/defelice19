# -*- coding: utf-8 -*-
from odoo import models, fields


class ApparatoElettronico(models.Model):
    _name = 'ey_base.apparato_elettronico'
    _description = 'Apparato elettronico di navigazione'
    _rec_name = 'modello'

    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    tipo_id = fields.Many2one(
        'ey_base.tipo_app_elett', string='Apparato',
        required=True, index=True,
    )
    marca_id = fields.Many2one(
        'ey_base.marca_app_elett', string='Marca',
        required=True, index=True,
    )
    modello = fields.Char(string='Modello')
    caratteristiche = fields.Char(string='Caratteristiche')

    document = fields.Binary(string='Allegato', attachment=True)
    document_fname = fields.Char(string='Nome file')
