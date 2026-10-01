# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command
from odoo.exceptions import ValidationError
from datetime import datetime


class CostoEsame(models.Model):
    _name = 'ey_corsi.costo_esame'
    _description = 'Costo esame'

    tipo_costo = fields.Selection(
        [('unitario', 'Unitario'), ('totale', 'Totale')], string='Tipo di prezzo', required=True, index=True)
    importo = fields.Float(string='Importo in euro')
    template_esame_id = fields.Many2one('ey_corsi.template_esame', index=True)
    esame_id = fields.Many2one('ey_corsi.esame', index=True)
    descrizione_id = fields.Many2one(
        'ey_corsi.descrizione_costo', string='Descrizione', required=True, index=True)


class DocumentoEsame(models.Model):
    _name = 'ey_corsi.documento_esame'
    _description = 'Documento esame'
    _order = 'tipo_id'

    tipo_id = fields.Many2one('ey_corsi.tipo_documento_esame', string='Tipo', required=True)
    template_id = fields.Many2one('ey_corsi.template_esame', index=True)
    esame_id = fields.Many2one('ey_corsi.esame', index=True)
    document = fields.Binary(string='Documento', attachment=True, help='Formato pdf')
    document_fname = fields.Char(string='Nome file')


class PersonaleEsame(models.Model):
    _name = 'ey_corsi.personale_esame'
    _description = 'Personale assegnato all\'esame'

    docente_id = fields.Many2one(
        'res.partner', string='Personale', required=True, index=True,
        domain=[('personale_ey', '=', True)],
        context={'default_anagrafica_ey': False, 'default_personale_ey': True},
    )
    esame_id = fields.Many2one('ey_corsi.esame', index=True)
    category_id = fields.Many2one('res.partner.category', string='Ruolo', required=True, index=True)


class Esame(models.Model):
    _name = 'ey_corsi.esame'
    _description = 'Esame'
    _order = 'data_esame desc'

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    data_esame = fields.Date(string='Data', required=True, index=True)
    max_iscritti = fields.Integer(
        string='Numero massimo iscrizioni', related='template_id.max_iscritti', store=True, index=True)
    prezzo_interni = fields.Float(string='Prezzo per interni', index=True)
    prezzo_esterni = fields.Float(string='Prezzo per esterni', index=True)
    totale_ricavi = fields.Float(string='Totale ricavi', compute='_compute_totale_ricavi', store=True)
    totale_costi = fields.Float(string='Totale costi', compute='_compute_totale_costi', store=True)
    computed = fields.Boolean(
        string='Esame validato',
        help="Impostato a vero quando l'esame ha rilasciato il certificato a chi l'ha superato")
    annullato = fields.Boolean(string='Esame annullato', index=True)
    note = fields.Text(string='Note')
    logo_azienda = fields.Binary(related='template_id.logo_azienda', string='Logo azienda')
    logo_ente = fields.Binary(related='template_id.logo_ente', string='Logo ente')

    template_id = fields.Many2one('ey_corsi.template_esame', string='Template esame', required=True, index=True)
    product_id = fields.Many2one('product.product', string='Prodotto collegato', index=True)
    invoice_id = fields.Many2one('account.move', string='Fattura fornitore', index=True)
    promossi_bocciati = fields.Binary(string='Riepilogo promossi / bocciati (pdf)', attachment=True)
    pb_fname = fields.Char(string='Nome file')

    personale = fields.One2many('ey_corsi.personale_esame', 'esame_id', string='Personale')
    costi = fields.One2many('ey_corsi.costo_esame', 'esame_id', string='Costi')
    iscrizione_ids = fields.One2many('ey_corsi.iscrizione_esame', 'esame_id', string='Iscrizioni')
    prospetto_esame = fields.One2many('ey_corsi.iscrizione_esame', 'esame_id', string='Prospetto esame')
    documento_ids = fields.One2many('ey_corsi.documento_esame', 'esame_id', string='Documenti esame')
    chiave_ids = fields.One2many('ey_corsi.chiave_esame', 'esame_id', string='Chiavi')

    def button_compute_esame(self):
        for esame in self:
            if esame.data_esame > fields.Date.today():
                raise ValidationError('Esame futuro')
            for iscrizione in esame.iscrizione_ids:
                self.env['ey_corsi.wiz_iscritti_esame'].create(
                    {'marittimo_id': iscrizione.marittimo_id.id, 'esame_id': esame.id})
            esame.computed = True
            domain_wiz = [
                ('esame_id', '=', esame.id),
                ('create_uid', '=', self.env.uid),
            ]
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ey_corsi.wiz_iscritti_esame',
                'view_mode': 'list',
                'domain': domain_wiz,
            }

    @api.depends('iscrizione_ids', 'iscrizione_ids.importo_versato')
    def _compute_totale_ricavi(self):
        for esame in self:
            esame.totale_ricavi = sum(esame.iscrizione_ids.mapped('importo_versato'))

    @api.depends('costi', 'costi.importo', 'costi.tipo_costo', 'iscrizione_ids')
    def _compute_totale_costi(self):
        for esame in self:
            numero_iscritti = len(esame.iscrizione_ids)
            tot_costi = 0.0
            for costo in esame.costi:
                if costo.tipo_costo == 'unitario':
                    tot_costi += costo.importo * numero_iscritti
                else:
                    tot_costi += costo.importo
            esame.totale_costi = tot_costi

    @api.depends('template_id', 'template_id.name', 'data_esame')
    def _compute_name(self):
        for esame in self:
            name = esame.template_id.name or ''
            if esame.data_esame:
                name += ' ' + esame.data_esame.strftime('%d/%m/%Y')
            name += f' [{esame.id}]'
            esame.name = name

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.max_iscritti = self.template_id.max_iscritti
            self.prezzo_interni = self.template_id.prezzo_interni
            self.prezzo_esterni = self.template_id.prezzo_esterni

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        esami = super().create(vals_list)
        for esame in esami:
            prodotto = self.env['product.product'].create({
                'name': esame.name,
                'type': 'service',
            })
            esame.product_id = prodotto.id

            for costo in esame.template_id.costo_ids:
                self.env['ey_corsi.costo_esame'].create({
                    'esame_id': esame.id,
                    'descrizione_id': costo.descrizione_id.id,
                    'tipo_costo': costo.tipo_costo,
                    'importo': costo.importo,
                })

            for doc in esame.template_id.documento_ids:
                self.env['ey_corsi.documento_esame'].create({
                    'esame_id': esame.id,
                    'document_fname': doc.document_fname,
                    'document': doc.document,
                    'tipo_id': doc.tipo_id.id,
                })

            esame._genera_chiavi_da_template()
        return esami

    def _genera_chiavi_da_template(self):
        """Risolve le chiavi definite sul template (campo puntato o valore fisso)
        e crea le righe ey_corsi.chiave_esame corrispondenti sull'esame."""
        self.ensure_one()
        ChiaveEsame = self.env['ey_corsi.chiave_esame']
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
            ChiaveEsame.create({
                'esame_id': self.id,
                'chiave': key,
                'descrizione': chiave_tpl.descrizione,
                'valore': value,
                'is_valore': is_valore,
                'priority': chiave_tpl.priority,
            })

    def genera_fattura(self):
        """Genera la fattura fornitore (spese esame) verso 'Fornitore Unico'."""
        fornitore = self.env['res.partner'].search([('name', '=', 'Fornitore Unico')], limit=1)
        for esame in self:
            move = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': fornitore.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [Command.create({
                    'product_id': esame.product_id.id,
                    'name': f'Spese per esame {esame.name}',
                    'price_unit': esame.totale_costi,
                    'quantity': 1,
                })],
            })
            esame.invoice_id = move.id


class ChiaveEsame(models.Model):
    _name = 'ey_corsi.chiave_esame'
    _description = 'Chiave esame'
    _order = 'priority asc'

    esame_id = fields.Many2one('ey_corsi.esame', index=True)
    chiave = fields.Char(string='Chiave', required=True, index=True)
    descrizione = fields.Char(string='Descrizione')
    tipo_chiave = fields.Selection(
        [('valore', 'Valore'), ('campo', 'Campo')], string='Tipo', default='campo', required=True, index=True)
    valore = fields.Char(string='Valore')
    is_valore = fields.Boolean(index=True)
    priority = fields.Integer(string='Priorità', default=0, index=True)


class IscrizioneEsame(models.Model):
    _name = 'ey_corsi.iscrizione_esame'
    _description = 'Iscrizione a esame'
    _order = 'data_iscrizione desc'

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    data_iscrizione = fields.Date(string='Data iscrizione', index=True, default=fields.Date.today)
    tipo_iscritto = fields.Selection(
        [('interno', 'Interno'), ('esterno', 'Esterno')], string='Tipo iscritto', default='esterno', index=True)
    importo_versato = fields.Float(string='Importo fatturato', compute='_compute_importo_fatturato', store=True)
    pagato = fields.Boolean(string='Saldato', index=True)
    prezzo_esame = fields.Float(string='Costo iscrizione')
    prezzo_scontato = fields.Boolean(string='Scontato', index=True)
    data_nascita_marittimo = fields.Date(
        string='Data di nascita', related='marittimo_id.data_nascita', store=True)
    esame_superato = fields.Boolean(string='Esame superato', index=True)
    avvertito_esito = fields.Boolean(string="Avvertito dell'esito", index=True)
    richiesta_ritiro = fields.Boolean(string='Richiesta ritiro', index=True)
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
    esame_id = fields.Many2one('ey_corsi.esame', string='Esame', required=True, index=True)
    luogo_nascita_marittimo_id = fields.Many2one(
        'ey_corsi.luogo_nascita', string='Luogo di nascita',
        related='marittimo_id.luogo_nascita_id', store=True)
    nazionalita_marittimo_id = fields.Many2one(
        'res.country', string='Cittadinanza',
        related='marittimo_id.nazionalita_id', store=True, index=True)
    corso_collegato_id = fields.Many2one('ey_corsi.corso', string='Iscrizione corso', index=True)

    invoice_ids = fields.One2many('account.move', 'iscrizione_esame_id', string='Fatture')
    documento_ids = fields.One2many(related='marittimo_id.documento_ids', string='Documenti marittimo')

    @api.depends('invoice_ids', 'invoice_ids.amount_total')
    def _compute_importo_fatturato(self):
        for iscrizione in self:
            iscrizione.importo_versato = sum(iscrizione.invoice_ids.mapped('amount_total'))

    @api.depends('esame_id', 'marittimo_id')
    def _compute_name(self):
        for iscrizione in self:
            name = iscrizione.esame_id.name or ''
            if iscrizione.marittimo_id:
                name += ' - ' + iscrizione.marittimo_id.name
            iscrizione.name = name

    @api.onchange('esame_id', 'tipo_iscritto')
    def _onchange_prezzo(self):
        if self.esame_id:
            if self.tipo_iscritto == 'interno':
                self.prezzo_esame = self.esame_id.prezzo_interni
            else:
                self.prezzo_esame = self.esame_id.prezzo_esterni

    @api.onchange('marittimo_id')
    def _onchange_marittimo_id(self):
        if self.marittimo_id and self.marittimo_id.blacklist:
            raise ValidationError('Errore di inserimento. Contattare amministratore')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        return super().create(vals_list)

    def genera_fattura(self):
        """Genera la fattura cliente per l'iscrizione all'esame."""
        moves = self.env['account.move']
        for iscrizione in self:
            prodotto = iscrizione.esame_id.product_id
            partner = iscrizione.destinatario_id or iscrizione.marittimo_id
            move = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.today(),
                'iscrizione_esame_id': iscrizione.id,
                'invoice_line_ids': [Command.create({
                    'product_id': prodotto.id,
                    'name': f'{iscrizione.marittimo_id.name} - {iscrizione.esame_id.name}',
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


class PreIscrizioneEsame(models.Model):
    _name = 'ey_corsi.pre_iscrizione_esame'
    _description = 'Pre-iscrizione a esame'
    _order = 'esito asc'

    _ESITI = [
        ('in_attesa', 'In attesa'),
        ('iscritto', 'Iscritto'),
        ('annullata', 'Annullata'),
    ]

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    template_id = fields.Many2one('ey_corsi.template_esame', string='Template esame', required=True, index=True)
    marittimo_id = fields.Many2one(
        'res.partner', string='Corsista', required=True, index=True,
        domain=['|', ('anagrafica_ey', '=', True), '|',
                ('personale_ey', '=', True), ('armatore_proprietario', '=', True)],
    )
    destinatario_id = fields.Many2one(
        'res.partner', string='Destinatario fatture', index=True,
        help='Inserire se il destinatario delle fatture non è il marittimo iscritto')
    tipo_iscritto = fields.Selection(
        [('interno', 'Interno'), ('esterno', 'Esterno')], string='Tipo iscritto', default='esterno', index=True)
    esame_id = fields.Many2one('ey_corsi.esame', string='Esame', index=True)
    data_iscrizione = fields.Date(string='Data iscrizione', index=True, default=fields.Date.today)
    prezzo_esame = fields.Float(string='Costo iscrizione')
    prezzo_scontato = fields.Boolean(string='Scontato', index=True)
    documento_ids = fields.One2many(related='marittimo_id.documento_ids', string='Documenti marittimo')
    iscrizione_id = fields.Many2one('ey_corsi.iscrizione_esame', string='Iscrizione collegata', index=True)
    esito = fields.Selection(_ESITI, string='Esito', required=True, default='in_attesa', index=True)
    note_esito = fields.Text(string='Note esito')

    @api.depends('esame_id', 'marittimo_id')
    def _compute_name(self):
        for pre in self:
            name = pre.esame_id.name or ''
            if pre.marittimo_id:
                name += ' - ' + pre.marittimo_id.name
            pre.name = name

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            return {'domain': {
                'esame_id': [
                    ('template_id', '=', self.template_id.id),
                    ('data_esame', '>=', fields.Date.today()),
                    ('computed', '=', False),
                ],
            }}

    @api.onchange('esame_id', 'tipo_iscritto')
    def _onchange_prezzo(self):
        if self.esame_id:
            if self.tipo_iscritto == 'interno':
                self.prezzo_esame = self.esame_id.prezzo_interni
            else:
                self.prezzo_esame = self.esame_id.prezzo_esterni

    @api.onchange('marittimo_id')
    def _onchange_marittimo_id(self):
        if self.marittimo_id and self.marittimo_id.blacklist:
            raise ValidationError('Errore di inserimento. Contattare amministratore')

    @api.constrains('marittimo_id', 'esame_id')
    def _check_preiscrizione_unica(self):
        for pre in self:
            if pre.marittimo_id and pre.esame_id:
                altre = self.env['ey_corsi.pre_iscrizione_esame'].search([
                    ('marittimo_id', '=', pre.marittimo_id.id),
                    ('esame_id', '=', pre.esame_id.id),
                    ('id', '!=', pre.id),
                ])
                if altre:
                    raise ValidationError("Marittimo già pre-iscritto a quell'esame")
            if pre.esame_id and len(pre.esame_id.iscrizione_ids) > pre.esame_id.max_iscritti:
                raise ValidationError("L'esame ha raggiunto il numero massimo di iscritti")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        return super().create(vals_list)

    def crea_iscrizione(self):
        self.ensure_one()
        iscrizione = self.env['ey_corsi.iscrizione_esame'].create({
            'marittimo_id': self.marittimo_id.id,
            'destinatario_id': self.destinatario_id.id,
            'data_iscrizione': self.data_iscrizione,
            'prezzo_scontato': self.prezzo_scontato,
            'prezzo_esame': self.prezzo_esame,
            'esame_id': self.esame_id.id,
            'tipo_iscritto': self.tipo_iscritto,
        })
        self.write({'iscrizione_id': iscrizione.id, 'esito': 'iscritto'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey_corsi.iscrizione_esame',
            'view_mode': 'form',
            'res_id': iscrizione.id,
            'target': 'current',
        }


class CertificatoEsame(models.Model):
    _name = 'ey_corsi.certificato_esame'
    _description = 'Certificato interno rilasciato dopo esame'

    created = fields.Boolean(string='Creato', index=True)
    name = fields.Char(compute='_compute_name', store=True, index=True)
    numero_sequenza = fields.Integer(string='Numero sequenza', index=True)
    data_rilascio = fields.Date(string='Data rilascio', required=True, index=True, default=fields.Date.today)
    data_scadenza = fields.Date(string='Data scadenza', index=True, required=True)
    document = fields.Binary(string='Documento', attachment=True)
    document_fname = fields.Char(string='Nome file')
    scaduto = fields.Boolean(compute='_compute_scaduto', index=True)

    esame_id = fields.Many2one('ey_corsi.esame', string='Esame', index=True)
    marittimo_id = fields.Many2one('res.partner', string='Marittimo', domain=[('anagrafica_ey', '=', True)], index=True)

    def button_stampa_duplicato(self):
        return self.env.ref('ey_corsi.action_report_certificato_esame').report_action(self)

    @api.depends('esame_id', 'marittimo_id', 'numero_sequenza')
    def _compute_name(self):
        for ce in self:
            name = ''
            if ce.esame_id:
                name += ce.esame_id.template_id.name + ' - '
            if ce.marittimo_id:
                name += ce.marittimo_id.name + ' - '
            name += str(ce.numero_sequenza)
            ce.name = name

    @api.depends('data_scadenza')
    def _compute_scaduto(self):
        for ce in self:
            ce.scaduto = bool(ce.data_scadenza) and datetime.today().date() > ce.data_scadenza

    @api.constrains('data_rilascio', 'data_scadenza')
    def _check_date(self):
        for ce in self:
            if ce.data_rilascio and ce.data_scadenza and ce.data_rilascio > ce.data_scadenza:
                raise ValidationError('La data di scadenza deve essere successiva a quella di emissione')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['created'] = True
        return super().create(vals_list)
