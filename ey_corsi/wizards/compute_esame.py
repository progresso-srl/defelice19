# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizAssegnaCertificato(models.TransientModel):
    _name = 'ey_corsi.wiz_assegna_certificato'
    _description = 'Assegna certificati (interni)'

    def _get_iscrizioni(self, wiz_iscritti):
        marittimi_ids = wiz_iscritti.mapped('marittimo_id').ids
        esame_id = wiz_iscritti[:1].esame_id.id
        return self.env['ey_corsi.iscrizione_esame'].search([
            ('marittimo_id', 'in', marittimi_ids),
            ('esame_id', '=', esame_id),
        ])

    def _default_date_start(self):
        iscritti = self.env['ey_corsi.wiz_iscritti_esame'].browse(self.env.context.get('active_ids', []))
        for iscrizione in self._get_iscrizioni(iscritti):
            if iscrizione.corso_collegato_id:
                return iscrizione.corso_collegato_id.data_inizio
        return False

    def _default_date_end(self):
        iscritti = self.env['ey_corsi.wiz_iscritti_esame'].browse(self.env.context.get('active_ids', []))
        for iscrizione in self._get_iscrizioni(iscritti):
            if iscrizione.corso_collegato_id:
                return iscrizione.corso_collegato_id.data_fine
        return False

    data_rilascio = fields.Date(string='Data inizio corso collegato', required=True, default=_default_date_start)
    data_scadenza = fields.Date(string='Data fine corso collegato', required=True, default=_default_date_end)

    @api.constrains('data_rilascio', 'data_scadenza')
    def _validate_fields(self):
        for wiz in self:
            if wiz.data_scadenza and wiz.data_rilascio > wiz.data_scadenza:
                raise ValidationError('Date invertite')

    def button_assegna_certificato(self):
        self.ensure_one()
        certificato_model = self.env['ey_corsi.certificato_esame']
        iscritti_ids = self.env.context['active_ids']
        iscritti = self.env['ey_corsi.wiz_iscritti_esame'].browse(iscritti_ids)
        certificati = certificato_model
        for wiz in iscritti:
            domain_af = [('esame_id', '=', wiz.esame_id.id), ('marittimo_id', '=', wiz.marittimo_id.id)]
            certificato = certificato_model.search(domain_af)
            if not certificato:
                n_seq = wiz.esame_id.template_id.numero_certificato_esame + 1
                certificato_vals = {
                    'data_rilascio': self.data_rilascio,
                    'data_scadenza': self.data_scadenza,
                    'esame_id': wiz.esame_id.id,
                    'marittimo_id': wiz.marittimo_id.id,
                    'numero_sequenza': n_seq,
                }
                certificato = certificato_model.create(certificato_vals)
                wiz.esame_id.template_id.numero_certificato_esame = n_seq
            certificati |= certificato
        if not certificati:
            return {'type': 'ir.actions.act_window_close'}
        return self.env.ref('ey_corsi.action_report_certificato_esame').report_action(certificati)


class WizIscrittiEsame(models.TransientModel):
    _name = 'ey_corsi.wiz_iscritti_esame'
    _description = "Tree degli iscritti all'esame"

    marittimo_id = fields.Many2one(
        'res.partner', string='Marittimo', domain=[('anagrafica_ey', '=', True)], required=True, index=True)
    superato_set = fields.Boolean(index=True)
    esame_id = fields.Many2one('ey_corsi.esame', string='Esame', required=True, index=True)
    data_nascita = fields.Date(string='Data di nascita', related='marittimo_id.data_nascita')
    luogo_nascita_id = fields.Many2one(
        'ey_corsi.luogo_nascita', string='Luogo di nascita', related='marittimo_id.luogo_nascita_id')
    nazionalita_id = fields.Many2one('res.country', string='Cittadinanza', related='marittimo_id.nazionalita_id')

    def button_esame_superato(self):
        for wiz in self:
            iscrizione = self.env['ey_corsi.iscrizione_esame'].search([
                ('marittimo_id', '=', wiz.marittimo_id.id),
                ('esame_id', '=', wiz.esame_id.id),
            ], limit=1)
            iscrizione.esame_superato = True
            wiz.superato_set = True
