# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

_FORMATO_DOCUMENTO = [
    ('odt', 'odt'),
    ('ods', 'ods'),
]

_DOC_CORSO_CATEGORIE = [
    ('standard', 'Standard'),
    ('attestati', 'Attestati'),
]

_TIPO_CHIAVE = [
    ('valore', 'Valore'),
    ('campo', 'Campo'),
]


class ChiaveTplCorso(models.Model):
    _name = 'ey_corsi.chiave_tpl'
    _description = 'Chiave template corso'
    _order = 'priority asc'

    tpl_id = fields.Many2one('ey_corsi.template_corso', index=True, ondelete='cascade')
    chiave = fields.Char(string='Chiave', required=True, index=True)
    descrizione = fields.Char(string='Descrizione')
    tipo_chiave = fields.Selection(_TIPO_CHIAVE, string='Tipo', default='campo', required=True, index=True)
    valore = fields.Char(string='Valore')
    priority = fields.Integer(string='Priorità', default=0, index=True)

    @api.onchange('tipo_chiave')
    def _onchange_tipo_chiave(self):
        if self.tipo_chiave == 'campo':
            self.valore = ''


class ChiaveTplEsame(models.Model):
    _name = 'ey_corsi.chiave_tpl_esame'
    _description = 'Chiave template esame'
    _order = 'priority asc'

    tpl_id = fields.Many2one('ey_corsi.template_esame', index=True, ondelete='cascade')
    chiave = fields.Char(string='Chiave', required=True, index=True)
    descrizione = fields.Char(string='Descrizione')
    tipo_chiave = fields.Selection(_TIPO_CHIAVE, string='Tipo', default='campo', required=True, index=True)
    valore = fields.Char(string='Valore')
    priority = fields.Integer(string='Priorità', default=0, index=True)

    @api.onchange('tipo_chiave')
    def _onchange_tipo_chiave(self):
        if self.tipo_chiave == 'campo':
            self.valore = ''


class DocumentoTplCorso(models.Model):
    _name = 'ey_corsi.documento_tpl_corso'
    _description = 'Documento allegato al template corso'
    _order = 'priority asc'

    name = fields.Char(string='Nome', required=True, index=True)
    tpl_id = fields.Many2one('ey_corsi.template_corso', index=True, ondelete='cascade')
    format = fields.Selection(_FORMATO_DOCUMENTO, string='Formato', required=True, default='odt', index=True)
    document = fields.Binary(string='Documento', attachment=True)
    document_fname = fields.Char(string='Nome file')
    priority = fields.Integer(string='Priorità', default=0, index=True)
    duplica = fields.Boolean(string='Duplica', default=True)
    category = fields.Selection(_DOC_CORSO_CATEGORIE, string='Categoria', default='standard')


class DocumentoTplEsame(models.Model):
    _name = 'ey_corsi.documento_tpl_esame'
    _description = 'Documento allegato al template esame'
    _order = 'priority asc'

    name = fields.Char(string='Nome', required=True, index=True)
    tpl_id = fields.Many2one('ey_corsi.template_esame', index=True, ondelete='cascade')
    format = fields.Selection(_FORMATO_DOCUMENTO, string='Formato', required=True, default='odt', index=True)
    document = fields.Binary(string='Documento', attachment=True)
    document_fname = fields.Char(string='Nome file')
    priority = fields.Integer(string='Priorità', default=0, index=True)
    duplica = fields.Boolean(string='Duplica', default=True)


class TemplateCorso(models.Model):
    _name = 'ey_corsi.template_corso'
    _description = 'Template corso'

    _SVOLGIMENTO_CORSO = [
        ('interno', 'Interno'),
        ('esterno', 'Esterno'),
    ]

    created = fields.Boolean(string='Creato', index=True)
    attivo = fields.Boolean(string='Attivo', default=True, index=True)
    name = fields.Char(string='Nome corso', required=True, index=True)
    prefisso = fields.Char(string='Prefisso', index=True)
    nr_approvazione = fields.Char(string='Numero approvazione')
    prezzo_corso = fields.Float(string='Prezzo corso', index=True)
    con_esame = fields.Selection(
        [('si', 'Sì'), ('no', 'No')], string='Con esame', default='si', required=True, index=True)

    logo_azienda = fields.Binary(string='Logo azienda', attachment=True)
    logo_ente = fields.Binary(string='Logo ente', attachment=True)

    max_iscritti = fields.Integer(string='Numero massimo iscrizioni', required=True, index=True)
    min_iscritti = fields.Integer(string='Numero minimo di iscritti')
    numero_attestato_frequenza = fields.Integer(string='Numero ultimo attestato di frequenza', required=True, index=True)
    data_scadenza_ca = fields.Date(string='Scadenza certificato accreditamento')

    registration_form = fields.Binary(
        string='Template registration form (odt)', attachment=True, required=True)
    rf_fname = fields.Char(string='Nome file registration form')
    certificato_frequenza = fields.Binary(
        string='Template attestato di frequenza (odt)', attachment=True, required=True)
    cf_fname = fields.Char(string='Nome file attestato')

    ente_corsi_id = fields.Many2one('ey_corsi.ente_corsi', string='Ente')
    template_esame_id = fields.Many2one('ey_corsi.template_esame', string='Template esame collegato', index=True)

    documento_tpl_ids = fields.One2many('ey_corsi.documento_tpl_corso', 'tpl_id', string='Documenti')
    chiave_ids = fields.One2many('ey_corsi.chiave_tpl', 'tpl_id', string='Chiavi')

    # campi per sito (dati soltanto: la pubblicazione sul sito non è in scope di questa migrazione)
    percorsi_formativi = fields.Many2many(
        comodel_name='ey_corsi.percorso_tpl_corso',
        relation='ey_corsi_tpl_corso_percorso_rel',
        string='Percorsi formativi', index=True,
    )
    titolo_corso = fields.Char(string='Titolo corso (per sito)', required=True)
    descrizione_corso = fields.Text(string='Descrizione corso')
    corso_int_est = fields.Selection(_SVOLGIMENTO_CORSO, string='Corso interno/esterno', index=True)
    pubblicato = fields.Boolean(string='Pubblicato sul sito', index=True)

    costo_ids = fields.One2many('ey_corsi.costo_corso', 'template_corso_id', string='Costi')
    documento_ids = fields.One2many('ey_corsi.documento_corso', 'template_id', string='Documenti corso')

    _name_unique = models.Constraint('UNIQUE(name)', 'Nome già utilizzato!')

    @api.onchange('name')
    def _onchange_name(self):
        if not self.titolo_corso and self.name:
            self.titolo_corso = self.name

    @api.constrains('max_iscritti')
    def _check_max_iscritti(self):
        for template in self:
            if template.max_iscritti <= 0:
                raise ValidationError('Numero massimo partecipanti errato')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        templates = super().create(vals_list)
        for template in templates:
            template._sync_agenda_scadenza_ca()
        return templates

    def write(self, vals):
        result = super().write(vals)
        if 'data_scadenza_ca' in vals:
            for template in self:
                template._sync_agenda_scadenza_ca()
        return result

    def unlink(self):
        # STEP 7: impedire la cancellazione se esistono corsi collegati al template
        for rec in self:
            self.env['ey_corsi.agenda_marittimo'].search([
                ('uniq_id', '=', f'template_corso-{rec.id}')
            ]).unlink()
        return super().unlink()

    def copy(self, default=None):
        raise ValidationError('Impossibile duplicare un template corso (problemi di integrità)')

    def _sync_agenda_scadenza_ca(self):
        self.ensure_one()
        if not self.data_scadenza_ca:
            return
        AgendaMarittimo = self.env['ey_corsi.agenda_marittimo']
        uniq = f'template_corso-{self.id}'
        agenda_vals = {
            'name': f'{self.name} - SCAD. CERT. ACCREDITAMENTO',
            'categoria_id': self.env.ref('ey_corsi.agenda_cert_acc').id,
            'uniq_id': uniq,
            'data_scadenza': self.data_scadenza_ca,
            'data_alert': self.data_scadenza_ca - relativedelta(months=3),
        }
        voce = AgendaMarittimo.search([('uniq_id', '=', uniq)], limit=1)
        if voce:
            voce.write(agenda_vals)
        else:
            AgendaMarittimo.create(agenda_vals)


class TemplateEsame(models.Model):
    _name = 'ey_corsi.template_esame'
    _description = 'Template esame'

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(string='Nome esame', required=True, index=True)
    prezzo_interni = fields.Float(string='Prezzo per interni da listino')
    prezzo_esterni = fields.Float(string='Prezzo per esterni da listino')

    logo_azienda = fields.Binary(string='Logo azienda', attachment=True)
    logo_ente = fields.Binary(string='Logo ente', attachment=True)

    max_iscritti = fields.Integer(string='Numero massimo iscrizioni', required=True, index=True)
    min_iscritti = fields.Integer(string='Numero minimo di iscritti')

    certificato_esame = fields.Binary(
        string='Template certificato esame (odt)', attachment=True, required=True)
    ce_fname = fields.Char(string='Nome file certificato')
    registration_form = fields.Binary(
        string='Template esame registration form (odt)', attachment=True, required=True)
    rf_fname = fields.Char(string='Nome file registration form')
    numero_certificato_esame = fields.Integer(string='Numero ultimo certificato', required=True, index=True)

    documento_tpl_ids = fields.One2many('ey_corsi.documento_tpl_esame', 'tpl_id', string='Documenti')
    chiave_ids = fields.One2many('ey_corsi.chiave_tpl_esame', 'tpl_id', string='Chiavi')

    costo_ids = fields.One2many('ey_corsi.costo_esame', 'template_esame_id', string='Costi')
    documento_ids = fields.One2many('ey_corsi.documento_esame', 'template_id', string='Documenti esame')

    _name_unique = models.Constraint('UNIQUE(name)', 'Nome già utilizzato!')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        return super().create(vals_list)

    def unlink(self):
        # STEP 8: impedire la cancellazione se esistono esami collegati al template
        return super().unlink()

    def copy(self, default=None):
        raise ValidationError('Impossibile duplicare un template esame (problemi di integrità)')
