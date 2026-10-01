# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SedeEnte(models.Model):
    _name = "ey_pratiche.sede_ente"

    name = fields.Char(string="Sede", index=True, required=True)


class UfficioEnte(models.Model):
    _name = "ey_pratiche.ufficio_ente"

    name = fields.Char(string="Ufficio", index=True, required=True)
    code = fields.Char(string="Codice", index=True)

class Ente(models.Model): #TODO##### CAPIRE A COSA SERVE, DATO CHE POI CI SARA ENTE_PRATICA CHE PUNTA A QUESTO, PROBABILMENTE è IL SOLITO ENTE RIGUARDANTE LE PRATICHE, MA QUESTO NON é CONGELATO, MENTRE ENTE PRATICA SI
    _name = "ey_pratiche.ente"

    @api.depends('denominazione', 'sede_id', 'sede_id.name')
    def _compute_name(self):
        for ente in self:
            name = ""
            if ente.denominazione:
                name += ente.denominazione
            if ente.sede_id:
                name += " (" + ente.sede_id.name + ")"
            ente.name = name

    name = fields.Char(string="name", index=True, compute="_compute_name", store=True)
    denominazione = fields.Char(string="Denominazione", required=True, index=True)
    sede_id = fields.Many2one("ey_pratiche.sede_ente", string="Sede", index=True)
    ufficio_id = fields.Many2one("ey_pratiche.ufficio_ente", string="Ufficio", index=True)
    contatto = fields.Char(string="Contatto")
    fiscalcode = fields.Char(string="Cod. Fiscale", index=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    zip = fields.Char(string='CAP', size=24)
    city = fields.Char(string='City')
    state_id = fields.Many2one("res.country.state", string='Provincia/Stato', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Nazione', ondelete='restrict')
    phone = fields.Char(string="Telefono")
    fax = fields.Char(string="Fax")
    email = fields.Char(string="Email")

###############################################################################à
class EntePratica(models.Model):
    _name = "ey_pratiche.ente_pratica"
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
        indirizzo = self.env['ey_pratiche.indirizzo_partner'].create(address_vals)
        return indirizzo.id

    def get_partner(self):
        for ep in self:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ey_pratiche.ente',
                'res_id': ep.partner_id.id,
                'target': 'current',
            }

    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    partner_id = fields.Many2one("ey_pratiche.ente", string="Ente", required=True)#########
    denominazione = fields.Char(string="Denominazione")
    sede = fields.Char(string="Sede")
    ufficio = fields.Char(string="Ufficio")
    codice_ufficio = fields.Char(string="Codice ufficio")
    identificatore = fields.Char(string="Identificatore")
    indirizzo_id = fields.Many2one("ey_pratiche.indirizzo_partner", string="Indirizzo")
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
            write_vals['codice_ufficio'] = ente.ufficio_id.code
        if ente.fiscalcode:
            write_vals['fiscalcode'] = ente.fiscalcode
        write_vals['indirizzo_id'] = self._get_address(ente)
        ente_pratica.write(write_vals)
        return ente_pratica

