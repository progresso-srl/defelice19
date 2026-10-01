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


##############################################################################
## ISCRIZIONE ################################################################
##############################################################################
class IscrizioneEsame(models.Model):
    _inherit = "ey.iscrizione_esame"

    note = fields.Text(string="Note")
    marittimo_id = fields.Many2one("res.partner", string="Corsista", required=True, index=True,
                                   domain=['|', ('anagrafica_ey', '=', True), '|', ('personale_ey', '=', True), ('armatore_proprietario', '=', True)])


##############################################################################
## PRE-ISCRIZIONE#############################################################
##############################################################################
class PreIscrizioneEsame(models.Model):
    _name = "ey2.pre_iscrizione_esame"
    _order = "esito asc"

    _ESITI = [
        ('In attesa', 'In attesa'),
        ('Iscritto', 'Iscritto'),
        ('Annullata', 'Annullata')
    ]

    @api.multi
    def stampa_reg_form(self):
        self.ensure_one()
        context = {}
        for key in self.env.context.keys():
            context[key] = self.env.context[key]
        context['model'] = 'ey2.pre_iscrizione_esame'
        context['iscrizione_id'] = self.id

        return {
            'type': 'ir.actions.report.xml',
            'report_name': self.esame_id.template_id.name + "_rfe_report",
            'context': context
        }

    @api.multi
    def crea_iscrizione(self):
        self.ensure_one()
        iscrizione_vals = {
            'marittimo_id': self.marittimo_id.id,
            'destinatario_id': self.destinatario_id.id,
            'data_iscrizione': self.data_iscrizione,
            'prezzo_scontato': self.prezzo_scontato,
            'rf_compilato': self.rf_compilato,
            'prezzo_esame': self.prezzo_esame,
            'esame_id': self.esame_id.id,
            'rf_fname': self.rf_fname,
            'tipo_iscritto': self.tipo_iscritto
        }
        iscrizione = self.env['ey.iscrizione_esame'].create(iscrizione_vals)
        self.write({
            'iscrizione_id': iscrizione.id,
            'esito': 'Iscritto'
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey.iscrizione_esame',
            'view_mode': 'form',
            'res_id': iscrizione.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    #####ONCHANGE
    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            return {'domain': {
                'esame_id': [
                    ('template_id', '=', self.template_id.id),
                    ('data_esame', '>=', datetime.today().strftime('%Y-%m-%d')),
                    ('computed', '=', False)
                ]
            }}

    @api.onchange("esame_id")
    def onchange_esame_id(self):
        if self.esame_id:
            if not self.template_id:
                raise ValidationError("Selezionare prima il template dell'esame")
            if self.tipo_iscritto == 'interno':
                self.prezzo_esame = self.esame_id.prezzo_interni
            else:
                self.prezzo_esame = self.esame_id.prezzo_esterni

    @api.onchange("tipo_iscritto")
    def onchange_tipo_iscritto(self):
        if self.esame_id:
            if self.tipo_iscritto == 'interno':
                self.prezzo_esame = self.esame_id.prezzo_interni
            else:
                self.prezzo_esame = self.esame_id.prezzo_esterni

    @api.onchange("marittimo_id")
    def onchange_marittimo_id(self):
        if self.marittimo_id and self.marittimo_id.blacklist:
            raise ValidationError("Errore di inserimento. Contattare amministratore")

    @api.depends('esame_id', 'marittimo_id')
    def _compute_name(self):
        for iscrizione in self:
            name = ""
            if iscrizione.esame_id:
                name += iscrizione.esame_id.name
            if iscrizione.marittimo_id:
                name += " - " + iscrizione.marittimo_id.name
            iscrizione.name = name

    # funzioni per il reg form
    @api.multi
    def _get_rf_compilato(self):
        ids = []
        for rec in self:
            ids.append(rec.id)
        ir_attachment_model = self.env['ir.attachment']
        domain_attachment = [('res_model', '=', self._name), ('res_id', 'in', ids)]
        attachments = ir_attachment_model.search(domain_attachment)
        for att in attachments:
            for rec in self:
                if rec.id == att.res_id:
                    rec.rf_compilato = att.datas
                    break

    @api.one
    def _set_rf_compilato(self):
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'pe_rf_compilato_' + str(self.id),
            'datas_fname': 'pe_rf_compilato_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.rf_compilato
        }
        attachments = ir_attachment_model.search([('datas_fname', '=', 'pe_rf_compilato_' + str(self.id)),
                                                  ('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    #####VALIDATE
    @api.one
    @api.constrains('marittimo_id', 'esame_id')
    def _validate_fields(self, context=None):
        """
        Controllo che un marittimo non venga iscritto 2 volte a un corso
        e che il corso non superi il numero massimo iscrizioni
        """
        if self.marittimo_id and self.esame_id:
            domain_iscr = [
                ('marittimo_id', '=', self.marittimo_id.id),
                ('esame_id', '=', self.esame_id.id)
            ]
            iscrizioni = self.env['ey2.pre_iscrizione_esame'].search(domain_iscr)
            for iscr in iscrizioni:
                if iscr.id != self.id:
                    raise ValidationError("Marittimo già pre-iscritto a quell'esame")
        if self.esame_id:
            if len(self.esame_id.iscrizione_ids) > self.esame_id.max_iscritti:
                raise ValidationError("L'esame ha raggiunto il numero massimo di iscritti")

    created = fields.Boolean(string="Created", index=True)
    template_id = fields.Many2one("ey.template_esame", string="Template esame", index=True, required=True)
    name = fields.Char(compute="_compute_name", store=True, index=True)
    data_iscrizione = fields.Date(string="Data iscrizione", index=True, default=lambda self: fields.datetime.now())
    marittimo_id = fields.Many2one("res.partner", string="Corsista", required=True, index=True,
                                   domain=['|', ('anagrafica_ey', '=', True), '|', ('personale_ey', '=', True), ('armatore_proprietario', '=', True)])
    destinatario_id = fields.Many2one("res.partner", string="Destinatario fatture", index=True,
                                      help=u"Inserire se il destinatario delle fatture non è il marittimo iscritto")
    tipo_iscritto = fields.Selection([('interno', 'Interno'), ('esterno', 'Esterno')], string="Tipo iscritto",
                                     default="esterno", index=True)
    esame_id = fields.Many2one("ey.esame", string="Esame",  index=True)
    prezzo_esame = fields.Float(string="Costo iscrizione")
    prezzo_scontato = fields.Boolean(string="Scontato", index=True)
    # registration form
    rf_compilato = fields.Binary(compute="_get_rf_compilato", inverse="_set_rf_compilato",
                                 string="Registration form compilato (pdf)")
    rf_fname = fields.Char(string="File name")
    # documenti_marittimo
    documento_ids = fields.One2many(related='marittimo_id.documento_ids', string="Documenti marittimo")
    # viene inizializzata solo nel momento in cui viene pigiato il bottone "crea iscrizione"
    iscrizione_id = fields.Many2one("ey.iscrizione_esame", string="Iscrizione collegata", index=True)
    # esiti
    esito = fields.Selection(_ESITI, string="Esito", index=True, required=True, default="In attesa")
    note_esito = fields.Text(string="Note esito")

    @api.model
    def create(self, vals):
        vals['created'] = True
        return super(PreIscrizioneEsame, self).create(vals)
