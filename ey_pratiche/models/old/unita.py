# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Unita(models.Model):
    _inherit = 'ey_base.unita'

    # sezione pratiche collegate
    imbarco_sbarco_ids = fields.One2many("ey_pratiche.pratica_nave", 'partner_id', string="Imbarchi/Sbarchi", domain=[('tipo_pratica', 'in', ['Imbarco', 'Sbarco'])])
    altra_pratica_ids = fields.One2many("ey_pratiche.pratica_nave", 'partner_id', string="Altre pratiche", domain=[('tipo_pratica', 'not in', ['Imbarco', 'Sbarco'])])
