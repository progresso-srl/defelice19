# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # flag per filtrare i partner per ruolo nel settore nautico
    armatore_proprietario = fields.Boolean(
        string='Armatore / Proprietario', index=True,
    )
    altri_soggetti = fields.Boolean(string='Altri soggetti', index=True)

    # navi in cui il partner è attivo come proprietario o armatore
    nave_arm_prop_ids = fields.One2many(
        comodel_name='ey_base.proprietario_armatore',
        inverse_name='partner_id',
        string='Navi',
        domain=[('riferimento', '=', True)],
    )
    # ruoli ricoperti dal partner su navi
    rappresentante_ruolo_ids = fields.One2many(
        comodel_name='ey_base.rappresentante_ruolo',
        inverse_name='partner_id',
        string='Ruoli su navi',
    )
