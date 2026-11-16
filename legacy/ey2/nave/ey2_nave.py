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


##############################################################################
## RAPPRESENTANTE ARMATORE####################################################
##############################################################################
class RuoloRappresentante(models.Model):
    _name = "ey2.ruolo_rappresentante"

    name = fields.Char(string="Ruolo", required=True, index=True)


class RappresentanteArmatore(models.Model):
    _name = "ey2.rappresentante_armatore"
    _rec_name = "rec_name"

    @api.depends('cognome', 'nome', 'fiscalcode')
    def _compute_rec_name(self):
        for ra in self:
            rec_name = ""
            if ra.cognome and ra.nome:
                rec_name = ra.cognome + " " + ra.nome
                if ra.fiscalcode:
                    rec_name += " - " + ra.fiscalcode
            ra.rec_name = rec_name

    rec_name = fields.Char(string="Cognome e nome", compute="_compute_rec_name", index=True, store=True)
    cognome = fields.Char(string="Cognome", index=True, required=True)
    nome = fields.Char(string="Nome", index=True, required=True)
    luogo_nascita_id = fields.Many2one("ey.luogo_nascita", string='Luogo di nascita', index=True)
    data_nascita = fields.Date(string="Data di nascita (gg/mm/aaaa)", index=True)
    cittadinanza_id = fields.Many2one("res.country", string="Cittadinanza", index=True)
    stato_civile = fields.Many2one("ey.stato_civile", string="Stato civile")
    telefono = fields.Char(string="Telefono")
    email = fields.Char(string="Email")
    fiscalcode = fields.Char(string="Cod. Fiscale", index=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    zip = fields.Char(string='CAP', size=24)
    city = fields.Char(string='City')
    state_id = fields.Many2one("res.country.state", string='Provincia/Stato', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Nazione', ondelete='restrict')

    _sql_constraints = [
        ('fiscalcode_uniq', 'UNIQUE (fiscalcode)', u'Esiste già un rappresentante con questo codice fiscale!')
    ]


class RappresentanteRuolo(models.Model):
    _name = "ey2.rappresentante_ruolo"

    nave_id = fields.Many2one("ey.unita", index=True)
    partner_id = fields.Many2one("res.partner", index=True)
    rappresentante_id = fields.Many2one("res.partner", string="Cognome e nome (RS)", required=True,
                                        index=True)
    ruolo_id = fields.Many2one("ey2.ruolo_rappresentante", string="Ruolo", required=True)
    identificatore = fields.Char(string="Identificatore", index=True)
    testo_descrittivo = fields.Char(string="Descr.")
    riferimento = fields.Boolean(string="Attivo", index=True, default=True)


##############################################################################
## UTILITIES PER MANY2ONE DA NAVE ############################################
##############################################################################
class Porto(models.Model):
    _name = "ey2.porto"

    name = fields.Char(string="Porto", index=True, required=True)


class TipoRegistroUnita(models.Model):
    _name = "ey2.tipo_registro_unita"

    name = fields.Char(string="Tipo registro", index=True, required=True)


class SocietaConcessionaria(models.Model):
    _name = "ey2.societa_concessionaria"

    name = fields.Char(string=u"Società", index=True, required=True)


class TipoCanoneRai(models.Model):
    _name = "ey2.tipo_canone_rai"

    name = fields.Char(string="Tipo canone", index=True, required=True)


class LimiteNavigazione(models.Model):
    _name = "ey2.limite_navigazione"

    name = fields.Char(string="Limite", index=True, reuqired=True)


class EnteSorveglianza(models.Model):
    _name = "ey2.ente_sorveglianza"

    name = fields.Char(string="Ente", index=True, reuqired=True)


class Costruttore(models.Model):
    _name = "ey2.costruttore"

    name = fields.Char(string="Nome", index=True, reuqired=True)


class MaterialeCostruzione(models.Model):
    _name = "ey2.materiale_costruzione"

    name = fields.Char(string="Nome", index=True, reuqired=True)


class Propulsione(models.Model):
    _name = "ey2.propulsione"

    name = fields.Char(string="Propulsione", index=True, reuqired=True)


##############################################################################
## PROCEDURA LEGALE ##########################################################
##############################################################################
class ProceduraLegale(models.Model):
    _name = "ey2.procedura_legale"

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
        cr = self._cr
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'allegato_procedura_' + str(self.id),
            'datas_fname': 'allegato_procedura_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    _TIPO_PROCEDURA = [
        ("Arrivo / Partenza", "Arrivo / Partenza"),
        ("Notifica garbage", "Notifia garbage"),
        ("Manifesto doganale", "Manifesto doganale"),
        ("Collaudo radio", "Collaudo radio"),
        ("Ispezione radio", "Ispezione audio"),
        ("Ispezione sanitaria", "Ispezione sanitaria"),
        ("Ispezione di sicurezza", "Ispezione di sicurezza")
    ]

    _PERIODICITA = [
        ("Variabile", "Variabile"),
        ("Semestrale", "Semestrale"),
        ("Annuale", "Annuale"),
        ("Biennale", "Biennale"),
        ("Triennale", "Triennale"),
        ("Quadriennale", "Quadriennale"),
        ("Mai", "Mai")
    ]

    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_procedura = fields.Selection(_TIPO_PROCEDURA, string="Tipo procedura", index=True, required=True)
    periodicita = fields.Selection(_PERIODICITA, string=u"Periodicità", index=True, required=True)
    operatore = fields.Char(string="Operatore", index=True) # @todo: è interno? Se si, many2one al res.users?!?
    data_effettuazione = fields.Date(string="Data effettuazione", required=True)
    data_scadenza = fields.Date(string="Data scadenza", required=True)
    giorni_preavviso = fields.Integer(string="Preavviso (in giorni)", required=True) # @todo: mettere alla create, all'unlink e alla write il collegamento con la scadenza? Scadenze come devono essere rispetto ai corsi?
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")


##############################################################################
## PROPRIETARIO ARMATORE #####################################################
##############################################################################
class ProprietarioArmatore(models.Model):
    _name = "ey2.proprietario_armatore"
    _order = "riferimento desc"

    @api.depends('nave_proprietario_id', 'nave_armatore_id')
    def _compute_for_partner_view(self):
        for rec in self:
            nave = None
            if rec.nave_proprietario_id:
                rec.armatore_proprietario = "Proprietario"
                nave = rec.nave_proprietario_id
            elif rec.nave_armatore_id:
                rec.armatore_proprietario = "Armatore"
                nave = rec.nave_armatore_id
            if nave:
                rec.nave_name = nave.name
                rec.nave_tipo_registro = nave.tipo_registro_id.name
                rec.nave_nr_on = nave.nr_on
                rec.nave_porto = nave.porto_id.name
                rec.nave_bandiera = nave.bandiera_id.name
                if nave.iva_id:
                    rec.nave_iva = nave.iva_id.description

    nave_proprietario_id = fields.Many2one("ey.unita", index=True)
    nave_armatore_id = fields.Many2one("ey.unita", index=True)
    partner_id = fields.Many2one("res.partner", string="Cognome e nome/Rag. sociale", index=True, required=True)
    identificatore = fields.Char(string="Identificatore", index=True)
    data_inizio = fields.Date(string="Inizio", required=True)
    data_fine = fields.Date(string="Fine")
    carati = fields.Char(string="Carati")
    riferimento = fields.Boolean(string="Attivo", index=True)
    #campi funzione non storati
    armatore_proprietario = fields.Char(string="Armatore/Proprietario", compute="_compute_for_partner_view")
    nave_name = fields.Char(string="Nave", compute="_compute_for_partner_view")
    nave_tipo_registro = fields.Char(string="Tipo registro", compute="_compute_for_partner_view")
    nave_nr_on = fields.Char(string="Nr. / O.N.", compute="_compute_for_partner_view")
    nave_porto = fields.Char(string="Porto di iscrizione", compute="_compute_for_partner_view")
    nave_bandiera = fields.Char(string="Bandiera", compute="_compute_for_partner_view")
    nave_iva = fields.Char(string="Dati amministrativi", compute="_compute_for_partner_view")


##############################################################################
## CERTIFICATO DI BORDO ######################################################
##############################################################################
class TipoCertBordo(models.Model):
    _name = "ey2.tipo_cert_bordo"

    name = fields.Char(string="Tipo", index=True, reuqired=True)


class CertificatoBordo(models.Model):
    _name = "ey2.certificato_bordo"

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
            'name': 'documento_certificato_bordo_' + str(self.id),
            'datas_fname': 'documento_certificato_bordo_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_id = fields.Many2one("ey2.tipo_cert_bordo", string="Tipo certificato", index=True, required=True)
    #ente_id = fields.Many2one("ey.ente_documenti", string="Ente", required=True)
    luogo_rilascio = fields.Char(string="Luogo rilascio", index=True)
    data_rilascio = fields.Date(string="Data rilascio", required=True)
    data_scadenza = fields.Date(string="Data scadenza", required=True)
    data_preavviso = fields.Date(string="Data preavviso", required=True)
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")
    #modifiche del 19/09/2019
    identificatore = fields.Char(string="Identificatore")
    numero_documento = fields.Char(string="Nr documento")
    ente_id = fields.Many2one("ey2.ente_sorveglianza", string="Ente", index=True)
    #modifiche 13/11/2019
    attivo = fields.Boolean(string="Attivo", default=True)

    ###COLLEGAMENTO ALL'AGENDA SCADENZE NAVI
    @api.model
    def create(self, vals):
        certificato = super(CertificatoBordo, self).create(vals)
        categoria_ca = self.env['ey2.categoria_agenda_nave'].search([('name', '=', 'Scadenza Certificato Nave')],
                                                                    limit=1)
        agenda_vals = {
            'name': certificato.nave_id.name + " - " + certificato.tipo_id.name,
            'categoria_id': categoria_ca.id,
            'uniq_id': 'certificato_bordo' + "-" + str(certificato.id),
            'data_scadenza': certificato.data_scadenza,
            'data_alert': certificato.data_preavviso
        }
        self.env['ey2.agenda_nave'].create(agenda_vals)
        return certificato

    @api.multi
    def unlink(self):
        for rec in self:
            # cancello anche le scadenze agenda associate
            scadenza = self.env['ey2.agenda_nave'].search([('uniq_id', '=', 'certificato_bordo' + "-" + str(rec.id))])
            if scadenza:
                scadenza.unlink()
        return super(CertificatoBordo, self).unlink()

    @api.multi
    def write(self, vals):
        scadenze_result = super(CertificatoBordo, self).write(vals)
        for rec in self:
            if 'data_preavviso' in vals or 'data_scadenza' in vals or 'tipo_id' in vals:
                # faccio il calcolo
                scadenza = self.env['ey2.agenda_nave'].search([('uniq_id', '=', 'certificato_bordo' + "-" + str(rec.id))])
                if not scadenza:
                    categoria_ca = self.env['ey2.categoria_agenda_nave'].search([('name', '=',
                                                                                  'Scadenza Certificato Nave')], limit=1)
                    agenda_vals = {
                        'name': rec.nave_id.name + " - " + rec.tipo_id.name,
                        'categoria_id': categoria_ca.id,
                        'uniq_id': 'task' + "-" + str(rec.id),
                        'data_scadenza': rec.data_scadenza,
                        'data_alert': rec.data_preavviso
                    }
                    scadenza = self.env['ey2.agenda_nave'].create(agenda_vals)

                scadenza_vals = {}
                if 'tipo_id' in vals:
                    tipo = self.env['ey2.tipo_cert_bordo'].search([('id', '=', vals['tipo_id'])], limit=1)
                    scadenza_vals['name'] = rec.nave_id.name + " - " + tipo.name
                if 'data_scadenza' in vals:
                    scadenza_vals['data_scadenza'] = vals['data_scadenza']
                if 'data_preavviso' in vals:
                    scadenza_vals['data_alert'] = vals['data_preavviso']
                scadenza.write(scadenza_vals)
        return scadenze_result


##############################################################################
## APPARATO ELETTRONICO ######################################################
##############################################################################
class TipoAppElett(models.Model):
    _name = "ey2.tipo_app_elett"

    name = fields.Char(string="Apparato", index=True, reuqired=True)


class MarcaAppElett(models.Model):
    _name = "ey2.marca_app_elett"

    name = fields.Char(string="Marca", index=True, reuqired=True)


class CategAppElett(models.Model):
    _name = "ey2.categ_app_elett"

    name = fields.Char(string="Categoria", index=True, reuqired=True)


class ApparatoElettronico(models.Model):
    _name = "ey2.apparato_elettronico"

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
            'name': 'documento_apparato_elettronico_' + str(self.id),
            'datas_fname': 'documento_apparato_elettronico_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_id = fields.Many2one("ey2.tipo_app_elett", string="Apparato", index=True, required=True)
    marca_id = fields.Many2one("ey2.marca_app_elett", string="Marca", index=True, required=True)
    modello = fields.Char(string="Modello")
    caratteristiche = fields.Char(string="Caratteristiche")
    categoria_id = fields.Many2one("ey2.apparato_elettronico", string="Categoria")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")


##############################################################################
## ALLOGGI ###################################################################
##############################################################################
class TipoAlloggio(models.Model):
    _name = "ey2.tipo_alloggio"

    name = fields.Char(string="Tipo", index=True, reuqired=True)


class LettoAlloggio(models.Model):
    _name = "ey2.letto_alloggio"

    name = fields.Char(string="Letti", index=True, reuqired=True)


class Alloggio(models.Model):
    _name = "ey2.alloggio"

    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_id = fields.Many2one("ey2.tipo_alloggio", string="Tipo alloggio")
    letto_id = fields.Many2one("ey2.letto_alloggio", string="Letti")
    bagno = fields.Boolean(string="Bagno riservato")
    tv = fields.Boolean(string="TV")
    wifi = fields.Boolean(string="WiFi")
    note = fields.Text(string="Note")


##############################################################################
## RECAPITI E CONTATTI #######################################################
##############################################################################
class TipoRecapito(models.Model):
    _name = "ey2.tipo_recapito"

    name = fields.Char(string="Tipo", index=True, reuqired=True)


class TipoContatto(models.Model):
    _name = "ey2.tipo_contatto"

    name = fields.Char(string="Tipo", index=True, reuqired=True)


class UlterioreRecapito(models.Model):
    _name = "ey2.ulteriore_recapito"

    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_id = fields.Many2one("ey2.tipo_recapito", string="Tipo recapito")
    indirizzo = fields.Char(string="Indirizzo", required=True)
    city = fields.Char(string=u"Città", size=50)
    zip = fields.Char(string="CAP", size=5)
    provincia = fields.Char(string="Provincia", size=25)


class ContattoNave(models.Model):
    _name = "ey2.contatto_nave"

    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_id = fields.Many2one("ey2.tipo_contatto", string="Ruolo")
    name = fields.Char(string="Nome", required=True)
    phone = fields.Char(string="Telefono", size=50)
    fax = fields.Char(string="Fax", size=50)
    email = fields.Char(string="Email", size=100)


##############################################################################
## PERIODO FATTURAZIONE ######################################################
##############################################################################
class PriodoFatturazioneNave(models.Model):
    _name = "ey2.periodo_fatturazione_nave"

    name = fields.Char(string="Nome", index=True, reuqired=True)


##############################################################################
## EQUIPAGGIAMENTI NAVE ######################################################
##############################################################################
class TipoEquipaggiamentoNave(models.Model):
    _name = "ey2.tipo_equip_nave"

    name = fields.Char(string="Apparato", index=True, reuqired=True)


class MarcaEquipaggiamentoNave(models.Model):
    _name = "ey2.marca_equip_nave"

    name = fields.Char(string="Marca", index=True, reuqired=True)


class CategEquipaggiamentoNave(models.Model):
    _name = "ey2.categ_equip_nave"

    name = fields.Char(string="Categoria", index=True, reuqired=True)


class EquipaggiamentoNave(models.Model):
    _name = "ey2.equipaggiamento_nave"

    nave_id = fields.Many2one("ey.unita", index=True)
    tipo_id = fields.Many2one("ey2.tipo_equip_nave", string="Apparato", index=True, required=True)
    marca_id = fields.Many2one("ey2.marca_equip_nave", string="Marca", index=True, required=True)
    modello = fields.Char(string="Modello")
    caratteristiche = fields.Char(string="Caratteristiche")
    categoria_id = fields.Many2one("ey2.categ_equip_nave", string="Categoria")


##############################################################################
## IMMAGINE NAVE #############################################################
##############################################################################
class ImmagineNave(models.Model):
    _name = "ey2.immagine_nave"
    _rec_name = "descrizione"

    ##### FUNZIONI PER IL SET E IL GET DEL BINARY
    @api.multi
    def _get_immagine(self):
        ids = []
        for rec in self:
            ids.append(rec.id)
        ir_attachment_model = self.env['ir.attachment']
        domain_attachment = [('res_model', '=', self._name), ('res_id', 'in', ids)]
        attachments = ir_attachment_model.search(domain_attachment)
        for att in attachments:
            for rec in self:
                if rec.id == att.res_id:
                    rec.image = att.datas
                    break

    @api.one
    def _set_immagine(self):
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'ey2_nave_img_' + str(self.id),
            'datas_fname': 'ey2_nave_img_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.image
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    ##### CAMPI TABELLA
    nave_id = fields.Many2one("ey.unita", string="House", index=True)
    image = fields.Binary(compute="_get_immagine", inverse="_set_immagine", string="Immagine")
    image_fname = fields.Char(string="File name")
    descrizione = fields.Char(string="Descrizione", required=True)


##############################################################################
## MOTORE NAVE ###############################################################
##############################################################################
class MarcaMotoreNave(models.Model):
    _name = "ey2.marca_motore_nave"

    name = fields.Char(string="Marca", index=True, reuqired=True)


class MotoreNave(models.Model):
    _name = "ey2.motore_nave"

    nave_id = fields.Many2one("ey.unita", index=True)
    #marca_id = fields.Many2one("ey2.marca_motore_nave", string="Marca", index=True, required=True)
    modello = fields.Char(string="Modello")
    numero_serie = fields.Char(string="Numero di serie", index=True)
    anno_costr = fields.Integer(string="Anno fabbr.", index=True)


##############################################################################
## FOLLOW UP #################################################################
##############################################################################
class FollowUpGestNave(models.Model):
    _name = "ey2.follow_up_gest_nave"

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
            'name': 'documento_follow_up_gest_' + str(self.id),
            'datas_fname': 'documento_follow_up_gest_' + str(self.id),
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
            fu.prev_descrizione = fu.descrizione[:30] + "..."

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    nave_id = fields.Many2one("ey.unita", index=True)
    data = fields.Date(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True)
    referente = fields.Char(string="Referente del contatto")
    oggetto = fields.Char(string="Oggetto")
    descrizione = fields.Text(string="Descrizione")
    prev_descrizione = fields.Char(string="Descrizione", compute="_compute_preview")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")


class FollowUpMedNave(models.Model):
    _name = "ey2.follow_up_med_nave"

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
            'name': 'documento_follow_up_med_' + str(self.id),
            'datas_fname': 'documento_follow_up_med_' + str(self.id),
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
            fu.prev_descrizione = fu.descrizione[:30] + "..."

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    nave_id = fields.Many2one("ey.unita", index=True)
    data = fields.Date(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True)
    referente = fields.Char(string="Referente del contatto")
    oggetto = fields.Char(string="Oggetto")
    descrizione = fields.Text(string="Descrizione")
    prev_descrizione = fields.Char(string="Descrizione", compute="_compute_preview")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Allegato")
    document_fname = fields.Char(string="File name")


##############################################################################
## UTILIZZO NAVE #############################################################
##############################################################################
class UtilizzoNave(models.Model):
    _name = "ey2.utilizzo_nave"

    name = fields.Char(string="Utilizzo", index=True, reuqired=True)


##############################################################################
## ABBR TIPO NAVE ############################################################
##############################################################################
class AbbrTipoNave(models.Model):
    _name = "ey2.abbr_tipo_nave"

    name = fields.Char(string="Nome", index=True, reuqired=True)


##############################################################################
## STORICI NAVE ############################################################
##############################################################################
class StoricoNave(models.Model):
    _name = "ey2.storico_nave"

    nave_id = fields.Many2one("ey.unita", index=True)
    nome = fields.Char(string="Nome", index=True)
    porto_id = fields.Many2one("ey2.porto", string="Porto di iscrizione", index=True)
    nr_on = fields.Char(string="Nr. / O.N.", index=True)
    bandiera_id = fields.Many2one("res.country", string="Bandiera", index=True)
    data_inizio = fields.Date(string="Inizio")
    data_fine = fields.Date(string="Fine")


##############################################################################
## UNITÀ NAVALE ##############################################################
##############################################################################
class Unita(models.Model):
    _inherit = "ey.unita"

    _INFO_DOVUTE = [
        ("Si", "Si"),
        ("No", "No"),
        ("Non dovute", "Non dovute")
    ]

    #####info generali
    riferimento = fields.Char(string="Riferimento", index=True)
    gestione_continuativa = fields.Boolean(string="Gestione continuativa", index=True)
    bandiera_id = fields.Many2one("res.country", string="Bandiera", index=True, required=True)
    porto_id = fields.Many2one("ey2.porto", string="Porto di iscrizione", index=True, required=True)
    nr_on = fields.Char(string="Nr. / O.N.", index=True)
    tipo_registro_id = fields.Many2one("ey2.tipo_registro_unita", string="Tipo registro", index=True, required=True)
    utilizzo_id = fields.Many2one("ey2.utilizzo_nave", string="Utilizzo", index=True, required=True)
    imo_nr = fields.Char(string="IMO Nr.", index=True)
    nominativo_interno = fields.Char("Nominativo internazionale", index=True)
    mmsi = fields.Char(string="MMSI", index=True)
    hin_cin = fields.Char(string="HIN / CIN", index=True)
    lunghezza = fields.Float(string="Lunghezza f.t. mt.", required=True, index=True)
    lunghezza_galleggiamento = fields.Float("Lunghezza al galleggiam.mt.")
    lunghezza_mt = fields.Float(string="Larghezza mt.")
    pescaggio = fields.Float(string="Pescaggio mt.")
    stazza_lorda = fields.Float(string="Stazza lorda")
    stazza_netta = fields.Float(string="Stazza netta")
    dislocamento = fields.Float(string="Dislocamento")
    limite_navigazione_id = fields.Many2one("ey2.limite_navigazione", string="Limiti di Navigazione", index=True)
    epirb = fields.Boolean(string="EPIRB", index=True)
    abbr_tipo_id = fields.Many2one("ey2.abbr_tipo_nave", string="Abbr. tipo", index=True)
    portata_max_kg = fields.Float(string="Portata max kg")
    #vele_mq = fields.Char(string="Vele (mq)")
    ssb = fields.Boolean(string="SSB", index=True)
    gmdss = fields.Boolean(string="GMDSS", index=True)
    nr_componenti_equipaggio = fields.Integer(string="Nr.componenti equipaggio", index=True)
    nr_max_persone_trasportabili = fields.Integer("Nr max persone trasportabili")
    tab_min_arm = fields.Float(string="Tab. min. arm.")
    gest_stazione_radiotel = fields.Boolean(string="Gestione stazione radiotelef.", index=True)
    societa_concessionaria = fields.Many2one("ey2.societa_concessionaria", string=u"Società concessionaria:",
                                             index=True)
    tipo_canone_id = fields.Many2one("ey2.tipo_canone_rai", string="Tipo canone RAI", index=True)
    porto_ormeggio_id = fields.Many2one("ey2.porto", string="Porto di ormeggio", index=True)
    porto_base_id = fields.Many2one("ey2.porto", string="Porto base (art.2 Dlgs 171)", index=True)
    ente_classifica_id = fields.Many2one("ey2.ente_sorveglianza", string="Ente di classifica")
    ente_sorveglianza_id = fields.Many2one("ey2.ente_sorveglianza", string="Ente di sorveglianza")
    numero_alberi_mq = fields.Float(string="Nr. alberi")
    numero_motori = fields.Integer(string="Nr.motori")
    marca_motori = fields.Char(string="Marca")
    kw_motori = fields.Float(string="Kw per motore")
    superficie_velica_mq = fields.Float(string="Superficie velica (mq)")
    colore_scafo = fields.Char(string="Colore scafo")
    procedura_legale_ids = fields.One2many("ey2.procedura_legale", "nave_id", string="Procedure legali")
    proprietario_ids = fields.One2many("ey2.proprietario_armatore", "nave_proprietario_id", string="Proprietari")
    armatore_ids = fields.One2many("ey2.proprietario_armatore", "nave_armatore_id", string="Armatori")
    note = fields.Text(string="Note")
    #contatti e recapiti
    ulteriore_recapito_ids = fields.One2many("ey2.ulteriore_recapito", "nave_id", string="Ulteriori recapiti")
    contatto_nave_ids = fields.One2many("ey2.contatto_pratica_nave", "nave_id", string="Contatti")
    #fatturazione
    iva_id = fields.Many2one("account.tax", string="Regime IVA")
    periodicita_id = fields.Many2one("ey2.periodo_fatturazione_nave", string=u"Periodicità")
    importo = fields.Float(string="Importo periodico")
    #info gestione
    inps = fields.Selection(_INFO_DOVUTE, string="INPS", index=True)
    matricola_inps = fields.Char(string="Matricola")
    password_inps = fields.Char(string="Password")
    sede_inps = fields.Char(string="Sede")
    inail = fields.Selection(_INFO_DOVUTE, string="INAIL", index=True)
    pam_inail = fields.Char("PAM")
    pin_pam_inail = fields.Char(string="PIN del PAM")
    certificato_inail = fields.Char(string="Certificato")
    fanimar = fields.Selection(_INFO_DOVUTE, string="FANIMAR", index=True)
    codice_ditta_fanimar = fields.Char(string="Codice ditta")
    password_fanimar = fields.Char(string="Password")
    nr_ass_fanimar = fields.Char(string="Nr Assicur.")
    nr_deter_fanimar = fields.Char(string="Nt contratti determinati")
    nr_indet_fanimar = fields.Char(string="Nr contratti indeterminati")
    nr_comand_dir_mach_fanimar = fields.Char(string="Nr Comandanti + Dir. Macchina")
    nr_ufficiali_fanimar = fields.Char(string="Nr. Ufficiali")
    imposte = fields.Selection(_INFO_DOVUTE, string="Imposte", index=True)
    stipendi = fields.Selection(_INFO_DOVUTE, string="Stipendi", index=True)
    fatture = fields.Selection(_INFO_DOVUTE, string="Fatture fornitori", index=True)
    prezzo_richiesto_vendita = fields.Float(string="Prezzo richiesto vendita (Euro)")
    prezzo_richiesto_noleggio = fields.Float(string="Prezzo richiesto noleggio (Euro)")
    iva_assolta = fields.Boolean(string="Iva assolta", index=True)
    #assicurazione
    assicurazione_equipaggio = fields.Selection(_INFO_DOVUTE, string="Ass. equipaggio", index=True)
    assicurazione_rc_terzi = fields.Selection(_INFO_DOVUTE, string="Ass. RC terzi", index=True)
    assicurazione_pi = fields.Selection(_INFO_DOVUTE, string=u"Ass. P&I", index=True)
    assicurazione_hm = fields.Selection(_INFO_DOVUTE, string=u"Ass. H&M", index=True)
    assicurazione_corpi = fields.Selection(_INFO_DOVUTE, string="Ass. corpi", index=True)
    assicurazione_tender = fields.Selection(_INFO_DOVUTE, string="Ass. tender", index=True)
    #####Certificati di borso
    certificato_bordo_ids = fields.One2many("ey2.certificato_bordo", "nave_id", string="Certificati di bordo")
    #####apparati elettronici
    apparato_elettronico_ids = fields.One2many("ey2.apparato_elettronico", "nave_id", string="Apparati elettronici")
    #####scheda tecnica
    modello = fields.Char(string="Modello")
    anno_costr = fields.Integer(string="Anno Costr.", index=True)
    costruttore_id = fields.Many2one("ey2.costruttore", string="Costruttore", index=True)
    id_cantiere = fields.Char(string="Numero costruzione", index=True)
    rnc = fields.Char(string="RNC")
    ufficio = fields.Char(string="Ufficio", index=True)
    progettisti_interni = fields.Char(string="Progettisti interni")
    progettisti_esterni = fields.Char(string="Progettisti esterni")
    materiale_costruzione_id = fields.Many2one("ey2.materiale_costruzione",string="Materiale costruzione", index=True)
    immersione_massima = fields.Float(string="Immersione massima mt.", index=True)
    immersione_minima = fields.Float(string="Immersione minima mt.", index=True)
    altezza = fields.Float(string="Altezza mt.", index=True)
    classe = fields.Char(string="Classe")
    ente_id = fields.Many2one("ey2.ente_sorveglianza", string="Ente", index=True)
    compliance = fields.Char(string="Compliance")
    autonomia_miglia = fields.Float(string="Autonomia miglia nautiche", index=True)
    velocita_crociera = fields.Float(string=u"Velocità di crociera nodi")
    max_nodi = fields.Float(string="Velocità massima nodi")
    max_ospiti = fields.Integer(string="Nr. max ospiti", index=True)
    #motorizzazione e velature
    motore_nave_ids = fields.One2many("ey2.motore_nave", "nave_id", string="Motori")
    invertitori = fields.Char(string="Invertitori / riduttori")
    ore_navigazione = fields.Float(string="Ore navigazione")
    consumo_orario = fields.Float(string="Consumo orario (litri/h)")
    propulsione_id = fields.Many2one("ey2.propulsione", string="Propulsione", index=True)
    trasmissione = fields.Char(string="Trasmissione")
    alimentazione = fields.Char(string="Alimentazione")
    #MACCHINARI AUSILIARI ED IMPIANTI
    generatori_marca = fields.Char(string="Marca generatori")
    generatori_modello = fields.Char(string="Modello generatori")
    generatori_potenza = fields.Float(string="Potenza generatori (kw)")
    generatori_volts = fields.Float(string="Volts generatori")
    generatori_fasi = fields.Integer(string="Fasi generatori")
    generatori_frequenza = fields.Float(string="Frequenza generatori (Hz)")
    sep_olio_marca = fields.Char(string="Marca separatore olio")
    sep_olio_modello = fields.Char(string="Modello separatore olio")
    dep_carburante_marca = fields.Char(string="Marca depuratore carburante")
    dep_carburante_modello = fields.Char(string="Modello depuratore carburante")
    save_system_marca = fields.Char(string="Marca sewage system")
    save_system_modello = fields.Char(string="Modello sewage system")
    elica_prua_marca = fields.Char(string="Marca elica di prua")
    elica_prua_modello = fields.Char(string="Modello elica di prua")
    dissalatore_marca = fields.Char(string="Marca dissalatore")
    dissalatore_modello = fields.Char(string="Modello dissalatore")
    ac_marca = fields.Char(string="Marca aria condizionata")
    ac_modello = fields.Char(string="Modello aria condizionata")
    nr_batterie_principali = fields.Integer(string="Numero batterie principali")
    volts_batterie_principali = fields.Float(string="Volts batterie principali")
    ah_batterie_prnncipali = fields.Float(string="Ah. batterie principali")
    nr_batterie_generatori = fields.Integer(string="Numero batterie generatori")
    volts_batterie_generatori = fields.Float(string="Volts batterie generatori")
    ah_batterie_generatori = fields.Float(string="Ah. batterie generatori")
    nr_batterie_servizi = fields.Integer(string="Numero batterie servizi")
    volts_batterie_servizi = fields.Float(string="Volts batterie servizi")
    ah_batterie_servizi = fields.Float(string="Ah. batterie servizi")
    nr_batterie_emergenza = fields.Integer(string="Numero batterie emergenza")
    volts_batterie_emergenza = fields.Float(string="Volts batterie emergenza")
    ah_batterie_emergenza = fields.Float(string="Ah. batterie emergenza")
    volts_alimentazione_terra = fields.Integer(string="Volts alimentazione da terra")
    fasi_alimentazione_terra = fields.Float(string="Fasi alimentazione da terra")
    frequenza_alimentazione_terra = fields.Float(string="Frequenza alimentazione da terra")
    #Capacità casse di bordo
    litri_carburante = fields.Float(string="Carbuarnte (litri)")
    litri_acqua = fields.Float(string="Acqua (litri)")
    litri_olio_lubr = fields.Float(string="Olio lubrificante (litri)")
    litri_olio_esausto = fields.Float(string="Olio esausto (litri)")
    note_scheda_tecnica = fields.Text(string="Note")
    #####alloggi
    alloggio_ids = fields.One2many("ey2.alloggio", "nave_id", string="Alloggi")
    #####equipaggiamtni
    equipaggiamento_nave_ids = fields.One2many("ey2.equipaggiamento_nave", "nave_id", string="Equipaggiamenti")
    #####galleria immagini
    immagine_nave_ids = fields.One2many('ey2.immagine_nave', 'nave_id', string='Immagini')
    #follow_up
    follow_up_gest_ids = fields.One2many("ey2.follow_up_gest_nave", "nave_id", string="Follw up (gestione)")
    follow_up_med_ids = fields.One2many("ey2.follow_up_med_nave", "nave_id", string="Follw up (mediazione)")
    # rappresentanti per armatore/proprietario
    rappresentante_ruolo_ids = fields.One2many("ey2.rappresentante_ruolo", "nave_id", string="Rappresentanti")
    # pratiche imbarchi o sbarchi
    imbarco_sbarco_ids = fields.One2many("ey2.pratica_nave", 'partner_id', string="Imbarchi/Sbarchi",
                                         domain=[('tipo_pratica', 'in', ['Imbarco', 'Sbarco'])])
    # altre pratiche
    altra_pratica_ids = fields.One2many("ey2.pratica_nave", 'partner_id', string="Altre pratiche",
                                        domain=[('tipo_pratica', 'not in', ['Imbarco', 'Sbarco'])])
    # adempimenti
    adempimenti = fields.Many2many(comodel_name="ey2.adempimento_nave", relation="ey2_unita_adempimenti_rel",
                                   string="Adempimenti", index=True)
    # blacklist
    blacklist = fields.Boolean(string="Black list")
    #soggetto fatturazione
    soggetto_fatturazione_id = fields.Many2one("res.partner", string="Soggetto fatturazione")
    #documenti amministrativi
    doc_amministrativi_ids = fields.One2many('ey.documento_partner', 'nave_id', string="Documenti amministrativi")
    #sted
    sted_nr_dci = fields.Char(string="Nr.DCI", index=True)
    sted_data_dci = fields.Date(string="Data DCI", index=True)
    sted_ente_rilascio = fields.Many2one("ey2.ente_sorveglianza", string="Ente rilascio DCI")
    # sezione storici
    storico_nome_ids = fields.One2many('ey2.storico_nave', "nave_id", string="Storico nomi",
                                       domain=[('nome', '!=', False)])
    storico_porto_ids = fields.One2many('ey2.storico_nave', "nave_id", string="Storico porti iscrizione",
                                        domain=[('porto_id', '!=', False)])
    storico_nr_on_ids = fields.One2many('ey2.storico_nave', "nave_id", string="Storico Nr. / O.N.",
                                        domain=[('nr_on', '!=', False)])
    storico_bandiera_ids = fields.One2many('ey2.storico_nave', "nave_id", string="Storico bandiere",
                                           domain=[('bandiera_id', '!=', False)])

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'nr_on':  "",
            'nominativo_interno': "",
            'imo': "",
            'mmsi': "",
            'hin_cin': "",
            'name': self.name + " (COPIA)"
        })
        return super(Unita, self).copy(default)

    @api.model
    def create(self, vals):
        prev = super(Unita, self).create(vals)
        domain_sequence = [
            ("code", '=', "ey2.riferimento_nave"),
        ]
        sequence = self.env['ir.sequence'].search(domain_sequence, limit=1)
        next_code = self.env['ir.sequence'].next_by_id(sequence.id)
        prev.write({'riferimento': next_code})
        #sequence.next_by_id()
        return prev
