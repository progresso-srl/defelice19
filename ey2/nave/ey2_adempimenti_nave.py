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

from openerp import fields, models, api


class TipoAdempimentoNave(models.Model):
    _name = "ey2.tipo_adempimento_nave"

    name = fields.Char(string="Tipo", index=True, required=True)


class AdempimentoNave(models.Model):
    _name = "ey2.adempimento_nave"

    name = fields.Char(string="Descrizione", index=True, required=True)
    tipo_id = fields.Many2one("ey2.tipo_adempimento_nave", string="Tipo", index=True)