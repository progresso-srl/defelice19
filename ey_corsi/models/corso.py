# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command
from odoo.exceptions import ValidationError
from datetime import datetime


class CostoCorso(models.Model):
    _name = 'ey_corsi.costo_corso'
    _description = 'Costo corso'

    tipo_costo = fields.Selection(
        [('unitario', 'Unitario'), ('totale', 'Totale')], string='Tipo di prezzo',
        default='totale', required=True, index=True,
    )
    importo = fields.Float(string='Importo in euro')
    template_corso_id = fields.Many2one('ey_corsi.template_corso', index=True)
    corso_id = fields.Many2one('ey_corsi.corso', index=True)
    descrizione_id = fields.Many2one(
        'ey_corsi.descrizione_costo', string='Descrizione', required=True, index=True)


class DocumentoCorso(models.Model):
    _name = 'ey_corsi.documento_corso'
    _description = 'Documento corso'
    _order = 'tipo_id'

    tipo_id = fields.Many2one('ey_corsi.tipo_documento_corso', string='Tipo', required=True)
    template_id = fields.Many2one('ey_corsi.template_corso', index=True)
    corso_id = fields.Many2one('ey_corsi.corso', index=True)
    document = fields.Binary(string='Documento', attachment=True, help='Formato pdf')
    document_fname = fields.Char(string='Nome file')


class PersonaleCorso(models.Model):
    _name = 'ey_corsi.personale_corso'
    _description = 'Personale assegnato al corso'

    docente_id = fields.Many2one(
        'res.partner', string='Personale', required=True, index=True,
        domain=[('personale_ey', '=', True)],
        context={'default_anagrafica_ey': False, 'default_personale_ey': True},
    )
    corso_id = fields.Many2one('ey_corsi.corso', index=True)
    category_id = fields.Many2one('res.partner.category', string='Ruolo', required=True, index=True)


class Corso(models.Model):
    _name = 'ey_corsi.corso'
    _description = 'Corso'
    _order = 'data_inizio desc'

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    codice_unico = fields.Char(string='Codice edizione', index=True)
    prefisso = fields.Char(string='Prefisso', index=True)
    nr_approvazione = fields.Char(string='Numero approvazione')
    prezzo_corso = fields.Float(string='Prezzo corso', index=True)
    data_inizio = fields.Date(string='Inizio', required=True, index=True)
    data_fine = fields.Date(string='Fine', required=True, index=True)
    max_iscritti = fields.Integer(
        string='Numero massimo iscrizioni', related='template_id.max_iscritti', store=True, index=True)
    totale_ricavi = fields.Float(string='Totale ricavi', compute='_compute_totale_ricavi', store=True)
    totale_costi = fields.Float(string='Totale costi', compute='_compute_totale_costi', store=True)
    computed = fields.Boolean(
        string='Corso validato',
        help="Impostato a vero quando il corso ha rilasciato i certificati a chi l'ha superato")
    annullato = fields.Boolean(string='Corso annullato', index=True)
    note = fields.Text(string='Note')
    logo_azienda = fields.Binary(related='template_id.logo_azienda', string='Logo azienda')
    logo_ente = fields.Binary(related='template_id.logo_ente', string='Logo ente')

    template_id = fields.Many2one('ey_corsi.template_corso', string='Template corso', required=True, index=True)
    ente_corsi_id = fields.Many2one('ey_corsi.ente_corsi', string='Ente')
    product_id = fields.Many2one('product.product', string='Prodotto collegato', index=True)
    invoice_id = fields.Many2one('account.move', string='Fattura fornitore', index=True)

    iscrizione_ids = fields.One2many('ey_corsi.iscrizione', 'corso_id', string='Iscrizioni')
    prospetto_corso = fields.One2many('ey_corsi.iscrizione', 'corso_id', string='Prospetto corso')
    personale = fields.One2many('ey_corsi.personale_corso', 'corso_id', string='Personale')
    costi = fields.One2many('ey_corsi.costo_corso', 'corso_id', string='Costi')
    documento_ids = fields.One2many('ey_corsi.documento_corso', 'corso_id', string='Documenti corso')
    chiave_ids = fields.One2many('ey_corsi.chiave_corso', 'corso_id', string='Chiavi')

    # campi per sito (dati soltanto: la pubblicazione sul sito non è in scope di questa migrazione)
    pubblicato = fields.Boolean(string='Pubblicato sul sito', index=True)
    sede_id = fields.Many2one('ey_corsi.sede_corso', string='Sede', index=True)

    def button_compute_corso(self):
        for corso in self:
            if corso.data_fine > fields.Date.today():
                raise ValidationError('Corso non ancora terminato')
            for iscrizione in corso.iscrizione_ids:
                self.env['ey_corsi.wiz_iscritti_corso'].create(
                    {'marittimo_id': iscrizione.marittimo_id.id, 'corso_id': corso.id})
            corso.computed = True
            domain_wiz = [
                ('corso_id', '=', corso.id),
                ('create_uid', '=', self.env.uid),
            ]
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ey_corsi.wiz_iscritti_corso',
                'view_mode': 'list',
                'domain': domain_wiz,
            }

    @api.depends('prezzo_corso', 'iscrizione_ids', 'iscrizione_ids.importo_versato')
    def _compute_totale_ricavi(self):
        for corso in self:
            corso.totale_ricavi = sum(corso.iscrizione_ids.mapped('importo_versato'))

    @api.depends('costi', 'costi.importo', 'costi.tipo_costo', 'iscrizione_ids')
    def _compute_totale_costi(self):
        for corso in self:
            numero_iscritti = len(corso.iscrizione_ids)
            tot_costi = 0.0
            for costo in corso.costi:
                if costo.tipo_costo == 'unitario':
                    tot_costi += costo.importo * numero_iscritti
                else:
                    tot_costi += costo.importo
            corso.totale_costi = tot_costi

    @api.depends('template_id', 'template_id.name', 'data_inizio', 'data_fine')
    def _compute_name(self):
        for corso in self:
            name = corso.template_id.name or ''
            if corso.data_inizio:
                name += ' ' + corso.data_inizio.strftime('%d/%m/%Y')
            if corso.data_fine:
                name += ' - ' + corso.data_fine.strftime('%d/%m/%Y')
            name += f' [{corso.id}]'
            corso.name = name

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.prefisso = self.template_id.prefisso
            self.nr_approvazione = self.template_id.nr_approvazione
            self.ente_corsi_id = self.template_id.ente_corsi_id
            self.prezzo_corso = self.template_id.prezzo_corso

    @api.constrains('data_inizio', 'data_fine')
    def _check_date(self):
        for corso in self:
            if corso.data_inizio and corso.data_fine and corso.data_inizio > corso.data_fine:
                raise ValidationError('Date invertite')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        corsi = super().create(vals_list)
        for corso in corsi:
            # creo il prodotto collegato (per la fatturazione)
            prodotto = self.env['product.product'].create({
                'name': corso.name,
                'type': 'service',
            })
            corso.product_id = prodotto.id

            # copio i costi dal template
            for costo in corso.template_id.costo_ids:
                self.env['ey_corsi.costo_corso'].create({
                    'corso_id': corso.id,
                    'descrizione_id': costo.descrizione_id.id,
                    'tipo_costo': costo.tipo_costo,
                    'importo': costo.importo,
                })

            # copio i documenti dal template
            for doc in corso.template_id.documento_ids:
                self.env['ey_corsi.documento_corso'].create({
                    'corso_id': corso.id,
                    'document_fname': doc.document_fname,
                    'document': doc.document,
                    'tipo_id': doc.tipo_id.id,
                })

            corso._genera_chiavi_da_template()
        return corsi

    def _genera_chiavi_da_template(self):
        """Risolve le chiavi definite sul template (campo puntato o valore fisso)
        e crea le righe ey_corsi.chiave_corso corrispondenti sul corso."""
        self.ensure_one()
        ChiaveCorso = self.env['ey_corsi.chiave_corso']
        for chiave_tpl in self.template_id.chiave_ids:
            key = chiave_tpl.chiave
            if chiave_tpl.tipo_chiave == 'campo':
                value = ''
                is_valore = False
                obj = self
                try:
                    arr_value = key.split('.')
                    for i, campo in enumerate(arr_value):
                        current_value = getattr(obj, campo)
                        if i != len(arr_value) - 1:
                            obj = current_value
                        else:
                            current_model = self.env[obj._name]
                            current_field = current_model._fields.get(campo)
                            if current_field:
                                tcf = current_field.type
                                if tcf in ('char', 'text'):
                                    value = current_value
                                elif tcf in ('float', 'integer'):
                                    value = str(current_value) if current_value is not None else ''
                                elif tcf == 'boolean':
                                    value = 'Sì' if current_value else 'No'
                                elif tcf == 'selection':
                                    value = dict(obj._fields[campo].selection).get(current_value) or ''
                                elif tcf == 'date':
                                    value = current_value.strftime('%d-%m-%Y') if current_value else ''
                                elif tcf == 'datetime':
                                    value = current_value.strftime('%d-%m-%Y %H:%M:%S') if current_value else ''
                                elif tcf == 'monetary':
                                    value = str(current_value) if current_value is not None else ''
                                else:
                                    value = ''
                            else:
                                value = ''
                except Exception:
                    value = ''
            else:
                is_valore = True
                value = chiave_tpl.valore
            ChiaveCorso.create({
                'corso_id': self.id,
                'chiave': key,
                'descrizione': chiave_tpl.descrizione,
                'valore': value,
                'is_valore': is_valore,
                'priority': chiave_tpl.priority,
            })

    def genera_fattura(self):
        """Genera la fattura fornitore (spese corso) verso 'Fornitore Unico'."""
        fornitore = self.env['res.partner'].search([('name', '=', 'Fornitore Unico')], limit=1)
        for corso in self:
            move = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': fornitore.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [Command.create({
                    'product_id': corso.product_id.id,
                    'name': f'Spese per corso {corso.name}',
                    'price_unit': corso.totale_costi,
                    'quantity': 1,
                })],
            })
            corso.invoice_id = move.id


class ChiaveCorso(models.Model):
    _name = 'ey_corsi.chiave_corso'
    _description = 'Chiave corso'
    _order = 'priority asc'

    corso_id = fields.Many2one('ey_corsi.corso', index=True)
    chiave = fields.Char(string='Chiave', required=True, index=True)
    descrizione = fields.Char(string='Descrizione')
    tipo_chiave = fields.Selection(
        [('valore', 'Valore'), ('campo', 'Campo')], string='Tipo', default='campo', required=True, index=True)
    valore = fields.Char(string='Valore')
    is_valore = fields.Boolean(index=True)
    priority = fields.Integer(string='Priorità', default=0, index=True)


class Iscrizione(models.Model):
    _name = 'ey_corsi.iscrizione'
    _description = 'Iscrizione a corso'
    _order = 'data_iscrizione desc'

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    data_iscrizione = fields.Date(string='Data iscrizione', index=True, default=fields.Date.today)
    importo_versato = fields.Float(string='Importo fatturato', compute='_compute_importo_fatturato', store=True)
    pagato = fields.Boolean(string='Saldato', index=True)
    prezzo_corso = fields.Float(string='Prezzo totale corso')
    prezzo_scontato = fields.Boolean(string='Scontato', index=True)
    data_inizio_corso = fields.Date(
        string='Inizio corso', related='corso_id.data_inizio', store=True, index=True)
    data_fine_corso = fields.Date(
        string='Fine corso', related='corso_id.data_fine', store=True, index=True)
    data_nascita_marittimo = fields.Date(
        string='Data di nascita', related='marittimo_id.data_nascita', store=True)
    corso_superato = fields.Boolean(
        string='Corso frequentato', index=True,
        help='Raggiunto almeno il 90% delle frequenze',
        readonly=False,
    )
    materiale_consegnato = fields.Boolean(string='Materiale consegnato', index=True)
    preavvertito = fields.Boolean(string='Preavvertito', index=True)
    attestato_frequenza_consegnato = fields.Boolean(string='Attestato frequenza consegnato', index=True)
    pagamento_acconto = fields.Boolean(string='Pagamento acconto', index=True)
    note = fields.Text(string='Note')

    marittimo_id = fields.Many2one(
        'res.partner', string='Corsista', required=True, index=True,
        domain=['|', ('anagrafica_ey', '=', True), '|',
                ('personale_ey', '=', True), ('armatore_proprietario', '=', True)],
    )
    destinatario_id = fields.Many2one(
        'res.partner', string='Destinatario fatture', index=True,
        help='Inserire se il destinatario delle fatture non è il marittimo iscritto')
    corso_id = fields.Many2one('ey_corsi.corso', string='Corso', required=True, index=True)
    luogo_nascita_marittimo_id = fields.Many2one(
        'ey_corsi.luogo_nascita', string='Luogo di nascita',
        related='marittimo_id.luogo_nascita_id', store=True)
    nazionalita_marittimo_id = fields.Many2one(
        'res.country', string='Cittadinanza',
        related='marittimo_id.nazionalita_id', store=True, index=True)

    invoice_ids = fields.One2many('account.move', 'iscrizione_id', string='Fatture')
    documento_ids = fields.One2many(related='marittimo_id.documento_ids', string='Documenti marittimo')
    esame_id = fields.Many2one('ey_corsi.esame', string='Esame a cui iscriversi', index=True)
    iscrizione_a_esame = fields.Boolean(
        string='Iscritto a esame', compute='_compute_iscrizione_a_esame', index=True)

    @api.depends('invoice_ids', 'invoice_ids.amount_total')
    def _compute_importo_fatturato(self):
        for iscrizione in self:
            iscrizione.importo_versato = sum(iscrizione.invoice_ids.mapped('amount_total'))

    @api.depends('corso_id', 'marittimo_id')
    def _compute_name(self):
        for iscrizione in self:
            name = iscrizione.corso_id.name or ''
            if iscrizione.marittimo_id:
                name += ' - ' + iscrizione.marittimo_id.name
            iscrizione.name = name

    @api.depends('esame_id', 'esame_id.iscrizione_ids', 'esame_id.iscrizione_ids.marittimo_id')
    def _compute_iscrizione_a_esame(self):
        for iscrizione in self:
            iscrizione.iscrizione_a_esame = bool(iscrizione.esame_id) and any(
                ie.marittimo_id.id == iscrizione.marittimo_id.id
                for ie in iscrizione.esame_id.iscrizione_ids
            )

    @api.onchange('corso_id')
    def _onchange_corso_id(self):
        if self.corso_id:
            self.prezzo_corso = self.corso_id.prezzo_corso
            template_esame = self.corso_id.template_id.template_esame_id
            esami = self.env['ey_corsi.esame'].search([
                ('template_id', '=', template_esame.id),
                ('data_esame', '>=', fields.Date.today()),
            ])
            return {'domain': {'esame_id': [('id', 'in', esami.ids)]}}
        return {'domain': {'esame_id': [('id', 'in', [])]}}

    @api.onchange('marittimo_id')
    def _onchange_marittimo_id(self):
        if self.marittimo_id and self.marittimo_id.blacklist:
            raise ValidationError('Errore di inserimento. Contattare amministratore')

    @api.constrains('marittimo_id', 'corso_id')
    def _check_iscrizione_unica(self):
        for iscrizione in self:
            if iscrizione.marittimo_id and iscrizione.corso_id:
                altre = self.env['ey_corsi.iscrizione'].search([
                    ('marittimo_id', '=', iscrizione.marittimo_id.id),
                    ('corso_id', '=', iscrizione.corso_id.id),
                    ('id', '!=', iscrizione.id),
                ])
                if altre:
                    raise ValidationError('Marittimo già iscritto a quel corso')
            if iscrizione.corso_id and len(iscrizione.corso_id.iscrizione_ids) > iscrizione.corso_id.max_iscritti:
                raise ValidationError('Il corso ha raggiunto il numero massimo di iscritti')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        iscrizioni = super().create(vals_list)
        for iscrizione in iscrizioni:
            if iscrizione.esame_id:
                self.env['ey_corsi.iscrizione_esame'].create({
                    'data_iscrizione': iscrizione.data_iscrizione,
                    'marittimo_id': iscrizione.marittimo_id.id,
                    'destinatario_id': iscrizione.destinatario_id.id,
                    'esame_id': iscrizione.esame_id.id,
                    'tipo_iscritto': 'interno',
                    'prezzo_esame': iscrizione.esame_id.prezzo_interni,
                    'corso_collegato_id': iscrizione.corso_id.id,
                })
        return iscrizioni

    def genera_fattura(self):
        """Genera la fattura cliente per l'iscrizione al corso."""
        moves = self.env['account.move']
        for iscrizione in self:
            prodotto = iscrizione.corso_id.product_id
            partner = iscrizione.destinatario_id or iscrizione.marittimo_id
            move = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.today(),
                'iscrizione_id': iscrizione.id,
                'invoice_line_ids': [Command.create({
                    'product_id': prodotto.id,
                    'name': f'{iscrizione.marittimo_id.name} - {iscrizione.corso_id.name}',
                    'price_unit': 1,
                    'quantity': 1,
                    'tax_ids': [Command.set(prodotto.taxes_id.ids)],
                })],
            })
            moves |= move
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': moves[:1].id,
            'target': 'current',
        }


class PreIscrizione(models.Model):
    _name = 'ey_corsi.pre_iscrizione'
    _description = 'Pre-iscrizione a corso'
    _order = 'esito asc'

    _ESITI = [
        ('in_attesa', 'In attesa'),
        ('iscritto', 'Iscritto'),
        ('annullata', 'Annullata'),
    ]

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    marittimo_id = fields.Many2one(
        'res.partner', string='Corsista', required=True, index=True,
        domain=['|', ('anagrafica_ey', '=', True), '|',
                ('personale_ey', '=', True), ('armatore_proprietario', '=', True)],
    )
    destinatario_id = fields.Many2one(
        'res.partner', string='Destinatario fatture', index=True,
        help='Inserire se il destinatario delle fatture non è il marittimo iscritto')
    template_id = fields.Many2one('ey_corsi.template_corso', string='Template corso', required=True, index=True)
    corso_id = fields.Many2one('ey_corsi.corso', string='Corso', index=True)
    data_iscrizione = fields.Date(string='Data preiscrizione', index=True, default=fields.Date.today)
    data_inizio_corso = fields.Date(string='Inizio corso', related='corso_id.data_inizio', store=True, index=True)
    data_fine_corso = fields.Date(string='Fine corso', related='corso_id.data_fine', store=True, index=True)
    prezzo_corso = fields.Float(string='Prezzo totale corso')
    prezzo_scontato = fields.Boolean(string='Scontato', index=True)
    documento_ids = fields.One2many(related='marittimo_id.documento_ids', string='Documenti marittimo')
    iscrizione_id = fields.Many2one('ey_corsi.iscrizione', string='Iscrizione collegata', index=True)
    esito = fields.Selection(_ESITI, string='Esito', required=True, default='in_attesa', index=True)
    note_esito = fields.Text(string='Note esito')
    esame_id = fields.Many2one('ey_corsi.esame', string='Esame a cui iscriversi', index=True)

    @api.depends('corso_id', 'marittimo_id')
    def _compute_name(self):
        for pre in self:
            name = '*** PREISCRIZIONE *** ' + (pre.corso_id.name or '')
            if pre.marittimo_id:
                name += ' - ' + pre.marittimo_id.name
            pre.name = name

    @api.onchange('corso_id')
    def _onchange_corso_id(self):
        if self.corso_id:
            self.prezzo_corso = self.corso_id.prezzo_corso
            template_esame = self.corso_id.template_id.template_esame_id
            esami = self.env['ey_corsi.esame'].search([
                ('template_id', '=', template_esame.id),
                ('data_esame', '>=', fields.Date.today()),
            ])
            return {'domain': {'esame_id': [('id', 'in', esami.ids)]}}
        return {'domain': {'esame_id': [('id', 'in', [])]}}

    @api.onchange('marittimo_id')
    def _onchange_marittimo_id(self):
        if self.marittimo_id and self.marittimo_id.blacklist:
            raise ValidationError('Errore di inserimento. Contattare amministratore')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            return {'domain': {
                'corso_id': [
                    ('template_id', '=', self.template_id.id),
                    ('data_inizio', '>=', fields.Date.today()),
                    ('computed', '=', False),
                ],
            }}

    @api.constrains('marittimo_id', 'corso_id')
    def _check_preiscrizione_unica(self):
        for pre in self:
            if pre.marittimo_id and pre.corso_id:
                altre = self.env['ey_corsi.pre_iscrizione'].search([
                    ('marittimo_id', '=', pre.marittimo_id.id),
                    ('corso_id', '=', pre.corso_id.id),
                    ('id', '!=', pre.id),
                ])
                if altre:
                    raise ValidationError('Marittimo già preiscritto a quel corso')
            if pre.corso_id and len(pre.corso_id.iscrizione_ids) > pre.corso_id.max_iscritti:
                raise ValidationError('Il corso ha raggiunto il numero massimo di iscritti')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        return super().create(vals_list)

    def crea_iscrizione(self):
        self.ensure_one()
        iscrizione = self.env['ey_corsi.iscrizione'].create({
            'corso_id': self.corso_id.id,
            'marittimo_id': self.marittimo_id.id,
            'destinatario_id': self.destinatario_id.id,
            'data_iscrizione': self.data_iscrizione,
            'prezzo_scontato': self.prezzo_scontato,
            'prezzo_corso': self.prezzo_corso,
            'esame_id': self.esame_id.id,
        })
        self.write({'iscrizione_id': iscrizione.id, 'esito': 'iscritto'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey_corsi.iscrizione',
            'view_mode': 'form',
            'res_id': iscrizione.id,
            'target': 'current',
        }


class AttestatoFrequenza(models.Model):
    _name = 'ey_corsi.attestato_frequenza'
    _description = 'Attestato di frequenza'

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    numero_sequenza = fields.Integer(string='Numero sequenza', index=True)
    data_rilascio = fields.Date(string='Data rilascio', required=True, index=True, default=fields.Date.today)
    data_scadenza = fields.Date(string='Data scadenza', required=True, index=True)
    document = fields.Binary(string='Documento', attachment=True)
    document_fname = fields.Char(string='Nome file')
    scaduto = fields.Boolean(compute='_compute_scaduto', index=True)

    marittimo_id = fields.Many2one('res.partner', string='Marittimo', domain=[('anagrafica_ey', '=', True)], index=True)
    corso_id = fields.Many2one('ey_corsi.corso', string='Corso', index=True)

    def button_stampa_duplicato(self):
        return self.env.ref('ey_corsi.action_report_attestato_frequenza').report_action(self)

    @api.depends('corso_id', 'marittimo_id', 'numero_sequenza')
    def _compute_name(self):
        for af in self:
            name = ''
            if af.corso_id:
                name += af.corso_id.name + ' - '
            if af.marittimo_id:
                name += af.marittimo_id.name + ' - '
            name += str(af.numero_sequenza)
            af.name = name

    @api.depends('data_scadenza')
    def _compute_scaduto(self):
        for af in self:
            af.scaduto = bool(af.data_scadenza) and datetime.today().date() > af.data_scadenza

    @api.constrains('data_rilascio', 'data_scadenza')
    def _check_date(self):
        for af in self:
            if af.data_rilascio and af.data_scadenza and af.data_rilascio > af.data_scadenza:
                raise ValidationError('La data di scadenza deve essere successiva a quella di emissione')
