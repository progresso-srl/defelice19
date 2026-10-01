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


class WizCreaProssimoPrevisionale(models.TransientModel):
    _name = "ey2.wiz_crea_prossimo_previsionale"

    def _compute_next_period(self):
        if not self.contratto_id.previsionale_ids:
            return {
                'mese':  self.contratto_id.mese_inizio,
                'anno': self.contratto_id.anno_inizio
            }
        else:
            mesi_periodicita = self.contratto_id.periodo_id.mesi % 12
            anni_periodicita = self.contratto_id.periodo_id.mesi / 12
            next_year = self.contratto_id.mese_inizio
            next_month = self.contratto_id.anno_inizio
            for period in self.contratto_id.previsionale_ids:
                if period.anno_inizio > next_year:
                    next_year = period.anno_inizio
                    next_month = period.mese_inizio
                elif period.anno_inizio == next_year:
                    if period.mese_inizio > next_month:
                        next_month = period.mese_inizio
            next_year = int(next_year) + anni_periodicita
            next_month = int(next_month) + mesi_periodicita
            if next_month > 12:
                next_year += next_month / 12
                next_month = next_month % 12
            next_year = str(next_year)
            next_month = str(next_month)
            if len(next_month) == 1:
                next_month = '0' + next_month
        return {
            'mese': next_month,
            'anno': next_year
        }

    @api.multi
    def button_crea_previsionale(self):
        self.ensure_one()
        period = self._compute_next_period()
        previsionale_vals = {
            'contratto_id': self.contratto_id.id,
            'mese_inizio': period['mese'],
            'anno_inizio': period['anno']
        }
        previsionale = self.env['ey2.previsionale_nave'].create(previsionale_vals)
        if self.periodo_precedente_id:
            for spesa in self.periodo_precedente_id.spesa_ids:
                spesa_vals = {
                    'previsionale_id': previsionale.id,
                    'tipo_id': spesa.tipo_id.id,
                    'name': spesa.name,
                    'previsto': spesa.effettivo
                }
                self.env['ey2.spesa_nave'].create(spesa_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey2.previsionale_nave',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': previsionale.id,
            'flags': {'initial_mode': 'edit'}
        }

    contratto_id = fields.Many2one("ey2.contratto_nave", string="Contratto", required=True)
    periodo_precedente_id = fields.Many2one("ey2.previsionale_nave", string="Previsionale da duplicare")