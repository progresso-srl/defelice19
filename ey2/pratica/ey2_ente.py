# -*- coding: utf-8 -*-
##############################################################################
#
#    CASE module for OpenERP
#    Copyright (C) 20013 Future Tech srl (http://www.futuretechsrl.it).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class SedeEnte(models.Model):
    _name = "ey2.sede_ente"

    name = fields.Char(string="Sede", index=True, required=True)


class UfficioEnte(models.Model):
    _name = "ey2.ufficio_ente"

    name = fields.Char(string="Ufficio", index=True, required=True)


class Ente(models.Model):
    _name = "ey2.ente"

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
    sede_id = fields.Many2one("ey2.sede_ente", string="Sede", index=True)
    ufficio_id = fields.Many2one("ey2.ufficio_ente", string="Ufficio", index=True)
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
