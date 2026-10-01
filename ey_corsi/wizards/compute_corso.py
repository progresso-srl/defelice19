# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizAssegnaAttestato(models.TransientModel):
    _name = 'ey_corsi.wiz_assegna_attestato'
    _description = 'Assegna attestati di frequenza'

    data_rilascio = fields.Date(string='Data assegnazione', required=True, default=fields.Date.today)
    data_scadenza = fields.Date(string='Data scadenza', required=True)

    @api.constrains('data_rilascio', 'data_scadenza')
    def _validate_fields(self):
        for wiz in self:
            if wiz.data_scadenza and wiz.data_rilascio > wiz.data_scadenza:
                raise ValidationError('La data di scadenza deve essere successiva rispetto a quella di emissione')

    def button_assegna_certificato(self):
        self.ensure_one()
        attestato_model = self.env['ey_corsi.attestato_frequenza']
        iscritti_ids = self.env.context['active_ids']
        iscritti = self.env['ey_corsi.wiz_iscritti_corso'].browse(iscritti_ids)
        attestati = attestato_model
        for wiz in iscritti:
            domain_af = [('corso_id', '=', wiz.corso_id.id), ('marittimo_id', '=', wiz.marittimo_id.id)]
            attestato = attestato_model.search(domain_af)
            if not attestato:
                n_seq = wiz.corso_id.template_id.numero_attestato_frequenza + 1
                attestato_vals = {
                    'data_rilascio': self.data_rilascio,
                    'data_scadenza': self.data_scadenza,
                    'corso_id': wiz.corso_id.id,
                    'marittimo_id': wiz.marittimo_id.id,
                    'numero_sequenza': n_seq,
                }
                attestato = attestato_model.create(attestato_vals)
                wiz.corso_id.template_id.numero_attestato_frequenza = n_seq
            attestati |= attestato
        if not attestati:
            return {'type': 'ir.actions.act_window_close'}
        return self.env.ref('ey_corsi.action_report_attestato_frequenza').report_action(attestati)


class WizIscrittiCorso(models.TransientModel):
    _name = 'ey_corsi.wiz_iscritti_corso'
    _description = "Tree degli iscritti al corso"

    marittimo_id = fields.Many2one(
        'res.partner', string='Marittimo', domain=[('anagrafica_ey', '=', True)], required=True, index=True)
    superato_set = fields.Boolean(index=True)
    corso_id = fields.Many2one('ey_corsi.corso', string='Corso', required=True, index=True)
    data_nascita = fields.Date(string='Data di nascita', related='marittimo_id.data_nascita')
    luogo_nascita_id = fields.Many2one(
        'ey_corsi.luogo_nascita', string='Luogo di nascita', related='marittimo_id.luogo_nascita_id')
    nazionalita_id = fields.Many2one('res.country', string='Cittadinanza', related='marittimo_id.nazionalita_id')

    def button_corso_superato(self):
        for wiz in self:
            iscrizione = self.env['ey_corsi.iscrizione'].search([
                ('marittimo_id', '=', wiz.marittimo_id.id),
                ('corso_id', '=', wiz.corso_id.id),
            ], limit=1)
            iscrizione.corso_superato = True
            wiz.superato_set = True
