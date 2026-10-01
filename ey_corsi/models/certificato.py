# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime


class Certificato(models.Model):
    _name = 'ey_corsi.certificato'
    _description = 'Certificato rilasciato da ente terzo'
    _rec_name = 'name'

    marittimo_id = fields.Many2one('res.partner', string='Marittimo', index=True)
    name = fields.Char(string='Nome', compute='_compute_name')
    descrizione_id = fields.Many2one('ey_corsi.descrizione_certificato', string='Descrizione', required=True)
    ente_certificati_id = fields.Many2one('ey_corsi.ente_certificati', string='Ufficio di rilascio')
    data_rilascio = fields.Date(string='Data rilascio', required=True, index=True, default=fields.Date.today)
    data_scadenza = fields.Date(string='Data scadenza', index=True, required=True)
    document = fields.Binary(string='Documento', attachment=True, help='Formato pdf')
    document_fname = fields.Char(string='Nome file')
    scaduto = fields.Boolean(compute='_compute_scaduto', index=True)
    attivo = fields.Boolean(string='Attivo', default=True)

    @api.depends('descrizione_id', 'descrizione_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.descrizione_id.name or ''

    @api.depends('data_scadenza')
    def _compute_scaduto(self):
        for rec in self:
            rec.scaduto = bool(rec.data_scadenza) and datetime.today().date() > rec.data_scadenza

    # ── aggancio automatico all'agenda scadenze marittimo ──────────────
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._sync_agenda(create=True)
        return records

    def write(self, vals):
        result = super().write(vals)
        if any(k in vals for k in ('data_scadenza', 'descrizione_id')):
            for rec in self:
                rec._sync_agenda(create=False)
        return result

    def unlink(self):
        for rec in self:
            self.env['ey_corsi.agenda_marittimo'].search([
                ('uniq_id', '=', f'ey_certificato-{rec.id}')
            ]).unlink()
        return super().unlink()

    def _sync_agenda(self, create=False):
        """Crea o aggiorna la voce di agenda collegata al certificato."""
        self.ensure_one()
        if not self.data_scadenza:
            return
        AgendaMarittimo = self.env['ey_corsi.agenda_marittimo']

        uniq = f'ey_certificato-{self.id}'
        data_alert = self.data_scadenza - relativedelta(months=3)
        agenda_vals = {
            'name': f'{self.descrizione_id.name} - SCAD. CERT. IAMI - {self.marittimo_id.name}',
            'categoria_id': self.env.ref('ey_corsi.agenda_cert_ente_terzi').id,
            'uniq_id': uniq,
            'data_scadenza': self.data_scadenza,
            'data_alert': data_alert,
        }
        voce = AgendaMarittimo.search([('uniq_id', '=', uniq)], limit=1)
        if voce:
            voce.write(agenda_vals)
        elif create:
            AgendaMarittimo.create(agenda_vals)
