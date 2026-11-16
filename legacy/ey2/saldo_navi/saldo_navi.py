# -*- coding: utf-8 -*-
##############################################################################
#
#    CASE module for OpenERP
#    Copyright (C) 20013 Future Tech srl (http://www.futuretechsrl.it).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models
from openerp.exceptions import ValidationError
from datetime import datetime


class PeriodoNave(models.Model):
    _name = "ey2.periodo_nave"

    @api.depends('mesi')
    def _compute_name(self):
        """
        Compuat il nome del tipo periodo
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
        return super(PeriodoNave, self).create(vals)


class ContrattoNave(models.Model):
    _name = "ey2.contratto_nave"

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

    @api.multi
    def button_crea_prossimo_previsionale(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ey2.wiz_crea_prossimo_previsionale',
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

    @api.depends("previsionale_ids", "previsionale_ids.bilancio")
    def _compute_saldo(self):
        for rec in self:
            saldo = rec.saldo_iniziale
            for p in rec.previsionale_ids:
                saldo += p.bilancio
            rec.saldo_attuale = saldo

    @api.depends('nave_id', 'nave_id.name', 'mese_inizio', 'anno_inizio')
    def _compute_name(self):
        for rec in self:
            name = ""
            if rec.nave_id:
                name += rec.nave_id.name + " - "
            if rec.mese_inizio and rec.anno_inizio:
                name += rec.mese_inizio + "/" + rec.anno_inizio
            rec.name = name

    @api.model
    def _default_currency(self):
        currency = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
        return currency.id

    name = fields.Char(string="Contratto", compute="_compute_name", store=True)
    currency_id = fields.Many2one("res.currency", string="Valuta", required=True, default=_default_currency)
    mese_inizio = fields.Selection(_MESI, string="Mese inizio", index=True, required=True)
    anno_inizio = fields.Selection(_get_selection_years, string="Anno inizio", index=True, required=True)
    attivo = fields.Boolean(string="Attivo", index=True, default=True)
    nave_id = fields.Many2one("ey.unita", string="Nave", index=True, required=True)
    periodo_id = fields.Many2one("ey2.periodo_nave", string=u"Periodicità previsionali", required=True)
    previsionale_ids = fields.One2many("ey2.previsionale_nave", "contratto_id", string="Previsionali")
    saldo_iniziale = fields.Float(string="Saldo iniziale")
    saldo_attuale = fields.Float(string="Saldo attuale", compute="_compute_saldo", store=True)
    note = fields.Text(string="Note")
    # @TODO: inserire prodotti da fatturare ogni periodo (poi vedere come e a chi generare le fatture e se aggiungere periodicità fatturazione indipendente)


class TipoSpesaNave(models.Model):
    _name = "ey2.tipo_spesa_nave"

    name = fields.Char(stinrg="Tipo spesa", index=True, required=True)


class SpesaNave(models.Model):
    _name = "ey2.spesa_nave"

    @api.onchange('tipo_id')
    def onchange_tipo_id(self):
        if self.tipo_id and self.tipo_id.name:
            self.name = self.tipo_id.name

    tipo_id = fields.Many2one("ey2.tipo_spesa_nave", stinrg="Spesa", index=True, required=True)
    name = fields.Char(string="Descrizione", required=True)
    previsto = fields.Float(string="Spesa prevista")
    effettivo = fields.Float(string="Spesa effettiva")
    previsionale_id = fields.Many2one("ey2.previsionale_nave", index=True)


class PrevisionaleNave(models.Model):
    _name = "ey2.previsionale_nave"
    _order = "anno_inizio desc, mese_inizio desc"

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

    _STATE = [
        ('Previsionale', 'Previsionale'),
        ('Consolidato', 'Consolidato'),
        ('Chiuso', 'Chiuso')
    ]

    @api.multi
    def stato_previsionale(self):
        return self.write({'state': 'Previsionale'})

    @api.multi
    def stato_consolidato(self):
        return self.write({'state': 'Consolidato'})

    @api.multi
    def stato_chiuso(self):
        return self.write({'state': 'Chiuso'})

    @api.depends('spesa_ids', 'spesa_ids.effettivo', 'spesa_ids.previsto')
    def _compute_totali(self):
        """
        Compuat i totali
        """
        for rec in self:
            richiesto = 0.0
            speso = 0.0
            for spesa in rec.spesa_ids:
                richiesto += spesa.previsto
                speso += spesa.effettivo
            rec.totale_richiesto = richiesto
            rec.totale_speso = speso
            rec.bilancio = richiesto - speso

    @api.depends('contratto_id', 'contratto_id.name', 'mese_inizio', 'anno_inizio')
    def _compute_name(self):
        for rec in self:
            name = ""
            if rec.contratto_id:
                name += rec.contratto_id.name + " PERIODO "
            if rec.mese_inizio and rec.anno_inizio:
                name += rec.mese_inizio + "/" + rec.anno_inizio
            rec.name = name

    name = fields.Char(string="Contratto", compute="_compute_name", store=True)
    state = fields.Selection(_STATE, string="State", index=True, default="Previsionale")
    currency_id = fields.Many2one("res.currency", string="Valuta", required=True, related='contratto_id.currency_id')
    contratto_id = fields.Many2one("ey2.contratto_nave", string="Contratto collegato", required=True, index=True)
    spesa_ids = fields.One2many("ey2.spesa_nave", "previsionale_id", string="Spese")
    totale_richiesto = fields.Float(string="Totale richiesto", compute="_compute_totali", store=True)
    totale_speso = fields.Float(string="Totale speso", compute="_compute_totali", store=True)
    bilancio = fields.Float(string="Bilancio", compute="_compute_totali", store=True)
    mese_inizio = fields.Selection(_MESI, string="Mese", index=True)
    anno_inizio = fields.Char(string="Anno", size=4, index=True)
    durata_id = fields.Many2one("ey2.periodo_nave", string="Durata", related="contratto_id.periodo_id", store=True)
    # @TODO: STATO PREVISIONALE: Aperto o Chiuso. Possibilità di chiudere confermando le spese oppure dopo averlo fatto a mano ma con conferma! In stato chiuso le spese non si toccano più