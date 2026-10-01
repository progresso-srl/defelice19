# -*- coding: utf-8 -*-
from odoo import models, fields


class EquipaggioNave(models.Model):
    _name = 'ey_base.equipaggio_nave'
    _description = 'Equipaggio nave'
    _order = 'data_imbarco desc'

    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    partner_id = fields.Many2one(
        'res.partner', string='Cognome e nome',
        required=True, index=True,
    )
    identificatore = fields.Char(string='Identificatore', index=True)
    inizio = fields.Date(string='Inizio')
    fine = fields.Date(string='Fine')
    data_imbarco = fields.Date(string='Data imbarco')
    data_sbarco = fields.Date(string='Data sbarco')
    ruolo = fields.Char(string='Ruolo')
    riferimento = fields.Boolean(string='Attivo', index=True, default=True)
