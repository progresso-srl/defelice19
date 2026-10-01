# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Qualifica(models.Model):
    _name = 'ey_corsi.qualifica'
    _description = 'Qualifica marittimo'
    _rec_name = 'name'

    name = fields.Char(string='Qualifica', required=True, index=True)


class Settore(models.Model):
    _name = 'ey_corsi.settore'
    _description = 'Settore lavorativo'
    _rec_name = 'name'

    name = fields.Char(string='Settore', required=True, index=True)


class StatoCivile(models.Model):
    _name = 'ey_corsi.stato_civile'
    _description = 'Stato civile'
    _rec_name = 'name'

    name = fields.Char(string='Stato civile', required=True, index=True)


class LuogoNascita(models.Model):
    _name = 'ey_corsi.luogo_nascita'
    _description = 'Luogo di nascita'
    _rec_name = 'name'

    name = fields.Char(compute='_compute_name', store=True, index=True)
    city = fields.Char(string='Città', required=True, index=True)
    state_id = fields.Many2one('res.country.state', string='Provincia/Stato', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Nazione', required=True, index=True)

    @api.depends('city', 'country_id')
    def _compute_name(self):
        for luogo in self:
            if luogo.city and luogo.country_id:
                luogo.name = f'{luogo.city} ({luogo.country_id.name})'
            else:
                luogo.name = luogo.city or False


class CircuitoPagamento(models.Model):
    _name = 'ey_corsi.circuito_pagamento'
    _description = 'Istituto / circuito di pagamento'
    _rec_name = 'name'

    name = fields.Char(string='Istituto / Circuito', required=True, index=True)


class TipoContattoExtra(models.Model):
    _name = 'ey_corsi.tipo_contatto_extra'
    _description = 'Tipo contatto extra'
    _rec_name = 'name'

    name = fields.Char(string='Tipo contatto', required=True, index=True)


class TipoDocumento(models.Model):
    _name = 'ey_corsi.tipo_documento'
    _description = 'Tipo documento marittimo'
    _rec_name = 'name'

    name = fields.Char(string='Tipo documento', required=True, index=True)


class EnteDocumenti(models.Model):
    _name = 'ey_corsi.ente_documenti'
    _description = 'Ente rilascio documenti'
    _rec_name = 'name'

    name = fields.Char(string='Nome', required=True, index=True)


class EnteCertificati(models.Model):
    _name = 'ey_corsi.ente_certificati'
    _description = 'Ente certificatore'
    _rec_name = 'name'

    name = fields.Char(string='Nome', required=True, index=True)


class DescrizioneCertificato(models.Model):
    _name = 'ey_corsi.descrizione_certificato'
    _description = 'Descrizione certificato'
    _rec_name = 'name'

    name = fields.Char(string='Descrizione', required=True, size=242)

    _name_unique = models.Constraint(
        'UNIQUE(name)',
        'Questa descrizione è già stata utilizzata!',
    )


class EnteCorsi(models.Model):
    _name = 'ey_corsi.ente_corsi'
    _description = 'Ente organizzatore corsi'
    _rec_name = 'name'

    name = fields.Char(string='Nome', required=True, index=True)


class SedeCorso(models.Model):
    _name = 'ey_corsi.sede_corso'
    _description = 'Sede corso'
    _rec_name = 'name'

    name = fields.Char(string='Sede', required=True, index=True)


class DescrizioneCosto(models.Model):
    _name = 'ey_corsi.descrizione_costo'
    _description = 'Descrizione voce di costo'
    _rec_name = 'name'

    name = fields.Char(string='Descrizione', required=True, index=True)


class TipoDocumentoCorso(models.Model):
    _name = 'ey_corsi.tipo_documento_corso'
    _description = 'Tipo documento corso'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class TipoDocumentoEsame(models.Model):
    _name = 'ey_corsi.tipo_documento_esame'
    _description = 'Tipo documento esame'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class CarrieraTplCorso(models.Model):
    _name = 'ey_corsi.carriera_tpl_corso'
    _description = 'Carriera (template corso)'
    _rec_name = 'name'

    name = fields.Char(string='Carriera', required=True, index=True)
    percorso_formativo_ids = fields.One2many(
        comodel_name='ey_corsi.percorso_tpl_corso',
        inverse_name='carriera_id',
        string='Percorsi formativi',
    )

    # NON portato: list_carriere_sito() (integrazione sito pubblico, fuori scope)


class PercorsoTplCorso(models.Model):
    _name = 'ey_corsi.percorso_tpl_corso'
    _description = 'Percorso formativo (template corso)'
    _rec_name = 'name'

    name = fields.Char(string='Percorso formativo', required=True, index=True)
    carriera_id = fields.Many2one(
        comodel_name='ey_corsi.carriera_tpl_corso', string='Carriera',
        required=True, index=True,
    )
    template_corsi = fields.Many2many(
        comodel_name='ey_corsi.template_corso',
        relation='ey_corsi_tpl_corso_percorso_rel',
        string='Template corsi', index=True,
    )

    # NON portato: list_percorsi_sito() (integrazione sito pubblico, fuori scope)
