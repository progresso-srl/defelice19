# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import time


class ContrattoNave(models.Model):
    _name = "ey_contabilita_navi.contratto_nave"
    _description = "Contratto nave"

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
                'view_mode': 'list,form',
                'domain': [('contratto_id', '=', self.id)],
            }

    def button_crea_prossimo_previsionale(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ey_contabilita_navi.wiz_crea_prossimo_previsionale',
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
        # Prima era "EUR" cercato per nome: se la valuta non e' attiva il campo
        # (obbligatorio) restava vuoto. La valuta della societa' c'e' sempre.
        return self.env.company.currency_id.id

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

    @api.model_create_multi
    def create(self, vals_list):
        # Odoo 19: create riceve sempre una lista; la logica resta per record.
        return self.browse().concat(*(self._ey_create_one(vals) for vals in vals_list))

    def _ey_create_one(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ey_contabilita_navi.nome_contratto')
        vals['name'] = sequence + ' - ' + vals['nome_contratto']

        result = super(ContrattoNave, self).create(vals)
        return result


class PeriodoContratto(models.Model):
    _name = "ey_contabilita_navi.periodo_contratto"
    _description = "Periodo contratto"

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

    @api.model_create_multi
    def create(self, vals_list):
        # Odoo 19: create riceve sempre una lista; la logica resta per record.
        return self.browse().concat(*(self._ey_create_one(vals) for vals in vals_list))

    def _ey_create_one(self, vals):
        if 'mesi' not in vals or vals['mesi'] < 1:
            raise ValidationError("Numero mesi non può essere 0 o negativo")
        return super(PeriodoContratto, self).create(vals)


class DocumentiContratto(models.Model):
    _name = "ey_contabilita_navi.documenti_contratto"
    _description = "Documenti contratto"
    _inherit = ["ey_base.documento_allegato_mixin"]
    _ey_document_prefix = "documenti_contratto"

    #####COLUMNS
    descrizione = fields.Char(string="Descrizione", required=True, index=True)
    data_inserimento = fields.Date(string="Data inserimento", default=lambda *a: time.strftime('%Y-%m-%d'))
    data_documento = fields.Date(string="Data documento")

    # CAMPI MANY2ONE
    contratto_id = fields.Many2one("ey_contabilita_navi.contratto_nave", index=True)
    tipo_id = fields.Many2one(comodel_name="ey_contabilita_navi.tipo_documento", index=True)


class TipoDocumento(models.Model):
    _name = "ey_contabilita_navi.tipo_documento"
    _description = "Tipo documento"

    name = fields.Char(string="Tipo", required=True, index=True)
