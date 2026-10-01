# -*- coding: utf-8 -*-

from odoo import api, fields, models

class EyPraticheArgomentoNormativa(models.Model):
    _name = "ey_pratiche.argomento_normativa"

    name = fields.Char(string="Argomento", index=True, required=True)