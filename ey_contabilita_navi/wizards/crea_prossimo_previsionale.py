from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizCreaProssimoPrevisionale(models.TransientModel):
    _name = "ey_contabilita_navi.wiz_crea_prossimo_previsionale"

    def _calcola_prossimo_periodo(self):
        if not self.contratto_id.previsionale_ids:
            return {
                'mese':  self.contratto_id.mese_inizio,
                'anno': self.contratto_id.anno_inizio
            }
        else:
            mesi_periodicita = self.contratto_id.periodo_id.mesi % 12
            anni_periodicita = self.contratto_id.periodo_id.mesi / 12
            next_year = self.contratto_id.anno_inizio
            next_month = self.contratto_id.mese_inizio
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

    def button_crea_previsionale(self):
        self.ensure_one()
        period = self._calcola_prossimo_periodo()
        previsionale_vals = {
            'contratto_id': self.contratto_id.id,
            'mese_inizio': period['mese'],
            'anno_inizio': period['anno']
        }
        previsionale = self.env['ey_contabilita_navi.previsionale_contratto'].create(previsionale_vals)
        if self.periodo_precedente_id:
            for spesa in self.periodo_precedente_id.spesa_ids:
                spesa_vals = {
                    'previsionale_id': previsionale.id,
                    'tipo_id': spesa.tipo_id.id,
                    'name': spesa.name,
                    'previsto': spesa.effettivo
                }
                self.env['ey_contabilita_navi.spesa_previsionale'].create(spesa_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey_contabilita_navi.previsionale_contratto',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': previsionale.id,
            'flags': {'initial_mode': 'edit'}
        }

    contratto_id = fields.Many2one("ey_contabilita_navi.contratto_nave", string="Contratto", required=True)
    periodo_precedente_id = fields.Many2one("ey_contabilita_navi.previsionale_contratto", string="Previsionale da duplicare")
