# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SedeEnte(models.Model):
    _name = "ey_pratiche.sede_ente"

    name = fields.Char(string="Sede", index=True, required=True)


class UfficioEnte(models.Model):
    _name = "ey_pratiche.ufficio_ente"

    name = fields.Char(string="Ufficio", index=True, required=True)


class Ente(models.Model):
    _name = "ey_pratiche.ente"

    @api.depends('denominazione', 'sede_id', 'sede_id.name')
    def _compute_name(self):
        for ente in self:
            name = ""
            if ente.denominazione:
                name += ente.denominazione
            if ente.sede_id:
                name += " (" + ente.sede_id.name + ")"
            ente.name = name

    name = fields.Char(string="name", index=True, compute="_compute_name", store=True)
    denominazione = fields.Char(string="Denominazione", required=True, index=True)
    sede_id = fields.Many2one("ey_pratiche.sede_ente", string="Sede", index=True)
    ufficio_id = fields.Many2one("ey_pratiche.ufficio_ente", string="Ufficio", index=True)
    contatto = fields.Char(string="Contatto")
    fiscalcode = fields.Char(string="Cod. Fiscale", index=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    zip = fields.Char(string='CAP', size=24)
    city = fields.Char(string='City')
    state_id = fields.Many2one("res.country.state", string='Provincia/Stato', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Nazione', ondelete='restrict')
    phone = fields.Char(string="Telefono")
    fax = fields.Char(string="Fax")
    email = fields.Char(string="Email")
