# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import time


class ContrattoNave(models.Model):
    _name = "ey_contabilita_navi.contratto_nave"

    _MESI = [
        ('01', 'Gennaio'),
        ('02', 'Febbraio'),
        ('03', 'Marzo'),
        ('04', 'Aprile'),
        ('05', 'Maggio'),
        ('06', 'Giugno'),
        ('07', 'Luglio'),
        ('08', 'Agosto'),
        ('09', 'Settembre'),
        ('10', 'Ottobre'),
        ('11', 'Novembre'),
        ('12', 'Dicembre')
    ]

    def button_mostra_preventivi_contratto(self):
        self.ensure_one()
        return {
                'name': 'Mostra preventivi',
                'type': 'ir.actions.act_window',
                'res_model': 'ey_contabilita_navi.previsionale_contratto',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('contratto_id', '=', self.id)],
            }

    def button_crea_prossimo_previsionale(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ey_contabilita_navi.wiz_crea_prossimo_previsionale',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_contratto_id': self.id}
            }

    @api.model
    def _get_selection_years(self):
        """
        Genera la lista di anni da passare al campo selection
        :return: list of tuples
        """
        current = datetime.today().year
        return [
            (str(current - 2), str(current - 2)),
            (str(current - 1), str(current - 1)),
            (str(current), str(current)),
            (str(current + 1), str(current + 1)),
            (str(current + 2), str(current + 2))
        ]

    @api.depends("previsionale_ids", "previsionale_ids.bilancio", "saldo_iniziale")
    def _compute_saldo(self):
        for rec in self:
            saldo = rec.saldo_iniziale
            for p in rec.previsionale_ids:
                saldo += p.bilancio
            rec.saldo_attuale = saldo

    @api.model
    def _default_currency(self):
        currency = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
        return currency.id

    name = fields.Char(string="Contratto", store=True)
    nome_contratto = fields.Char(string="Nome contratto", required=True)
    mese_inizio = fields.Selection(_MESI, string="Mese inizio", index=True, required=True)
    anno_inizio = fields.Selection(_get_selection_years, string="Anno inizio", index=True, required=True)
    attivo = fields.Boolean(string="Attivo", index=True, default=True)
    saldo_iniziale = fields.Float(string="Saldo iniziale")
    saldo_attuale = fields.Float(string="Saldo attuale", compute="_compute_saldo", store=True)
    note = fields.Text(string="Note")

    # CAMPI MANY2ONE
    currency_id = fields.Many2one("res.currency", string="Valuta", required=True, default=_default_currency)
    nave_id = fields.Many2one("ey_base.unita", string="Nave", index=True, required=True)
    periodo_id = fields.Many2one("ey_contabilita_navi.periodo_contratto", string=u"Periodicità previsionali", required=True)
    soggetto_riferimento_id = fields.Many2one("res.partner", string="Soggetto di riferimento")

    # CAMPI ONE2MANY
    previsionale_ids = fields.One2many("ey_contabilita_navi.previsionale_contratto", "contratto_id", string="Previsionali")
    documento_ids = fields.One2many("ey_contabilita_navi.documenti_contratto", "contratto_id", string="Documenti")

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ey_contabilita_navi.nome_contratto')
        vals['name'] = sequence + ' - ' + vals['nome_contratto']

        result = super(ContrattoNave, self).create(vals)
        return result


class PeriodoContratto(models.Model):
    _name = "ey_contabilita_navi.periodo_contratto"

    @api.depends('mesi')
    def _compute_name(self):
        """
        Compte il nome del tipo periodo
        """
        for rec in self:
            if rec.mesi and rec.mesi > 0:
                name = str(rec.mesi) + " "
                if rec.mesi > 1:
                    rec.name = name + "mesi"
                else:
                    rec.name = name + "mese"

    name = fields.Char(string="Periodo", compute="_compute_name", index=True, store=True)
    mesi = fields.Integer(string="Mesi", required=True)

    @api.model
    def create(self, vals):
        if 'mesi' not in vals or vals['mesi'] < 1:
            raise ValidationError("Numero mesi non può essere 0 o negativo")
        return super(PeriodoContratto, self).create(vals)


class DocumentiContratto(models.Model):
    _name = "ey_contabilita_navi.documenti_contratto"

    ##### FUNZIONI PER IL SET E IL GET DEL BINARY
    def _get_document(self):
        ids = []
        for rec in self:
            ids.append(rec.id)
        ir_attachment_model = self.env['ir.attachment']
        domain_attachment = [('res_model', '=', self._name), ('res_id', 'in', ids)]
        attachments = ir_attachment_model.search(domain_attachment)
        for att in attachments:
            for rec in self:
                if rec.id == att.res_id:
                    rec.document = att.datas
                    break

    def _set_document(self):
        self.ensure_one()
        max_id = 0
        cr = self._cr
        cr.execute("SELECT max(id) AS id FROM ey_corsi_documento_corso")
        dati = cr.dictfetchone()
        if dati['id']:
            max_id = int(dati['id']) + 1
        else:
            max_id = 1
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'documenti_contratto_' + str(max_id),
            'datas_fname': 'documenti_contratto_' + str(max_id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments and not self.document:
            return attachments.unlink()
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    #####COLUMNS
    descrizione = fields.Char(string="Descrizione", required=True, index=True)
    data_inserimento = fields.Date(string="Data inserimento", default=lambda *a: time.strftime('%Y-%m-%d'))
    data_documento = fields.Date(string="Data documento")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Documento")
    document_fname = fields.Char(string="File name")

    # CAMPI MANY2ONE
    contratto_id = fields.Many2one("ey_contabilita_navi.contratto_nave", index=True)
    tipo_id = fields.Many2one(comodel_name="ey_contabilita_navi.tipo_documento", index=True)


class TipoDocumento(models.Model):
    _name = "ey_contabilita_navi.tipo_documento"

    name = fields.Char(string="Tipo", required=True, index=True)
