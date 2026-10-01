# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(string='Nome completo', required=False, index=True)
    cognome = fields.Char(string='Cognome (rag. sociale)', required=True, index=True)
    nome = fields.Char(string='Nome', index=True)
    iami_cid = fields.Char(string='IAMI CID', index=True)
    codice_unico = fields.Char(string='Codice unico', index=True)
    qualifica_id = fields.Many2one('ey_corsi.qualifica', string='Qualifica', index=True, help='Qualifica di lavoro')
    territorialita = fields.Selection(
        [('italiana', 'Italiana'), ('comunitaria', 'Comunitaria'), ('non_comunitaria', 'Non comunitaria')],
        string='Territorialità', index=True,
    )
    settore_id = fields.Many2one('ey_corsi.settore', string='Settore', help='Settore lavorativo')

    # familiari a carico
    coniuge_a_carico = fields.Boolean(string='Coniuge a carico', index=True)
    figli_a_carico = fields.Integer(string='Figli a carico', index=True)

    # filtraggio
    anagrafica_ey = fields.Boolean(string='Marittimo', index=True)
    personale_ey = fields.Boolean(string='Personale docente', index=True)

    nazionalita_id = fields.Many2one('res.country', string='Cittadinanza', index=True)
    sesso = fields.Selection([('m', 'M'), ('f', 'F')], string='Sesso', index=True)
    stato_civile = fields.Many2one('ey_corsi.stato_civile', string='Stato civile')

    # info nascita
    data_nascita = fields.Date(string='Data di nascita', index=True)
    luogo_nascita_id = fields.Many2one('ey_corsi.luogo_nascita', string='Luogo di nascita', index=True)

    # altre note interne
    blacklist = fields.Boolean(string='Black list')
    dislessia = fields.Boolean(string='Dislessia')

    # filtri curriculum
    esperienza_vela = fields.Boolean(string='Esperienza vela', index=True)
    doppia_qualifica = fields.Boolean(string='Doppia qualifica', index=True)
    imbarcato = fields.Boolean(string='Imbarcato', index=True)

    # CV
    document = fields.Binary(string='C. V.', attachment=True, help='Formato pdf')
    document_fname = fields.Char(string='Nome file')

    documento_ids = fields.One2many('ey_corsi.documento', 'marittimo_id', string='Documenti')
    altro_recapito_ids = fields.One2many('ey_corsi.altro_recapito', 'anagrafica_id', string="Recapiti d'emergenza")
    esperienza_precedente_ids = fields.One2many(
        'ey_corsi.esperienza_precedente', 'anagrafica_id', string='Esperienze precedenti')
    contatto_extra_ids = fields.One2many('ey_corsi.contatto_extra', 'anagrafica_id', string='Contatti')
    info_carta_ids = fields.One2many('ey_corsi.info_carta', 'anagrafica_id', string='Info banca')
    privacy_ids = fields.One2many('ey_corsi.privacy', 'marittimo_id', string='Privacies')
    mailing_list_ids = fields.One2many('ey_corsi.mailing_list', 'marittimo_id', string='Mailing lists')
    servizio_ids = fields.One2many('ey_corsi.servizio', 'anagrafica_id', string='Servizi')
    doc_partner_ids = fields.One2many('ey_corsi.documento_partner', 'partner_id', string='Allegati per anagrafica')
    certificati = fields.One2many('ey_corsi.certificato', 'marittimo_id', string='Certificati (esterni)')
    iscrizione_ids = fields.One2many('ey_corsi.iscrizione', 'marittimo_id', string='Corsi effettuati')
    attestato_frequenza_ids = fields.One2many(
        'ey_corsi.attestato_frequenza', 'marittimo_id', string='Attestati di frequenza')
    certificati_interni = fields.One2many(
        'ey_corsi.certificato_esame', 'marittimo_id', string='Certificati (interni)')

    def write(self, vals):
        result = super().write(vals)
        if 'cognome' in vals or 'nome' in vals:
            for partner in self:
                name = f'{partner.cognome} {partner.nome or ""}'.strip()
                super(ResPartner, partner).write({'name': name})
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'cognome' not in vals and vals.get('name'):
                vals['cognome'] = vals['name']
            if vals.get('cognome'):
                vals['name'] = f"{vals['cognome']} {vals.get('nome') or ''}".strip()
        return super().create(vals_list)
