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

from openerp import fields, models, api
import time


##############################################################################
## FOLLOW UP #################################################################
##############################################################################
class FollowUpMarittimo(models.Model):
    _name = "ey2.follow_up_marittimo"

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
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'documento_follow_up_marittimo_' + str(self.id),
            'datas_fname': 'documento_follow_up_marittimo_' + str(self.id),
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
            if len(fu.descrizione) > 30:
                fu.prev_descrizione = fu.descrizione[:30] + "..."
            else:
                fu.prev_descrizione = fu.descrizione

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    partner_id = fields.Many2one("res.partner", index=True)
    data = fields.Date(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True)
    referente = fields.Char(string="Referente del contatto")
    oggetto = fields.Char(string="Oggetto")
    descrizione = fields.Text(string="Descrizione")
    prev_descrizione = fields.Char(string="Descrizione", compute="_compute_preview")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")


##############################################################################
## RES PARTNER ###############################################################
##############################################################################
class res_partner(models.Model):
    _inherit = "res.partner"

    armatore_proprietario = fields.Boolean(string="Armatore / Proprietario", index=True)
    altri_soggetti = fields.Boolean(string="Altri soggetti", index=True)
    follow_up_marittimo_ids = fields.One2many("ey2.follow_up_marittimo", "partner_id", string="Follw up")
    pec = fields.Char(string="PEC")
    # campi armatore
    codice_eori = fields.Char(string="Cod EORI")
    user_inps = fields.Char(string="User ID")
    pwd_inps = fields.Char(string="Password")
    cod_ditta_inail = fields.Char(string="Codice ditta")
    sede_inail = fields.Char(string="Sede")
    pin_inail = fields.Char(string="PIN")
    cod_ditta_fanimar = fields.Char(string="Codice ditta")
    pwd_fanimar = fields.Char(string="Password")
    altre_note = fields.Text(strint="Note")
    # navi - pratiche imbarchi o sbarchi
    imbarco_sbarco_ids = fields.One2many("ey2.pratica_nave", 'partner_riferimento_id', string="Imbarchi/Sbarchi",
                                         domain=[('tipo_pratica', 'in', ['Imbarco', 'Sbarco'])])
    # navi - altre pratiche
    altra_pratica_ids = fields.One2many("ey2.pratica_nave", 'partner_riferimento_id', string="Altre pratiche",
                                        domain=[('tipo_pratica', 'not in', ['Imbarco', 'Sbarco'])])
    # soggetti - pratiche_in_corso
    pratica_soggetto_attiva_ids = fields.One2many("ey2.pratica_soggetto", 'partner_id', string="Pratiche attive",
                                                  domain=[('state',
                                                           'in',
                                                           ['c-Preventivo', 'h-In corso', 'p-Da fatturare', 'a-Alert', 's-Fatturata'])])
    # soggetti - pratiche esaurite
    pratica_soggetto_ferma_ids = fields.One2many("ey2.pratica_soggetto", 'partner_id', string="Pratiche concluse",
                                                 domain=[('state',
                                                          'in',
                                                          ['v-Pagata', 'x-Sospesa', 'z-Annullata'])])
    # adempimenti
    adempimenti = fields.Many2many(comodel_name="ey2.adempimento_marittimo", relation="ey2_marittimo_adempimenti_rel",
                                   string="Adempimenti", index=True)
    # rappresentante
    rappresentante_ruolo_ids = fields.One2many("ey2.rappresentante_ruolo", "partner_id", string="Rappresentanti")
    # override contatti extra
    contatto_extra_ids = fields.One2many("ey2.contatto_pratica_nave", "partner_id", string="Contatti")
    #navi da visualizzare per proprietario armatore
    nave_arm_prop_ids = fields.One2many("ey2.proprietario_armatore", "partner_id", string="Navi", domain=[('riferimento', '=', True)])
