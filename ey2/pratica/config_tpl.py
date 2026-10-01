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
import time
from datetime import datetime


##############################################################################
## TPL #######################################################################
##############################################################################
class Tpl(models.Model):
    _inherit = "config_tpl.tpl"

    _TIPO_TEMPLATE = [
        ('Navi', 'Navi'),
        ('Soggetti', 'Soggetti')
    ]

    tipo_template = fields.Selection(_TIPO_TEMPLATE, string="Tipo template", index=True)

    @api.multi
    def unlink(self):
        corso_model = self.env['ey2.pratica_nave']
        # controllo che non esistano corsi per il template che si vuol cancellare
        for rec in self:
            pratiche = corso_model.search([('tpl_id', '=', rec.id)])
            if pratiche:
                raise ValidationError("Impossibile cancellare un template con pratiche associate")
        return super(Tpl, self).unlink()


##############################################################################
## CHIAVE PRATICA ############################################################
##############################################################################
class ChiavePraticaNave(models.Model):
    _name = "ey2.chiave_pratica_nave"
    _inherit = "config_tpl.chiave_pratica"

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)


##############################################################################
## REPORT PRATICA ############################################################
##############################################################################
class ReportPraticaNave(models.Model):
    _name = "ey2.report_pratica_nave"
    _inherit = "config_tpl.report_pratica"

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)

    @api.multi
    def button_stampa_pratica(self):
        self.ensure_one()
        # passo il context
        context = {}
        for key in self.env.context.keys():
            context[key] = self.env.context[key]
        if self.pratica_id:
            context.update({'active_ids': [self.pratica_id.partner_id.id]})
            context.update({'pratica_id': self.pratica_id.id})
            context.update({'model_pratica': 'ey2.pratica_nave'})
        else:
            context.update({'active_ids': [self.pratica_soggetto_id.partner_id.id]})
            context.update({'pratica_id': self.pratica_soggetto_id.id})
            context.update({'model_pratica': 'ey2.pratica_soggetto'})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': self.report_id.report_name,
            'context': context
        }


##############################################################################
## INDIRIZZO PARTNER #########################################################
##############################################################################
class IndirizzoPartner(models.Model):
    _name = "ey2.indirizzo_partner"

    @api.depends('street', 'street2', 'city', 'state', 'zip', 'country')
    def _compute_address(self):
        for ip in self:
            address = ""
            if ip.street:
                address += ip.street
            if ip.street2:
                address += " " + ip.street2
            if ip.city:
                address += " " + ip.city
            if ip.state:
                address += " " + ip.state
            if ip.zip:
                address += " " + ip.zip
            if ip.country:
                address += " " + ip.country
            ip.name = address

    name = fields.Text(string="Indirizzo completo", compute="_compute_address", store=True)
    # campi per indirizzo disgiunti
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City")
    state = fields.Char(string="State / Province")
    zip = fields.Char(string="Zip")
    country = fields.Char(string="Country")


##############################################################################
## ENTE PRATICA ##############################################################
##############################################################################
class EntePratica(models.Model):
    _name = "ey2.ente_pratica"
    _rec_name = "denominazione"

    # utility
    def _get_address(self, partner):
        """
        funzione che restituisce un dict coi vals da congelare in armatore e proprietario
        :param partner: obj il partner da cui prendere l'indirizzo
        :return: 
        """
        address_vals = {}
        if partner.street:
            address_vals['street'] = partner.street
        if partner.street2:
            address_vals['street2'] = partner.street2
        if partner.city:
            address_vals['city'] = partner.city
        if partner.state_id:
            address_vals['state'] = partner.state_id.code
        if partner.zip:
            address_vals['zip'] = partner.zip
        if partner.country_id:
            address_vals['country'] = partner.country_id.name
        indirizzo = self.env['ey2.indirizzo_partner'].create(address_vals)
        return indirizzo.id

    @api.multi
    def get_partner(self):
        for ep in self:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ey2.ente',
                'res_id': ep.partner_id.id,
                'target': 'current',
            }

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    partner_id = fields.Many2one("ey2.ente", string="Ente", required=True)
    denominazione = fields.Char(string="Denominazione")
    sede = fields.Char(string="Sede")
    ufficio = fields.Char(string="Ufficio")
    identificatore = fields.Char(string="Identificatore")
    indirizzo_id = fields.Many2one("ey2.indirizzo_partner", string="Indirizzo")
    fiscalcode = fields.Char(string="Cod. Fiscale")

    @api.model
    def create(self, vals):
        ente_pratica = super(EntePratica, self).create(vals)
        ente = ente_pratica.partner_id
        write_vals = {
            'denominazione': ente.denominazione
        }
        if ente.sede_id:
            write_vals['sede'] = ente.sede_id.name
        if ente.ufficio_id:
            write_vals['ufficio'] = ente.ufficio_id.name
        if ente.fiscalcode:
            write_vals['fiscalcode'] = ente.fiscalcode
        write_vals['indirizzo_id'] = self._get_address(ente)
        ente_pratica.write(write_vals)
        return ente_pratica


##############################################################################
## STRUTTURA ARM, PROP E RAPPR ###############################################
##############################################################################
class PropArmPratica(models.Model):
    _name = "ey2.prop_arm_pratica"

    @api.multi
    def get_partner(self):
        for pap in self:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'res_id': pap.partner_id.id,
                'target': 'current',
            }

    @api.multi
    def get_rappresentante(self):
        for pap in self:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ey2.rappresentante_armatore',
                'res_id': pap.rappresentante_id.id,
                'target': 'current',
            }

    pratica_proprietario_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_armatore_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_rappresentante_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    partner_id = fields.Many2one("res.partner", string="Cognome e nome/Rag. sociale", index=True)
    rappresentante_id = fields.Many2one("ey2.rappresentante_armatore", string="Rappresentante", index=True)
    arm_prop = fields.Boolean(default=True)
    cognome = fields.Char(string="Cognome / RS", index=True)
    nome = fields.Char(string="Nome", index=True)
    identificatore = fields.Char(string="Identificatore", index=True)
    stato_civile = fields.Char(string="Stato civile")
    ruolo = fields.Char(string="Ruolo")
    indirizzo_id = fields.Many2one("ey2.indirizzo_partner", string="Indirizzo")
    fiscalcode = fields.Char(string="Cod. Fiscale")
    testo_descrittivo = fields.Char(string="Descr.")
    carati = fields.Char(string="Carati")


##############################################################################
## ALLEGATO PRATICA ##########################################################
##############################################################################
class AllegatoPratica(models.Model):
    _name = "ey2.allegato_pratica"

    ##### FUNZIONI PER IL SET E IL GET DEL BINARY
    @api.multi
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

    @api.one
    def _set_document(self):
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'allegato_pratica_' + str(self.id),
            'datas_fname': 'allegato_pratica' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    name = fields.Char(string="Descrizione", required=True, index=True)
    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Documento")
    document_fname = fields.Char(string="File name")


##############################################################################
## ATTIVITÀ SISTEMA ##########################################################
##############################################################################
class AttSistemaPratica(models.Model):
    _name = "ey2.att_sistema_pratica"
    _order = "data desc"

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    data = fields.Datetime(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True)
    descrizione = fields.Text(string="Descrizione")


##############################################################################
## ATTIVITÀ OPERATORE ##########################################################
##############################################################################
class AttOperatoreaPratica(models.Model):
    _name = "ey2.att_operatore_pratica"
    _order = "data desc"

    #### FUNZIONI PER IL SET E IL GET DEL BINARY
    @api.multi
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

    @api.one
    def _set_document(self):
        max_id = 0
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'documento_aop_pratica_' + str(self.id),
            'datas_fname': 'documento_aop_pratica_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    data = fields.Datetime(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True, required=True)
    descrizione = fields.Text(string="Descrizione")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")


##############################################################################
## CONTATTI PRATICA ##########################################################
##############################################################################
class ContattoPraticaNave(models.Model):
    _name = "ey2.contatto_pratica_nave"

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    partner_id = fields.Many2one('res.partner', index=True)
    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_id = fields.Many2one("ey2.tipo_contatto", string="Ruolo")
    name = fields.Char(string="Nome", required=True)
    phone = fields.Char(string="Telefono", size=50)
    cellulare = fields.Char(string="Cellulare", size=50)
    email = fields.Char(string="Email", size=100)


##############################################################################
## FOLLOW UP #################################################################
##############################################################################
class FollowUpPratica(models.Model):
    _name = "ey2.follow_up_pratica"

    #### FUNZIONI PER IL SET E IL GET DEL BINARY
    @api.multi
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

    @api.one
    def _set_document(self):
        max_id = 0
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'documento_follow_up_pratica_' + str(self.id),
            'datas_fname': 'documento_follow_up_pratica_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    @api.depends('descrizione')
    def _compute_preview(self):
        for fu in self:
            if fu.descrizione:
                fu.prev_descrizione = fu.descrizione[:30] + "..."
            else:
                fu.prev_descrizione = ""

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    data = fields.Date(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True)
    oggetto = fields.Char(string="Oggetto")
    descrizione = fields.Text(string="Descrizione")
    prev_descrizione = fields.Char(string="Descrizione", compute="_compute_preview")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")


##############################################################################
## QUALIFICA #################################################################
##############################################################################
class QualificaPraticaNave(models.Model):
    _name = "ey2.qualifica_pratica_nave"

    name = fields.Char(string="Qualifica", index=True, reuqired=True)


##############################################################################
## ALERT PRATICA #############################################################
##############################################################################
class AlertPratica(models.Model):
    _name = "ey2.alert_pratica_nave"
    _order = "attivo desc"

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    pratica_id = fields.Many2one("ey2.pratica_nave", index=True)
    pratica_soggetto_id = fields.Many2one("ey2.pratica_soggetto", index=True)
    data = fields.Date(string="Data", required=True)
    descrizione = fields.Char(string="Descrizione", reuqired=True, required=True)
    attivo = fields.Boolean(string="Attivo", index=True, default=True)
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True, required=True)

    @api.multi
    def write(self, vals):
        for ap in self:
            if 'attivo' in vals and vals['attivo']:
                altri_alerts = self.env['ey2.alert_pratica_nave'].search([('pratica_id', '=', ap.pratica_id.id)])
                for aa in altri_alerts:
                    if aa.id != ap.id and aa.attivo:
                        raise ValidationError("Esiste già un alert attivo per questa pratica")
        return super(AlertPratica, self).write(vals)

    @api.model
    def create(self, vals):
        alert = super(AlertPratica, self).create(vals)
        altri_alert = self.search([('pratica_id', '=', alert.pratica_id.id)])
        for ap in altri_alert:
            if ap.id != alert.id:
                ap.write({'attivo': False})
        return alert


##############################################################################
## PRATICA ###################################################################
##############################################################################
class PraticaNave(models.Model):
    _name = "ey2.pratica_nave"
    _inherit = "config_tpl.pratica"
    _order = "state asc, data_pratica desc"

    ##### FUNZIONI PER IL CAMBIAMENTO DI STATO
    @api.multi
    def stato_preventivo(self):
        return self.write({'state': 'c-Pre-istruzione'})

    @api.multi
    def stato_in_corso(self):
        to_write = {'state': 'h-In corso'}
        if not self.riferimento_pratica:
            domain_sequence = [
                ("code", '=', "ey2_riferimento_pratica"),
            ]
            sequence = self.env['ir.sequence'].search(domain_sequence, limit=1)
            next_code = self.env['ir.sequence'].next_by_id(sequence.id)
            to_write['riferimento_pratica'] = next_code
            to_write['protocollo_data'] = time.strftime('%Y-%m-%d')
        return self.write(to_write)

    @api.multi
    def stato_da_fatturare(self):
        return self.write({'state': 'p-Da fatturare'})

    @api.multi
    def stato_fatturata(self):
        return self.write({'state': 's-Fatturata'})

    @api.multi
    def stato_pagata(self):
        return self.write({'state': 'v-Pagata'})

    @api.multi
    def stato_sospesa(self):
        return self.write({'state': 'x-Sospesa'})

    @api.multi
    def stato_annullata(self):
        return self.write({'state': 'z-Annullata'})

    _STATO_PRATICA = [
        ("c-Pre-istruzione", "Pre-istruzione"),
        ("h-In corso", "In corso"),
        ("p-Da fatturare", "Da fatturare"),
        ("s-Fatturata", "Fatturata"),
        ("v-Pagata", "Pagata"),
        ("x-Sospesa", "Sospesa"),
        ("z-Annullata", "Annullata"),
        ("a-Alert", "Alert")
    ]

    # utility
    def _get_address(self, partner):
        """
        funzione che restituisce un dict coi vals da congelare in armatore e proprietario
        :param partner: obj il partner da cui prendere l'indirizzo
        :return: 
        """
        address_vals = {}
        if partner.street:
            address_vals['street'] = partner.street
        if partner.street2:
            address_vals['street2'] = partner.street2
        if partner.city:
            address_vals['city'] = partner.city
        if partner.state_id:
            address_vals['state'] = partner.state_id.code
        if partner.zip:
            address_vals['zip'] = partner.zip
        if partner.country_id:
            address_vals['country'] = partner.country_id.name
        indirizzo = self.env['ey2.indirizzo_partner'].create(address_vals)
        return indirizzo.id

    # utility
    def _compute_prop_arm(self, obj_list, field, pratica_id, prop_arm=True):
        """
        Funzione che aggiorna la lista degli armatori o dei proprietari
        :param obj_list: list lista degli armatori/proprietari della nave
        :param field: string 'pratica_proprietario_id' o 'pratica_armatore_id'
        :param pratica_id: integer id della pratica
        :param prop_arm: Boolean False se si crea un rappresentante
        :return: 
        """
        model = self.env['ey2.prop_arm_pratica']
        field_partner = "partner_id"
        if not prop_arm:
            field_partner = "rappresentante_id"
        for item in obj_list:
            partner = getattr(item, field_partner)
            stato_civile = ""
            if partner.stato_civile:
                stato_civile = partner.stato_civile.name
            # solo se il proprietario/armatore è attivo
            if item.riferimento:
                vals = {
                    field: pratica_id,
                    'cognome': partner.cognome,
                    'nome': partner.nome,
                    'partner_id': partner.id,
                    'stato_civile': stato_civile,
                    'indirizzo_id': self._get_address(partner),
                    'identificatore': item.identificatore,
                    'fiscalcode': partner.fiscalcode
                }
                if not prop_arm:
                    vals['ruolo'] = item.ruolo_id.name
                    vals['testo_descrittivo'] = item.testo_descrittivo
                if field == 'pratica_proprietario_id':
                    vals['carati'] = item.carati
                model.create(vals)

    @api.depends('tpl_id', 'tpl_id.name', 'partner_id', 'partner_id.name', 'partner_riferimento_id',
                 'partner_riferimento_id.name')
    def _compute_name(self):
        for pratica in self:
            name = ""
            if pratica.tpl_id:
                name += pratica.tpl_id.name
            if pratica.partner_id:
                name += " - " + pratica.partner_id.name
            if pratica.partner_riferimento_id:
                name += " - " + pratica.partner_riferimento_id.name
            pratica.name = name

    @api.depends('att_operatore_ids', 'att_operatore_ids.descrizione', 'att_operatore_ids.data')
    def _compute_ultima_attivita(self):
        for pratica in self:
            date = "1970-01-01"
            descr = ""
            for att in pratica.att_operatore_ids:
                if att.data > date:
                    date = att.data
                    descr = att.descrizione
            if len(descr) > 255:
                descr = descr[:252] + "..."
            pratica.ultima_attivita = descr

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        if self.partner_id and self.partner_id.blacklist:
            raise ValidationError("Errore di inserimento. Contattare amministratore")

    @api.one
    @api.constrains('partner_id')
    def _validate_fields(self, context=None):
        if self.partner_id and self.partner_id.blacklist:
            raise ValidationError("Errore di inserimento. Contattare amministratore")

    name = fields.Char(string="Nome pratica", index=True, required=True, compute="_compute_name", store=True)
    partner_id = fields.Many2one(comodel_name="ey.unita", string="Nave", required=True, index=True)
    report_ids = fields.One2many("ey2.report_pratica_nave", "pratica_id", string="Reports", ondelete="cascade")
    chiave_ids = fields.One2many("ey2.chiave_pratica_nave", "pratica_id", string="Chiavi", ondelete="cascade")
    partner_riferimento_id = fields.Many2one("res.partner", string="Marittimo di riferimento", index=True)
    tipo_pratica = fields.Char(string="Tipo pratica", index=True)
    tipo_documento_id = fields.Many2one("ey.tipo_documento", string="Tipo documento marittimo", index=True)
    data_pratica = fields.Date(string="Data pre-istruzione", index=True, required=True,
                               default=lambda *a: time.strftime('%Y-%m-%d'))
    state = fields.Selection(_STATO_PRATICA, string="Stato pratica", index=True, required=True,
                             default="c-Pre-istruzione", track_visibility='onchange')
    qualifica_id = fields.Many2one("ey2.qualifica_pratica_nave", string="Qualifica", index=True)
    # campi da prendere dalla nave al create e non più modificabili
    nome_nave = fields.Char(string="Nome nave", index=True)
    riferimento_nave = fields.Char(string="Riferimento nave", index=True)
    tipo_registro_nave = fields.Char(string="Tipo registro nave", index=True)
    numero_registro_nave = fields.Char(string="Numero registro nave", index=True)
    porto_nave = fields.Char(string="Porto di registro nave", index=True)
    bandiera_nave = fields.Char(string="Bandiera nave", index=True)
    stazza_lorda_nave = fields.Char(string="Stazza lorda nave")
    utilizzo_nave =  fields.Char(string="Utilizzo", index=True)
    # campi da congelare per il marittimo di riferimento
    cognome_marittimo = fields.Char(string="Cognome marittimo")
    nome_marittimo = fields.Char(string="Nome marittimo")
    cf_marittimo = fields.Char(string="Codice fiscale marittimo")
    indirizzo_marittimo_id = fields.Many2one("ey2.indirizzo_partner", string="Indirizzo marittimo")
    stato_civile_marittimo = fields.Char(string="Stato civile marittimo")
    cittadinanza_marittimo = fields.Char(string="Cittadinanza marittimo")
    tipo_documento_marittimo = fields.Char(string="Tipo documento marittimo")
    numero_documento_marittimo = fields.Char(string="Numero documento marittimo")
    rilascio_documento_marittimo = fields.Char(string="Uff. rilascio documento marittimo")
    luogo_rilascio_documento_marittimo = fields.Char(string="Luogo rilascio documento marittimo")
    categoria_documento_marittimo = fields.Char(string="Categoria documento marittimo")
    documento_marittimo_id = fields.Many2one("ey.documento", string="Documento marittimo")
    # armatori e proprietari
    armatore_ids = fields.One2many("ey2.prop_arm_pratica", "pratica_armatore_id", string="Armatori")
    proprietario_ids = fields.One2many("ey2.prop_arm_pratica", "pratica_proprietario_id", string="Proprietari")
    rappresentante_ids = fields.One2many("ey2.prop_arm_pratica", "pratica_rappresentante_id", string="Rappresentanti")
    # enti
    ente_ids = fields.One2many("ey2.ente_pratica", "pratica_id", string="Enti")
    # allegati
    info_operatore = fields.Text(string="Info operatore")
    allegati = fields.Many2many(comodel_name="config_tpl.allegato_tpl", relation="pratica_allegato_model",
                                string="Allegati", index=True)
    # documenti
    documenti_pratica_ids = fields.One2many("ey2.allegato_pratica", "pratica_id", string="Documenti pratica")
    # soggetto per fatturazione
    soggetto_fatturazione_id = fields.Many2one("res.partner", string="Soggetto fatturazione")
    # attività di sistema
    att_sistema_ids = fields.One2many("ey2.att_sistema_pratica", "pratica_id", string=u"Attività di sistema")
    # attività operatore
    ultima_attivita = fields.Char(string=u"Ultima attività", compute="_compute_ultima_attivita")
    att_operatore_ids = fields.One2many("ey2.att_operatore_pratica", "pratica_id", string=u"Attività operatore")
    # contatti pratica
    contatto_pratica_ids = fields.One2many("ey2.contatto_pratica_nave", 'pratica_id', string="Contatti")
    # pratiche collegate
    pratiche_collegate = fields.Many2many(comodel_name="ey2.pratica_nave", relation="ey2_pratiche_collegate_rel",
                                          column1="pratica1_id", column2="pratica2_id", string="Pratiche collegate",
                                          index=True)
    #follow up
    follow_up_ids = fields.One2many("ey2.follow_up_pratica", "pratica_id", string="Follow up")
    #alerts
    alert_ids = fields.One2many("ey2.alert_pratica_nave", "pratica_id", string="Alerts")
    #responsabile della pratica
    user_id = fields.Many2one("res.users", string="Responsabile", index=True, required=True,
                              default=lambda self: self.env.user)
    riferimento_pratica = fields.Char(string="Protocollo numero", index=True)
    protocollo_data = fields.Date(string="Protocollo data", index=True)
    #sted
    sted_nr_dci = fields.Char(string="Nr.DCI", index=True)
    sted_nr_pratica = fields.Char(string="Nr. Pratica", index=True)
    sted_data_dci = fields.Date(string="Data DCI", index=True)
    sted_data_pratica = fields.Date(string="Data pratica", index=True)
    sted_ente_rilascio = fields.Many2one("ey2.ente_sorveglianza", string="Ente rilascio DCI")

    @api.one
    def compute_prop_arm(self, obj, field, pratica_id, ruolo=False):
        """
        Funzione che aggiorna la lista degli armatori o dei proprietari
        :param obj_list: list lista degli armatori/proprietari della nave
        :param field: string 'pratica_proprietario_id' o 'pratica_armatore_id'
        :param pratica_id: integer id della pratica
        :param prop_arm: Boolean False se si crea un rappresentante
        :return:
        """
        model = self.env['ey2.prop_arm_pratica']
        #field_partner = "partner_id"
        #if not prop_arm:
        #    field_partner = "rappresentante_id"
        partner = obj
        stato_civile = ""
        if partner.stato_civile:
            stato_civile = partner.stato_civile.name
        # solo se il proprietario/armatore è attivo
        vals = {
            field: pratica_id,
            'cognome': partner.cognome,
            'nome': partner.nome,
            'partner_id': partner.id,
            'stato_civile': stato_civile,
            'indirizzo_id': self._get_address(partner),
            'identificatore': "",
            'fiscalcode': partner.fiscalcode
        }
        if ruolo:
            vals['ruolo'] = ruolo
        model.create(vals)

    @api.model
    def create(self, vals):
        vals['created'] = True
        name = ""
        if vals['tpl_id']:
            name += self.env['config_tpl.tpl'].browse([vals['tpl_id']])[0].name
        if vals['partner_id']:
            name += " - " + self.env['ey.unita'].browse([vals['partner_id']])[0].name
        if vals['partner_riferimento_id']:
            name += " - " + self.env['res.partner'].browse([vals['partner_riferimento_id']])[0].name
        vals['name'] = name
        pratica = super(PraticaNave, self).create(vals)
        # PARTE IN CUI SETTO I VALORI RELATIVI ALLA NAVE
        riferimento_nave, tipo_registro_nave, numero_registro_nave, porto_nave, bandiera_nave = ("", "", "", "", "")
        riferimento_nave = pratica.partner_id.riferimento
        if pratica.partner_id.nr_on:
            numero_registro_nave = pratica.partner_id.nr_on
        utilizzo_nave = ""
        if pratica.partner_id.utilizzo_id:
            utilizzo_nave = pratica.partner_id.utilizzo_id.name
        tipo_registro_nave = pratica.partner_id.tipo_registro_id.name
        porto_nave = pratica.partner_id.porto_id.name
        bandiera_nave = pratica.partner_id.bandiera_id.name
        soggetto_fatturazione_nave_id = False
        if pratica.partner_id.soggetto_fatturazione_id:
            soggetto_fatturazione_nave_id = pratica.partner_id.soggetto_fatturazione_id.id
        # campi partner_riferimento
        doc_obj = None
        cognome_marittimo, nome_marittimo, cf_marittimo, indirizzo_marittimo = ("", "", "", "")
        cittadinanza_marittimo, stato_civile_marittimo = ("", "")
        if pratica.partner_riferimento_id:
            cognome_marittimo = pratica.partner_riferimento_id.cognome
            nome_marittimo = pratica.partner_riferimento_id.nome
            cf_marittimo = pratica.partner_riferimento_id.fiscalcode
            indirizzo_marittimo = self._get_address(pratica.partner_riferimento_id)
            if pratica.partner_riferimento_id.stato_civile:
                stato_civile_marittimo = pratica.partner_riferimento_id.stato_civile.name
            if pratica.partner_riferimento_id.nazionalita_id:
                cittadinanza_marittimo = pratica.partner_riferimento_id.nazionalita_id.name
            # cerco il documento del marittomo
            max_date = ""
            for doc in pratica.partner_riferimento_id.documento_ids:
                if doc.tipo_id.name == pratica.tipo_documento_id.name:
                    scadenza = doc.data_scadenza or ""
                    if scadenza >= max_date:
                        doc_obj = doc
                        max_date = scadenza
            if not doc_obj:
                raise ValidationError(
                    "Il marittimo in questione non ha un documento di tipo " + pratica.tipo_documento_id.name)
        campi_da_congelare = {
            'info_operatore': pratica.tpl_id.info_operatore,
            "tipo_pratica": pratica.tpl_id.tipo_pratica,
            "nome_nave": pratica.partner_id.name,
            "stazza_lorda_nave": ("%.2f" % pratica.partner_id.stazza_lorda).replace(".", ","),
            "riferimento_nave": riferimento_nave,
            "tipo_registro_nave": tipo_registro_nave,
            "utilizzo_nave": utilizzo_nave,
            "numero_registro_nave": numero_registro_nave,
            "porto_nave": porto_nave,
            "bandiera_nave": bandiera_nave,
            "indirizzo_marittimo_id": indirizzo_marittimo,
            "stato_civile_marittimo": stato_civile_marittimo,
            "cittadinanza_marittimo": cittadinanza_marittimo,
            "soggetto_fatturazione_id": soggetto_fatturazione_nave_id,
            # marittimo_di_riferimento
            'cognome_marittimo': cognome_marittimo,
            'nome_marittimo': nome_marittimo,
            'cf_marittimo': cf_marittimo
        }
        if doc_obj:
            campi_da_congelare['tipo_documento_marittimo'] = doc_obj.tipo_id.name
            campi_da_congelare['numero_documento_marittimo'] = doc_obj.numero_documento or ""
            campi_da_congelare['rilascio_documento_marittimo'] = doc_obj.ufficio_id.name
            campi_da_congelare['categoria_documento_marittimo'] = doc_obj.categoria or ""
            campi_da_congelare['luogo_rilascio_documento_marittimo'] = doc_obj.luogo_rilascio or ""
            campi_da_congelare['documento_marittimo_id'] = doc_obj.id
        # scrivo gli allegati
        allegati_list = []
        for allegato in pratica.tpl_id.allegato_ids:
            allegati_list.append(allegato.id)
        if len(allegati_list) > 0:
            campi_da_congelare['allegati'] = [(6, 0, allegati_list)]
        #sted
        if pratica.tpl_id.tipo_pratica == 'Pratica STED':
            campi_da_congelare['sted_nr_dci'] = pratica.partner_id.sted_nr_dci
            campi_da_congelare['sted_data_dci'] = pratica.partner_id.sted_data_dci
            if pratica.partner_id.sted_ente_rilascio:
                campi_da_congelare['sted_ente_rilascio'] = pratica.partner_id.sted_ente_rilascio.id
        pratica.write(campi_da_congelare)
        # PARTE IN CUI SETTO IL VALORE DELLE CHIAVI
        # models
        cp_model = self.env['ey2.chiave_pratica_nave']
        rp_model = self.env['ey2.report_pratica_nave']
        ir_model = self.env['ir.actions.report.xml']
        # inizializzo le chiavi
        tpl = pratica.tpl_id
        partner = pratica.partner_id
        for chiave in tpl.chiave_ids:
            key = chiave.chiave
            descrizione = chiave.descrizione
            if chiave.tipo_chiave == 'Campo':
                arr_value = key.split(".")
                result = ""
                value = ""
                is_valore = False
                obj = partner
                try:
                    for field in arr_value:
                        obj = getattr(obj, field)
                        if str(type(obj))[:6] != "<class":
                            result = obj
                            break
                    if result == "" and obj:
                        value = obj
                    if str(result) != 'False' and result is not None:
                        value = result
                except Exception:
                    value = ""
            else:
                is_valore = True
                value = chiave.valore
            chiave_vals = {
                "pratica_id": pratica.id,
                "chiave": key,
                "descrizione": descrizione,
                "valore": value,
                "is_valore": is_valore,
                "priority": chiave.priority
            }
            cp_model.create(chiave_vals)
        # valori per proprietari e armatori
        self._compute_prop_arm(pratica.partner_id.armatore_ids, 'pratica_armatore_id', pratica.id)
        self._compute_prop_arm(pratica.partner_id.proprietario_ids, 'pratica_proprietario_id', pratica.id)
        self._compute_prop_arm(pratica.partner_id.rappresentante_ruolo_ids, 'pratica_rappresentante_id', pratica.id,
                               prop_arm=False)
        # inizializzo i reports
        for doc in tpl.document_ids:
            rp = ir_model.search([('report_name', '=', str(doc.id) + "_" + str(tpl.id) + "_tpl_report")], limit=1)
            if rp:
                rp_vals = {
                    'pratica_id': pratica.id,
                    'report_id': rp.id,
                    'priority': doc.priority
                }
                rp_model.create(rp_vals)
        # SETTO IL PARSER CORRETTO
        for report in pratica.report_ids:
            report.report_id.write({'parser_loc': 'ey2/report/pratica_nave_parser.py'})
        # ATTIVITÀ DI SISTEMA CREATA PRATICA
        as_vals = {
            'pratica_id': pratica.id,
            'descrizione': "Creata pratica in stato " + pratica.state.split("-")[1]
        }
        self.env['ey2.att_sistema_pratica'].create(as_vals)
        #PRATICHE COLLEGATE
        if 'pratiche_collegate' in vals:
            for pc in pratica.pratiche_collegate:
                query = "INSERT INTO ey2_pratiche_collegate_rel (pratica1_id, pratica2_id) VALUES (" + str(pc.id) + ", " + str(pratica.id) + ")"
                self.env.cr.execute(query)
        return pratica

    @api.multi
    def write(self, vals):
        for p in self:
            #pratiche collegate
            if 'pratiche_collegate' in vals:
                pc_copy = []
                for pc_id in vals['pratiche_collegate'][0][2]:
                    pc_copy.append(pc_id)
                for pc in p.pratiche_collegate:
                    if pc.id in pc_copy:
                        pc_copy.remove(pc.id)
                        continue
                    else:
                        query = "DELETE FROM ey2_pratiche_collegate_rel WHERE pratica1_id=" + str(pc.id) + " AND pratica2_id=" + str(p.id)
                        self.env.cr.execute(query)
                for pc_id in pc_copy:
                    query = "INSERT INTO ey2_pratiche_collegate_rel (pratica1_id, pratica2_id) VALUES (" + str(pc_id) + ", " + str(p.id) + ")"
                    self.env.cr.execute(query)
            # passaggio di stato in attività di sistema
            if 'state' in vals and vals['state'] != p.state:
                state_before = p.state.split("-")[1]
                state_after = vals['state'].split("-")[1]
                descr = "Passaggio da " + state_before + " a " + state_after
                as_vals = {
                    'pratica_id': p.id,
                    'descrizione': descr
                }
                if state_after == 'Alert':
                    as_vals['operatore_id'] = self.env.context['operatore_id']
                self.env['ey2.att_sistema_pratica'].create(as_vals)
        return super(PraticaNave, self).write(vals)

    @api.multi
    def unlink(self):
        for p in self:
            #pratiche collegate
            for pc in p.pratiche_collegate:
                query = "DELETE FROM ey2_pratiche_collegate_rel WHERE pratica1_id=" + str(pc.id) + " AND pratica2_id=" + str(p.id)
                self.env.cr.execute(query)
        return super(PraticaNave, self).unlink()

    ################ SCHEDULER ALERT
    @api.model
    def scheduler_alert_pratica(self):
        today = datetime.now()
        pratiche = self.search([])
        for pratica in pratiche:
            if pratica.state != 'a-Alert':
                for alert in pratica.alert_ids:
                    if alert.attivo:
                        alert_date = datetime.strptime(alert.data, '%Y-%m-%d')
                        if today >= alert_date:
                            pratica.with_context({'operatore_id': alert.operatore_id.id}).write({'state': 'a-Alert'})


##############################################################################
## PRATICA SOGGETTO ##########################################################
##############################################################################
class PraticaSoggetto(models.Model):
    _name = "ey2.pratica_soggetto"
    _inherit = "config_tpl.pratica"
    _order = "state asc, data_pratica desc"

    ##### FUNZIONI PER IL CAMBIAMENTO DI STATO
    @api.multi
    def stato_preventivo(self):
        return self.write({'state': 'c-Preventivo'})

    @api.multi
    def stato_in_corso(self):
        return self.write({'state': 'h-In corso'})

    @api.multi
    def stato_da_fatturare(self):
        return self.write({'state': 'p-Da fatturare'})

    @api.multi
    def stato_fatturata(self):
        return self.write({'state': 's-Fatturata'})

    @api.multi
    def stato_pagata(self):
        return self.write({'state': 'v-Pagata'})

    @api.multi
    def stato_sospesa(self):
        return self.write({'state': 'x-Sospesa'})

    @api.multi
    def stato_annullata(self):
        return self.write({'state': 'z-Annullata'})

    _STATO_PRATICA = [
        ("c-Preventivo", "Preventivo"),
        ("h-In corso", "In corso"),
        ("p-Da fatturare", "Da fatturare"),
        ("s-Fatturata", "Fatturata"),
        ("v-Pagata", "Pagata"),
        ("x-Sospesa", "Sospesa"),
        ("z-Annullata", "Annullata"),
        ("a-Alert", "Alert")
    ]

    # utility
    def _get_address(self, partner):
        """
        funzione che restituisce un dict coi vals da congelare in armatore e proprietario
        :param partner: obj il partner da cui prendere l'indirizzo
        :return:
        """
        address_vals = {}
        if partner.street:
            address_vals['street'] = partner.street
        if partner.street2:
            address_vals['street2'] = partner.street2
        if partner.city:
            address_vals['city'] = partner.city
        if partner.state_id:
            address_vals['state'] = partner.state_id.code
        if partner.zip:
            address_vals['zip'] = partner.zip
        if partner.country_id:
            address_vals['country'] = partner.country_id.name
        indirizzo = self.env['ey2.indirizzo_partner'].create(address_vals)
        return indirizzo.id

    @api.depends('att_operatore_ids', 'att_operatore_ids.descrizione', 'att_operatore_ids.data')
    def _compute_ultima_attivita(self):
        for pratica in self:
            date = "1970-01-01"
            descr = ""
            for att in pratica.att_operatore_ids:
                if att.data > date:
                    date = att.data
                    descr = att.descrizione
            if len(descr) > 255:
                descr = descr[:252] + "..."
            pratica.ultima_attivita = descr

    @api.one
    def compute_prop_arm(self, obj, field, pratica_id, ruolo=False):
        """
        Funzione che aggiorna la lista degli armatori o dei proprietari
        :param obj_list: list lista degli armatori/proprietari della nave
        :param field: string 'pratica_proprietario_id' o 'pratica_armatore_id'
        :param pratica_id: integer id della pratica
        :param prop_arm: Boolean False se si crea un rappresentante
        :return:
        """
        model = self.env['ey2.prop_arm_pratica']
        # field_partner = "partner_id"
        # if not prop_arm:
        #    field_partner = "rappresentante_id"
        partner = obj
        stato_civile = ""
        if partner.stato_civile:
            stato_civile = partner.stato_civile.name
        # solo se il proprietario/armatore è attivo
        vals = {
            field: pratica_id,
            'cognome': partner.cognome,
            'nome': partner.nome,
            'partner_id': partner.id,
            'stato_civile': stato_civile,
            'indirizzo_id': self._get_address(partner),
            'identificatore': "",
            'fiscalcode': partner.fiscalcode
        }
        if ruolo:
            vals['ruolo'] = ruolo
        model.create(vals)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        if self.partner_id and self.partner_id.blacklist:
            raise ValidationError("Errore di inserimento. Contattare amministratore")

    @api.one
    @api.constrains('partner_id')
    def _validate_fields(self, context=None):
        if self.partner_id and self.partner_id.blacklist:
            raise ValidationError("Errore di inserimento. Contattare amministratore")

    name = fields.Char(string="Nome pratica", index=True, required=True, store=True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Soggetto", required=True, index=True)
    tipo_documento_id = fields.Many2one("ey.tipo_documento", string="Tipo documento soggetto", index=True)
    report_ids = fields.One2many("ey2.report_pratica_nave", "pratica_soggetto_id", string="Reports", ondelete="cascade")
    chiave_ids = fields.One2many("ey2.chiave_pratica_nave", "pratica_soggetto_id", string="Chiavi", ondelete="cascade")
    ente_ids = fields.One2many("ey2.ente_pratica", "pratica_soggetto_id", string="Enti")
    tipo_pratica = fields.Char(string="Tipo pratica", index=True)
    data_pratica = fields.Date(string="Data apertura", index=True, required=True,
                               default=lambda *a: time.strftime('%Y-%m-%d'))
    #campi da congelare sicuramente
    cognome_soggetto = fields.Char(string="Cognome soggetto")
    nome_soggetto = fields.Char(string="Nome soggetto")
    cf_soggetto = fields.Char(string="Codice fiscale soggetto")
    indirizzo_soggetto_id = fields.Many2one("ey2.indirizzo_partner", string="Indirizzo soggetto")
    stato_civile_soggetto = fields.Char(string="Stato civile soggetto")
    cittadinanza_soggetto = fields.Char(string="Cittadinanza soggetto")
    tipo_documento_soggetto = fields.Char(string="Tipo documento soggetto")
    numero_documento_soggetto = fields.Char(string="Numero documento soggetto")
    rilascio_documento_soggetto = fields.Char(string="Uff. rilascio documento soggetto")
    luogo_rilascio_documento_soggetto = fields.Char(string="Luogo rilascio documento soggetto")
    categoria_documento_soggetto = fields.Char(string="Categoria documento soggetto")
    documento_soggetto_id = fields.Many2one("ey.documento", string="Documento soggetto")
    #altri dati
    state = fields.Selection(_STATO_PRATICA, string="Stato pratica", index=True, required=True,
                             default="h-In corso", track_visibility='onchange')
    user_id = fields.Many2one("res.users", string="Responsabile", index=True, required=True,
                              default=lambda self: self.env.user)
    riferimento_pratica = fields.Char(string="Riferimento pratica", index=True)
    # soggetto per fatturazione
    soggetto_fatturazione_id = fields.Many2one("res.partner", string="Soggetto fatturazione")
    #allegati
    info_operatore = fields.Text(string="Info operatore")
    allegati = fields.Many2many(comodel_name="config_tpl.allegato_tpl", relation="pratica_soggetto_allegato_model",
                                string="Allegati", index=True)
    # attività di sistema
    att_sistema_ids = fields.One2many("ey2.att_sistema_pratica", "pratica_soggetto_id", string=u"Attività di sistema")
    # attività operatore
    ultima_attivita = fields.Char(string=u"Ultima attività", compute="_compute_ultima_attivita")
    att_operatore_ids = fields.One2many("ey2.att_operatore_pratica", "pratica_soggetto_id", string=u"Attività operatore")
    # contatti pratica
    contatto_pratica_ids = fields.One2many("ey2.contatto_pratica_nave", 'pratica_soggetto_id', string="Contatti")
    # documenti
    documenti_pratica_ids = fields.One2many("ey2.allegato_pratica", "pratica_soggetto_id", string="Documenti pratica")
    # follow up
    follow_up_ids = fields.One2many("ey2.follow_up_pratica", "pratica_soggetto_id", string="Follow up")
    # alerts
    alert_ids = fields.One2many("ey2.alert_pratica_nave", "pratica_soggetto_id", string="Alerts")
    # pratiche collegate
    pratiche_collegate = fields.Many2many(comodel_name="ey2.pratica_soggetto", relation="ey2_pratiche_s_collegate_rel",
                                          column1="pratica1_id", column2="pratica2_id", string="Pratiche collegate",
                                          index=True)
    #altri soggetti
    rappresentante_ids = fields.One2many("ey2.prop_arm_pratica", "pratica_soggetto_id", string="Altri soggetti")

    @api.model
    def create(self, vals):
        vals['created'] = True
        name = ""
        if vals['tpl_id']:
            name += self.env['config_tpl.tpl'].browse([vals['tpl_id']])[0].name
        if vals['partner_id']:
            name += " - " + self.env['res.partner'].browse([vals['partner_id']])[0].name
        vals['name'] = name
        pratica = super(PraticaSoggetto, self).create(vals)
        # sequenza
        domain_sequence = [
            ("code", '=', "ey2_riferimento_pratica"),
        ]
        sequence = self.env['ir.sequence'].search(domain_sequence, limit=1)
        next_code = self.env['ir.sequence'].next_by_id(sequence.id)
        pratica.write({'riferimento_pratica': next_code})
        # campi partner_riferimento
        doc_obj = None
        cognome_marittimo, nome_marittimo, cf_marittimo, indirizzo_marittimo = ("", "", "", "")
        cittadinanza_marittimo, stato_civile_marittimo = ("", "")
        if pratica.partner_id:
            cognome_marittimo = pratica.partner_id.cognome
            nome_marittimo = pratica.partner_id.nome
            cf_marittimo = pratica.partner_id.fiscalcode
            indirizzo_marittimo = self._get_address(pratica.partner_id)
            if pratica.partner_id.stato_civile:
                stato_civile_marittimo = pratica.partner_id.stato_civile.name
            if pratica.partner_id.nazionalita_id:
                cittadinanza_marittimo = pratica.partner_id.nazionalita_id.name
            # cerco il documento del marittomo
            if pratica.tipo_documento_id:
                max_date = ""
                for doc in pratica.partner_id.documento_ids:
                    if doc.tipo_id.name == pratica.tipo_documento_id.name:
                        scadenza = doc.data_scadenza or ""
                        if scadenza >= max_date:
                            doc_obj = doc
                            max_date = scadenza
                if not doc_obj:
                    raise ValidationError(
                        "Il soggetto in questione non ha un documento di tipo " + pratica.tipo_documento_id.name)
        campi_da_congelare = {
            'info_operatore': pratica.tpl_id.info_operatore,
            "tipo_pratica": pratica.tpl_id.tipo_pratica,
            "nome_nave": pratica.partner_id.name,
            "indirizzo_soggetto_id": indirizzo_marittimo,
            "stato_civile_soggetto": stato_civile_marittimo,
            "cittadinanza_soggetto": cittadinanza_marittimo,
            # marittimo_di_riferimento
            'cognome_soggetto': cognome_marittimo,
            'nome_soggetto': nome_marittimo,
            'cf_soggetto': cf_marittimo
        }
        if doc_obj:
            campi_da_congelare['tipo_documento_soggetto'] = doc_obj.tipo_id.name
            campi_da_congelare['numero_documento_soggetto'] = doc_obj.numero_documento or ""
            campi_da_congelare['rilascio_documento_soggetto'] = doc_obj.ufficio_id.name
            campi_da_congelare['categoria_documento_soggetto'] = doc_obj.categoria or ""
            campi_da_congelare['luogo_rilascio_documento_soggetto'] = doc_obj.luogo_rilascio or ""
            campi_da_congelare['documento_soggetto_id'] = doc_obj.id
        # scrivo gli allegati
        allegati_list = []
        for allegato in pratica.tpl_id.allegato_ids:
            allegati_list.append(allegato.id)
        if len(allegati_list) > 0:
            campi_da_congelare['allegati'] = [(6, 0, allegati_list)]
        pratica.write(campi_da_congelare)
        # PARTE IN CUI SETTO IL VALORE DELLE CHIAVI
        # models
        cp_model = self.env['ey2.chiave_pratica_nave']
        rp_model = self.env['ey2.report_pratica_nave']
        ir_model = self.env['ir.actions.report.xml']
        # inizializzo le chiavi
        tpl = pratica.tpl_id
        partner = pratica.partner_id
        for chiave in tpl.chiave_ids:
            key = chiave.chiave
            descrizione = chiave.descrizione
            if chiave.tipo_chiave == 'Campo':
                arr_value = key.split(".")
                result = ""
                value = ""
                is_valore = False
                obj = partner
                try:
                    for field in arr_value:
                        obj = getattr(obj, field)
                        if str(type(obj))[:6] != "<class":
                            result = obj
                            break
                    if result == "" and obj:
                        value = obj
                    if str(result) != 'False' and result is not None:
                        value = result
                except Exception:
                    value = ""
            else:
                is_valore = True
                value = chiave.valore
            chiave_vals = {
                "pratica_soggetto_id": pratica.id,
                "chiave": key,
                "descrizione": descrizione,
                "valore": value,
                "is_valore": is_valore,
                "priority": chiave.priority
            }
            cp_model.create(chiave_vals)
        # inizializzo i reports
        for doc in tpl.document_ids:
            rp = ir_model.search([('report_name', '=', str(doc.id) + "_" + str(tpl.id) + "_tpl_report")], limit=1)
            if rp:
                rp_vals = {
                    'pratica_soggetto_id': pratica.id,
                    'report_id': rp.id,
                    'priority': doc.priority
                }
                rp_model.create(rp_vals)
        # SETTO IL PARSER CORRETTO
        for report in pratica.report_ids:
            report.report_id.write({'parser_loc': 'ey2/report/pratica_soggetto_parser.py'})
        # ATTIVITÀ DI SISTEMA CREATA PRATICA
        as_vals = {
            'pratica_soggetto_id': pratica.id,
            'descrizione': "Creata pratica in stato " + pratica.state.split("-")[1]
        }
        self.env['ey2.att_sistema_pratica'].create(as_vals)
        # PRATICHE COLLEGATE
        if 'pratiche_collegate' in vals:
            for pc in pratica.pratiche_collegate:
                query = "INSERT INTO ey2_pratiche_s_collegate_rel (pratica1_id, pratica2_id) VALUES (" + str(pc.id) + ", " + str(pratica.id) + ")"
                self.env.cr.execute(query)
        return pratica

    @api.multi
    def write(self, vals):
        for p in self:
            # pratiche collegate
            if 'pratiche_collegate' in vals:
                pc_copy = []
                for pc_id in vals['pratiche_collegate'][0][2]:
                    pc_copy.append(pc_id)
                for pc in p.pratiche_collegate:
                    if pc.id in pc_copy:
                        pc_copy.remove(pc.id)
                        continue
                    else:
                        query = "DELETE FROM ey2_pratiche_s_collegate_rel WHERE pratica1_id=" + str(pc.id) + " AND pratica2_id=" + str(p.id)
                        self.env.cr.execute(query)
                for pc_id in pc_copy:
                    query = "INSERT INTO ey2_pratiche_s_collegate_rel (pratica1_id, pratica2_id) VALUES (" + str(pc_id) + ", " + str(p.id) + ")"
                    self.env.cr.execute(query)
            # passaggio di stato in attività di sistema
            if 'state' in vals and vals['state'] != p.state:
                state_before = p.state.split("-")[1]
                state_after = vals['state'].split("-")[1]
                descr = "Passaggio da " + state_before + " a " + state_after
                as_vals = {
                    'pratica_soggetto_id': p.id,
                    'descrizione': descr
                }
                if state_after == 'Alert':
                    as_vals['operatore_id'] = self.env.context['operatore_id']
                self.env['ey2.att_sistema_pratica'].create(as_vals)
        return super(PraticaSoggetto, self).write(vals)

    @api.multi
    def unlink(self):
        for p in self:
            # pratiche collegate
            for pc in p.pratiche_collegate:
                query = "DELETE FROM ey2_pratiche_s_collegate_rel WHERE pratica1_id=" + str(pc.id) + " AND pratica2_id=" + str(p.id)
                self.env.cr.execute(query)
        return super(PraticaSoggetto, self).unlink()

    ################ SCHEDULER ALERT
    @api.model
    def scheduler_alert_pratica(self):
        today = datetime.now()
        pratiche = self.search([])
        for pratica in pratiche:
            if pratica.state != 'a-Alert':
                for alert in pratica.alert_ids:
                    if alert.attivo:
                        alert_date = datetime.strptime(alert.data, '%Y-%m-%d')
                        if today >= alert_date:
                            pratica.with_context({'operatore_id': alert.operatore_id.id}).write({'state': 'a-Alert'})
