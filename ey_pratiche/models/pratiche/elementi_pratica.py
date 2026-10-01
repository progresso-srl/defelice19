#-*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import time



class AlertPratica(models.Model):
    _name = "ey_pratiche.alert_pratica_nave"
    _order = "attivo desc"

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    data = fields.Date(string="Data", required=True)
    descrizione = fields.Char(string="Descrizione", required=True)
    attivo = fields.Boolean(string="Attivo", index=True, default=True)
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True, required=True)

    def write(self, vals):
        for ap in self:
            if 'attivo' in vals and vals['attivo']:
                altri_alerts = self.env['ey_pratiche.alert_pratica_nave'].search([('pratica_id', '=', ap.pratica_id.id)])
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
    
    
    
class AllegatoPratica(models.Model):
    _name = "ey_pratiche.allegato_pratica"
    

    name = fields.Char(string="Descrizione", required=True, index=True)
    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    document = fields.Binary(attachment=True, string="Documento")
    document_fname = fields.Char(string="File name")
    
    
    
class AttOperatorePratica(models.Model):
    _name = "ey_pratiche.att_operatore_pratica"
    _order = "data desc"

    
    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    data = fields.Datetime(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True, required=True)
    descrizione = fields.Text(string="Descrizione")
    document = fields.Binary(attachment=True, string="Allegato")
    document_fname = fields.Char(string="File name")


    
    
class AttSistemaPratica(models.Model):
    _name = "ey_pratiche.att_sistema_pratica"
    _order = "data desc"

    # funzione per user corrente
    def default_user_id(self):
        return self._uid

    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    data = fields.Datetime(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True)
    descrizione = fields.Text(string="Descrizione")
    


class ContattoPraticaNave(models.Model):
    _name = "ey_base.contatto_pratica_nave"
    _description = "Contatto Pratica Nave"
    
    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    name = fields.Char(string="Nome", required=True)
   

#TODO SERVE FOLLOW UP MARITTIMO???

class FollowUpPratica(models.Model):
    _name = "ey_pratiche.follow_up_pratica"    

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

    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    data = fields.Date(string="Data", index=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    operatore_id = fields.Many2one("res.users", string="Operatore", default=default_user_id, index=True)
    oggetto = fields.Char(string="Oggetto")
    descrizione = fields.Text(string="Descrizione")
    prev_descrizione = fields.Char(string="Descrizione", compute="_compute_preview")
    document = fields.Binary(attachment=True, string="Allegato")
    document_fname = fields.Char(string="File name")


    
class IndirizzoPartner(models.Model):
    _name = "ey_pratiche.indirizzo_partner"

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
    street = fields.Char(string="Indirizzo")
    street2 = fields.Char(string="Indirizzo 2")
    city = fields.Char(string="Città")
    state = fields.Char(string="Provincia")
    zip = fields.Char(string="CAP")
    country = fields.Char(string="Nazione")


class PropArmPratica(models.Model):
    _name = "ey_pratiche.prop_arm_pratica"

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

    def get_rappresentante(self):
        for pap in self:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ey_pratiche.rappresentante_armatore',
                'res_id': pap.rappresentante_id.id,
                'target': 'current',
            }

    pratica_proprietario_id = fields.Many2one("ey_pratiche.pratica", index=True)
    pratica_armatore_id = fields.Many2one("ey_pratiche.pratica", index=True)
    pratica_rappresentante_id = fields.Many2one("ey_pratiche.pratica", index=True)
    pratica_soggetto_id = fields.Many2one("ey_pratiche.pratica", index=True)
    
    partner_id = fields.Many2one("res.partner", string="Cognome e nome/Rag. sociale", index=True)
    rappresentante_id = fields.Many2one("ey_pratiche.rappresentante_armatore", string="Rappresentante", index=True)
    arm_prop = fields.Boolean(default=True)
    cognome = fields.Char(string="Cognome / RS", index=True)
    nome = fields.Char(string="Nome", index=True)
    identificatore = fields.Char(string="Identificatore", index=True)
    stato_civile = fields.Char(string="Stato civile")
    ruolo = fields.Char(string="Ruolo")
    indirizzo_id = fields.Many2one("ey_pratiche.indirizzo_partner", string="Indirizzo")
    fiscalcode = fields.Char(string="Cod. Fiscale")
    testo_descrittivo = fields.Char(string="Descr.")
    carati = fields.Char(string="Carati")
    
    

class QualificaPraticaNave(models.Model):
    _name = "ey_pratiche.qualifica_pratica_nave"
    
    name = fields.Char(string="Qualifica", index=True, required=True)
    
class RappresentanteArmatore(models.Model):
    _name = "ey_pratiche.rappresentante_armatore"
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
    # luogo_nascita_id = fields.Many2one("ey.luogo_nascita", string='Luogo di nascita', index=True)
    data_nascita = fields.Date(string="Data di nascita (gg/mm/aaaa)", index=True)
    cittadinanza_id = fields.Many2one("res.country", string="Cittadinanza", index=True)
    # stato_civile = fields.Many2one("ey.stato_civile", string="Stato civile")
    telefono = fields.Char(string="Telefono")
    email = fields.Char(string="Email")
    fiscalcode = fields.Char(string="Cod. Fiscale", index=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    zip = fields.Char(string='CAP', size=24)
    city = fields.Char(string='Città')
    state_id = fields.Many2one("res.country.state", string='Provincia/Stato', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Nazione', ondelete='restrict')

    _sql_constraints = [
        ('fiscalcode_uniq', 'UNIQUE (fiscalcode)', u'Esiste già un rappresentante con questo codice fiscale!')
    ]

class EquipaggioNavePratica(models.Model):
    _name = "ey_pratiche.equipaggio_nave_pratica"
    
    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    
    partner_id = fields.Many2one("res.partner", string="Cognome e nome", index=True)
    cognome = fields.Char(string="Cognome", index=True)
    nome = fields.Char(string="Nome", index=True)
    
    identificatore = fields.Char(string="Identificatore", index=True)
    inizio = fields.Date(string="Inizio")
    fine = fields.Date(string="Fine")
    data_imbarco = fields.Date(string="Data imbarco")
    data_sbarco = fields.Date(string="Data sbarco")
    ruolo = fields.Char(string="Ruolo")
    
    def get_partner(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'res_id': rec.partner_id.id,
                'target': 'current',
            }