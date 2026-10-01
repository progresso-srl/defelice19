# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    iscrizione_id = fields.Many2one(
        'ey_corsi.iscrizione', string='Iscrizione corso collegata', index=True)
    iscrizione_esame_id = fields.Many2one(
        'ey_corsi.iscrizione_esame', string='Iscrizione esame collegata', index=True)
