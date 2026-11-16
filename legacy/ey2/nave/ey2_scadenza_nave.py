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


class CategoriaAgenda(models.Model):
    _name = "ey2.categoria_agenda_nave"

    name = fields.Char("Categoria", index=True, required=True)


class Agenda(models.Model):
    _name = "ey2.agenda_nave"
    _order = "data_scadenza desc"

    name = fields.Char(string="Descrizione", index=True, required=True)
    categoria_id = fields.Many2one("ey2.categoria_agenda_nave", string="Categoria", required=True, index=True)
    categoria_name = fields.Char(string="Nome categoria", related="categoria_id.name")
    uniq_id = fields.Char(index=True)
    data_scadenza = fields.Date(string="Data scadenza", index=True, required=True)
    data_alert = fields.Date(string="Data alert", index=True, required=True)
    completato = fields.Boolean(string="Completato", index=True)
