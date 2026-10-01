# -*- coding: utf-8 -*-
from odoo import models, fields


class RappresentanteRuolo(models.Model):
    _name = 'ey_base.rappresentante_ruolo'
    _description = 'Rappresentante con ruolo su nave'

    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner di riferimento', index=True)
    rappresentante_id = fields.Many2one(
        'res.partner', string='Cognome e nome / RS',
        required=True, index=True,
    )
    ruolo_id = fields.Many2one(
        'ey_base.ruolo_rappresentante', string='Ruolo', required=True,
    )
    identificatore = fields.Char(string='Identificatore', index=True)
    testo_descrittivo = fields.Char(string='Descrizione')
    riferimento = fields.Boolean(string='Attivo', index=True, default=True)
