# -*- coding: utf-8 -*-
from odoo import models, fields


class Documento(models.Model):
    _name = 'ey_corsi.documento'
    _description = "Documento d'identità / patente marittimo"
    _rec_name = 'tipo_id'

    marittimo_id = fields.Many2one('res.partner', index=True)
    tipo_id = fields.Many2one('ey_corsi.tipo_documento', string='Tipo', required=True)
    ufficio_id = fields.Many2one('ey_corsi.ente_documenti', string='Ufficio', required=True)
    luogo_rilascio = fields.Char(string='Luogo rilascio')
    numero_documento = fields.Char(string='Numero')
    data_rilascio = fields.Date(string='Rilascio')
    data_scadenza = fields.Date(string='Scadenza', index=True)
    categoria = fields.Char(string='Categ')
    identificatore = fields.Char(string='Identificatore', index=True)
    attivo = fields.Boolean(string='Attivo', index=True, default=True)
    document = fields.Binary(string='Documento', attachment=True, help='Formato pdf')
    document_fname = fields.Char(string='Nome file')


class AltroRecapito(models.Model):
    _name = 'ey_corsi.altro_recapito'
    _description = "Recapito di emergenza"

    anagrafica_id = fields.Many2one('res.partner', string='Anagrafica', index=True)
    name = fields.Char(string='Cognome e nome', required=True, index=True)
    grado_parentela = fields.Char(string='Grado parentela')
    telefono_principale = fields.Char(string='Telefono principale')
    telefono_secondario = fields.Char(string='Telefono secondario')


class EsperienzaPrecedente(models.Model):
    _name = 'ey_corsi.esperienza_precedente'
    _description = 'Esperienza precedente'
    _rec_name = 'qualifica_id'
    _order = 'date_to desc'

    anagrafica_id = fields.Many2one('res.partner', string='Anagrafica', index=True)
    qualifica_id = fields.Many2one('ey_corsi.qualifica', string='Qualifica', required=True, index=True)
    unita_id = fields.Many2one('ey_base.unita', string='Unità', required=True)
    tipo_unita_id = fields.Many2one('ey_base.tipo_unita', related='unita_id.tipo_unita_id', store=True)
    bandiera_id = fields.Many2one('res.country', string='Bandiera')
    date_from = fields.Date(string='Da')
    date_to = fields.Date(string='A', index=True)


class ContattoExtra(models.Model):
    _name = 'ey_corsi.contatto_extra'
    _description = 'Contatto extra'

    anagrafica_id = fields.Many2one('res.partner', string='Anagrafica', index=True)
    tipo_id = fields.Many2one('ey_corsi.tipo_contatto_extra', string='Tipo contatto', required=True)
    dettaglio = fields.Char(string='Dettaglio')
    contatto = fields.Char(string='Recapito', required=True)
    priority = fields.Char(string='Priorità', index=True)


class InfoCarta(models.Model):
    _name = 'ey_corsi.info_carta'
    _description = 'Info carta di pagamento'
    _rec_name = 'intestatario'

    anagrafica_id = fields.Many2one('res.partner', string='Marittimo', index=True)
    intestatario = fields.Char(string='Intestatario', required=True)
    circuito_id = fields.Many2one('ey_corsi.circuito_pagamento', string='Circuito')
    numero_carta = fields.Char(string='Numero')
    cvv = fields.Char(string='CVV', size=10)
    data_rilascio = fields.Date(string='Rilascio')
    data_scadenza = fields.Date(string='Scadenza', index=True)
    identificatore = fields.Char(string='Identificatore', index=True)


class Privacy(models.Model):
    _name = 'ey_corsi.privacy'
    _description = 'Accettazione privacy'
    _order = 'data_scadenza desc'

    marittimo_id = fields.Many2one('res.partner', index=True)
    data_inizio = fields.Date(string='Data accettazione')
    data_scadenza = fields.Date(string='Data scadenza', index=True)
    document = fields.Binary(string='Documento', attachment=True, help='Formato pdf')
    document_fname = fields.Char(string='Nome file')


class MailingList(models.Model):
    _name = 'ey_corsi.mailing_list'
    _description = 'Iscrizione mailing list'
    _order = 'data_scadenza desc'

    marittimo_id = fields.Many2one('res.partner', index=True)
    data_inizio = fields.Date(string='Data accettazione')
    data_scadenza = fields.Date(string='Data scadenza', index=True)
    document = fields.Binary(string='Documento', attachment=True, help='Formato pdf')
    document_fname = fields.Char(string='Nome file')


class Servizio(models.Model):
    _name = 'ey_corsi.servizio'
    _description = 'Servizio reso al marittimo'
    _order = 'inizio_servizio desc'

    anagrafica_id = fields.Many2one('res.partner', string='Anagrafica', index=True)
    name = fields.Char(string='Descrizione servizio', required=True, index=True)
    inizio_servizio = fields.Date(string='Inizio servizio', index=True, required=True)
    fine_servizio = fields.Date(string='Fine servizio', index=True, required=True)
    costo = fields.Float(string='Costo (in euro)')
    scadenzario = fields.Boolean(string='Scadenzario', index=True)


class DocumentoPartner(models.Model):
    _name = 'ey_corsi.documento_partner'
    _description = 'Documento amministrativo partner'
    _order = 'data_inserimento desc'

    partner_id = fields.Many2one('res.partner', index=True)
    nave_id = fields.Many2one('ey_base.unita', index=True)
    name = fields.Char(string='Descrizione', required=True, index=True)
    data_inserimento = fields.Date(string='Data inserimento', default=fields.Date.today)
    data_documento = fields.Date(string='Data documento')
    document = fields.Binary(string='Documento', attachment=True)
    document_fname = fields.Char(string='Nome file')
