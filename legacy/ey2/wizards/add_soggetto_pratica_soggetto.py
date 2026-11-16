# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, fields, api
from openerp.exceptions import Warning, ValidationError


class WizAddSoggettoPraticaSoggetto(models.TransientModel):
    _name = "ey2.wiz_add_soggetto_pratica_soggetto"

    _SOGGETTI = [
        ('Altri soggetti', 'Altri soggetti')
    ]

    @api.multi
    def button_aggiungi_soggetto(self):
        self.ensure_one()
        pratica = self.pratica_id
        if self.tipo_soggetto == 'Altri soggetti':
            pratica.compute_prop_arm(self.partner_id, 'pratica_soggetto_id', pratica.id, ruolo=self.ruolo)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey2.pratica_soggetto',
            'view_mode': 'form',
            'res_id': self.pratica_id.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    @api.onchange('tipo_soggetto')
    def onchange_tipo_soggetto(self):
        if self.tipo_soggetto:
            if self.partner_id:
                self.partner_id = False
            bind = {
                'Altri soggetti': 'altri_soggetti'
            }
            return {
                'domain': {
                    'partner_id': [(bind[self.tipo_soggetto], '=', True)]
                }
            }
        else:
            self.partner_id = False

    tipo_soggetto = fields.Selection(_SOGGETTI, string="Tipo soggetto", required=True, default='Altri soggetti')
    pratica_id = fields.Many2one('ey2.pratica_soggetto', string='Pratica', required=True)
    partner_id = fields.Many2one('res.partner', string="Soggetto", required=True)
    ruolo = fields.Char(string="Ruolo")
