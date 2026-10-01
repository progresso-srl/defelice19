# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CertificatoBordo(models.Model):
    _name = 'ey_base.certificato_bordo'
    _description = 'Certificato di bordo'
    _rec_name = 'identificatore'
    _order = 'data_scadenza desc'

    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    tipo_id = fields.Many2one(
        'ey_base.tipo_cert_bordo', string='Tipo certificato',
        required=True, index=True,
    )
    identificatore = fields.Char(string='Identificatore')
    numero_documento = fields.Char(string='Nr documento')
    ente_id = fields.Many2one('ey_base.ente_sorveglianza', string='Ente', index=True)
    luogo_rilascio = fields.Char(string='Luogo rilascio', index=True)
    data_rilascio = fields.Date(string='Data rilascio', required=True)
    data_scadenza = fields.Date(string='Data scadenza', required=True)
    data_preavviso = fields.Date(string='Data preavviso', required=True)
    attivo = fields.Boolean(string='Attivo', default=True)

    # ── allegato: attachment=True gestisce tutto Odoo nativamente ────
    document = fields.Binary(string='Allegato', attachment=True)
    document_fname = fields.Char(string='Nome file')

    # ── aggancio automatico all'agenda scadenze ───────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._sync_agenda(create=True)
        return records

    def write(self, vals):
        result = super().write(vals)
        if any(k in vals for k in ('data_scadenza', 'data_preavviso', 'tipo_id')):
            for rec in self:
                rec._sync_agenda(create=False)
        return result

    def unlink(self):
        for rec in self:
            self.env['ey_base.agenda_nave'].search([
                ('uniq_id', '=', f'certificato_bordo-{rec.id}')
            ]).unlink()
        return super().unlink()

    def _sync_agenda(self, create=False):
        """Crea o aggiorna la voce di agenda collegata al certificato."""
        self.ensure_one()
        AgendaNave = self.env['ey_base.agenda_nave']
        CategoriaAgenda = self.env['ey_base.categoria_agenda_nave']

        categoria = CategoriaAgenda.search(
            [('name', '=', 'Scadenza Certificato Nave')], limit=1
        )
        if not categoria:
            categoria = CategoriaAgenda.create({'name': 'Scadenza Certificato Nave'})

        uniq = f'certificato_bordo-{self.id}'
        agenda_vals = {
            'name': f'{self.nave_id.name} — {self.tipo_id.name}',
            'categoria_id': categoria.id,
            'uniq_id': uniq,
            'data_scadenza': self.data_scadenza,
            'data_alert': self.data_preavviso,
        }
        voce = AgendaNave.search([('uniq_id', '=', uniq)], limit=1)
        if voce:
            voce.write(agenda_vals)
        elif create:
            AgendaNave.create(agenda_vals)
