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
## CARRIERS TEMPLATE CORSO ###################################################
##############################################################################
class CarrieraTplCorso(models.Model):
    _name = "ey2.carriera_tpl_corso"

    name = fields.Char(string="Carriera", index=True, reuqired=True)
    percorso_formativo_ids = fields.One2many("ey2.percorso_tpl_corso", "carriera_id", string="Percorsi formativi")

    ##### INFO SITO
    @api.model
    def list_carriere_sito(self):
        """
        Funzione che ritorna le carriere visibili sulla pagina training del sito con tutte le info utili
        :return: obj
        """
        result = {}
        list_carriere = self.search([])
        for carriera in list_carriere:
            result[str(carriera.id)] = {
                'id': carriera.id,
                'name': carriera.name,
                'percorsi_formativi': []
            }
            for pf in carriera.percorso_formativo_ids:
                templates = []
                for tpl in pf.template_corsi:
                    if tpl.attivo and tpl.pubblicato:
                        templates.append({
                            'id': tpl.id,
                            'name': tpl.name,
                            'descrizione': tpl.descrizione_corso,
                            'titolo_per_sito': tpl.titolo_corso
                        })
                result[str(carriera.id)]['percorsi_formativi'].append({
                    'id': pf.id,
                    'name': pf.name,
                    'templates': templates[:]
                })
        return result


##############################################################################
## PERCORSO TEMPLATE CORSO ###################################################
##############################################################################
class PercorsoTplCorso(models.Model):
    _name = "ey2.percorso_tpl_corso"

    name = fields.Char(string="Percorso formativo", index=True, reuqired=True)
    carriera_id = fields.Many2one("ey2.carriera_tpl_corso", string="Carriera", index=True, required=True)
    template_corsi = fields.Many2many(comodel_name="ey.template_corso", relation="ey2_tpl_corso_percorso_rel", string="Template corsi",
                                      index=True)

    ##### INFO SITO
    @api.model
    def list_percorsi_sito(self):
        """
        Funzione che ritorna i percorsi formativi visibili sulla pagina training del sito con tutte le info utili
        :return: obj
        """
        result = {}
        percorsi_formativi = self.search([])
        for pf in percorsi_formativi:
            result[str(pf.id)] = {
                'id': pf.id,
                'name': pf.name,
                'carriera_id': {
                    'id': pf.carriera_id.id,
                    'name': pf.carriera_id.name
                },
                'templates': []
            }
            for tpl in pf.template_corsi:
                if tpl.attivo and tpl.pubblicato:
                    result[str(pf.id)]['templates'].append({
                        'id': tpl.id,
                        'name': tpl.name,
                        'descrizione': tpl.descrizione_corso,
                        'titolo_per_sito': tpl.titolo_corso
                    })
        return result


##############################################################################
## TEMPLATE CORSO ############################################################
##############################################################################
class TemplateCorso(models.Model):
    _inherit = "ey.template_corso"

    _SVOLGIMENTO_CORSO = [
        ('Interno', 'Interno'),
        ('Esterno', 'Esterno')
    ]

    @api.onchange('name')
    def onchange_name(self):
        if not self.titolo_corso and self.name:
            self.titolo_corso = self.name

    # campi per sito
    percorsi_formativi = fields.Many2many(comodel_name="ey2.percorso_tpl_corso", relation="ey2_tpl_corso_percorso_rel",
                                          string="Percorsi formativi", index=True)
    titolo_corso = fields.Char(string="Titolo corso (per sito)", required=True)
    descrizione_corso = fields.Text(string="Descrizione corso")
    corso_int_est = fields.Selection(_SVOLGIMENTO_CORSO, string="Corso interno/esterno", index=True)
    pubblicato = fields.Boolean(string="Pubblicato sul sito", index=True)

    def _get_carriere(self):
        result = {}
        list_carriere = self.env['ey2.carriera_tpl_corso'].search([])
        for carriera in list_carriere:
            result[str(carriera.id)] = {
                'id': carriera.id,
                'name': carriera.name,
                'percorsi_formativi': []
            }
            for pf in carriera.percorso_formativo_ids:
                templates = []
                for tpl in pf.template_corsi:
                    if tpl.attivo and tpl.pubblicato:
                        templates.append({
                            'id': tpl.id,
                            'name': tpl.name,
                            'descrizione': tpl.descrizione_corso,
                            'titolo_per_sito': tpl.titolo_corso
                        })
                result[str(carriera.id)]['percorsi_formativi'].append({
                    'id': pf.id,
                    'name': pf.name,
                    'templates': templates[:]
                })
        return result

    def _get_percorsi(self):
        result = {}
        percorsi_formativi = self.env['ey2.percorso_tpl_corso'].search([])
        for pf in percorsi_formativi:
            result[str(pf.id)] = {
                'id': pf.id,
                'name': pf.name,
                'carriera_id': {
                    'id': pf.carriera_id.id,
                    'name': pf.carriera_id.name
                },
                'templates': []
            }
            for tpl in pf.template_corsi:
                if tpl.attivo and tpl.pubblicato:
                    result[str(pf.id)]['templates'].append({
                        'id': tpl.id,
                        'name': tpl.name,
                        'descrizione': tpl.descrizione_corso,
                        'titolo_per_sito': tpl.titolo_corso
                    })
        return result

    def _get_corsi(self):
        result = {}
        today = datetime.today().strftime("%Y-%m-%d")
        corso_domain = [
            ('data_inizio', '>=', today),
            ('pubblicato', '=', True)
        ]
        #if data_fine:
            #corso_domain.append(('data_inizio', '<=', data_fine))
        lista_corsi = self.env['ey.corso'].search(corso_domain)
        for corso in lista_corsi:
            posti_disponibili = corso.max_iscritti
            if corso.iscrizione_ids:
                posti_disponibili -= len(corso.iscrizione_ids)
            result[str(corso.id)] = {
                'id': corso.id,
                'template_id': {
                    'id': corso.template_id.id,
                    'name': corso.template_id.name,
                    'descrizione': corso.template_id.descrizione_corso,
                    'titolo_per_sito': corso.template_id.titolo_corso
                },
                'data_inizio': corso.data_inizio,
                'data_fine': corso.data_fine,
                'sede': (corso.sede_id and corso.sede_id.name) or "",
                'nr_massimo_iscrizioni': corso.max_iscritti,
                'posti_disponibili': posti_disponibili
            }
        return result

    # INFO PER SITO
    @api.model
    def list_tpl_sito(self):
        """
        Funzione che ritorna i templates visibili sulla pagina training del sito con tutte le info utili
        :return: obj
        """
        result = {}
        tpl_domain = [
            ('attivo', '=', True),
            ('pubblicato', '=', True)
        ]
        lista_templates = self.search(tpl_domain)
        for tpl in lista_templates:
            result[str(tpl.id)] = {
                'id': tpl.id,
                'name': tpl.name,
                'titolo_per_sito': tpl.titolo_corso,
                'descrizione': tpl.descrizione_corso,
                'interno_esterno': tpl.corso_int_est,
                'massimo_iscritti': tpl.max_iscritti,
                'prezzo_corso': tpl.prezzo_corso,
                'percorsi_formativi': []
            }
            for percorso in tpl.percorsi_formativi:
                result[str(tpl.id)]['percorsi_formativi'].append({
                    'id'
                    : percorso.id,
                    'name': percorso.name,
                    'carriera_id': {
                        'id': percorso.carriera_id.id,
                        'name': percorso.carriera_id.name
                    }
                })
        return {
            'templates': result,
            'percorsi': self._get_percorsi(),
            'carriere': self._get_carriere(),
            'corsi': self._get_corsi()
        }


##############################################################################
## TEMPLATE CORSO ############################################################
##############################################################################
class SedeCorso(models.Model):
    _name = "ey2.sede_corso"

    name = fields.Char(string="Sede", index=True, reuqired=True)


##############################################################################
## CORSO #####################################################################
##############################################################################
class Corso(models.Model):
    _inherit = "ey.corso"

    pubblicato = fields.Boolean(string="Pubblicato sul sito", index=True)
    sede_id = fields.Many2one("ey2.sede_corso", string="Sede", index=True)

    # INFO PER SITO
    @api.model
    def list_corsi_sito(self, data_fine=False):
        """
        Funzione che ritorna dei corsi visibili sulla pagina training del sito con tutte le info utili
        :param data_fine: date (%Y-%m-%d) - opzionale, data limite per i corsi
        :return: obj
        """
        result = {}
        today = datetime.today().strftime("%Y-%m-%d")
        corso_domain = [
            ('data_inizio', '>=', today),
            ('pubblicato', '=', True)
        ]
        if data_fine:
            corso_domain.append(('data_inizio', '<=', data_fine))
        lista_corsi = self.search(corso_domain)
        for corso in lista_corsi:
            posti_disponibili = corso.max_iscritti
            if corso.iscrizione_ids:
                posti_disponibili -= len(corso.iscrizione_ids)
            result[str(corso.id)] = {
                'id': corso.id,
                'template_id': {
                    'id': corso.template_id.id,
                    'name': corso.template_id.name,
                    'descrizione': corso.template_id.descrizione_corso,
                    'titolo_per_sito': corso.template_id.titolo_corso
                },
                'data_inizio': corso.data_inizio,
                'data_fine': corso.data_fine,
                'sede': corso.sede_id.name,
                'nr_massimo_iscrizioni': corso.max_iscritti,
                'posti_disponibili': posti_disponibili
            }
        return result


##############################################################################
## ISCRIZIONE ################################################################
##############################################################################
class Iscrizione(models.Model):
    _inherit = "ey.iscrizione"

    note = fields.Text(string="Note")
    marittimo_id = fields.Many2one("res.partner", string="Corsista", required=True, index=True,
                                   domain=['|', ('anagrafica_ey', '=', True), '|', ('personale_ey', '=', True), ('armatore_proprietario', '=', True)])


##############################################################################
## PRE-ISCRIZIONE#############################################################
##############################################################################
class PreIscrizione(models.Model):
    _name = "ey2.pre_iscrizione"
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
        context['model'] = 'ey2.pre_iscrizione'
        context['iscrizione_id'] = self.id
        return {
            'type': 'ir.actions.report.xml',
            'report_name': self.template_id.name + "_rf_report",
            'context': context,
        }

    @api.multi
    def crea_iscrizione(self):
        self.ensure_one()
        iscrizione_vals = {
            'corso_id': self.corso_id.id,
            'marittimo_id': self.marittimo_id.id,
            'destinatario_id': self.destinatario_id.id,
            'data_iscrizione': self.data_iscrizione,
            'prezzo_scontato': self.prezzo_scontato,
            'rf_compilato': self.rf_compilato,
            'prezzo_corso': self.prezzo_corso,
            'esame_id': self.esame_id.id,
            'rf_fname': self.rf_fname
        }
        iscrizione = self.env['ey.iscrizione'].create(iscrizione_vals)
        self.write({
            'iscrizione_id': iscrizione.id,
            'esito': 'Iscritto'
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey.iscrizione',
            'view_mode': 'form',
            'res_id': iscrizione.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

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
            'name': 'pi_rf_compilato_' + str(self.id),
            'datas_fname': 'pi_rf_compilato_' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.rf_compilato
        }
        attachments = ir_attachment_model.search([('datas_fname', '=', 'pi_rf_compilato_' + str(self.id)),
                                                  ('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    #####VALIDATE
    @api.one
    @api.constrains('marittimo_id', 'corso_id')
    def _validate_fields(self, context=None):
        """
        Controllo che un marittimo non venga iscritto 2 volte a un corso
        e che il corso non superi il numero massimo iscrizioni
        """
        if self.marittimo_id and self.corso_id:
            domain_iscr = [
                ('marittimo_id', '=', self.marittimo_id.id),
                ('corso_id', '=', self.corso_id.id)
            ]
            iscrizioni = self.env['ey2.pre_iscrizione'].search(domain_iscr)
            for iscr in iscrizioni:
                if iscr.id != self.id:
                    raise ValidationError("Marittimo già preiscritto a quel corso")
        if self.corso_id:
            if len(self.corso_id.iscrizione_ids) > self.corso_id.max_iscritti:
                raise ValidationError("Il corso ha raggiunto il numero massimo di iscritti")

    @api.onchange('corso_id')
    def onchange_corso_id(self):
        if self.corso_id:
            if not self.template_id:
                raise ValidationError("Selezionare prima il template del corso")
            # trovo tutti gli esami futuri con template esame collegato al template del corso selezionato
            self.prezzo_corso = self.corso_id.prezzo_corso
            esame_ids = []
            template_esame = self.corso_id.template_id.tenplate_esame_id
            esami = self.env['ey.esame'].search([('template_id', '=', template_esame.id),
                                                 ('data_esame', '>=', fields.date.today())])
            for item in esami:
                esame_ids.append(item.id)
            result = {'domain': {
                'esame_id': [('id', 'in', esame_ids)]
            }}
        else:
            result = {'domain': {
                'esame_id': [('id', 'in', [])]
            }}
        return result

    @api.onchange("marittimo_id")
    def onchange_marittimo_id(self):
        if self.marittimo_id and self.marittimo_id.blacklist:
            raise ValidationError("Errore di inserimento. Contattare amministratore")

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            return {'domain': {
                'corso_id': [
                    ('template_id', '=', self.template_id.id),
                    ('data_inizio', '>=', datetime.today().strftime('%Y-%m-%d')),
                    ('computed', '=', False)
                ]
            }}

    @api.depends('corso_id', 'marittimo_id')
    def _compute_name(self):
        for iscrizione in self:
            name = "*** PREISCRIZIONE *** "
            if iscrizione.corso_id:
                name += iscrizione.corso_id.name
            if iscrizione.marittimo_id:
                name += " - " + iscrizione.marittimo_id.name
            iscrizione.name = name

    created = fields.Boolean(string="Created", index=True)
    name = fields.Char(compute="_compute_name", store=True, index=True)
    marittimo_id = fields.Many2one("res.partner", string="Corsista", required=True, index=True,
                                   domain=['|', ('anagrafica_ey', '=', True), '|', ('personale_ey', '=', True), ('armatore_proprietario', '=', True)])
    destinatario_id = fields.Many2one("res.partner", string="Destinatario fatture", index=True,
                                      help=u"Inserire se il destinatario delle fatture non è il marittimo iscritto")
    template_id = fields.Many2one("ey.template_corso", string="Template corso", index=True, required=True)
    corso_id = fields.Many2one("ey.corso", string="Corso", index=True)
    esame_id = fields.Many2one("ey.esame", string="Esame a cui iscriversi", index=True)
    data_iscrizione = fields.Date(string="Data Preiscrizione", index=True, default=lambda self: fields.datetime.now())
    # registration form
    rf_compilato = fields.Binary(compute="_get_rf_compilato", inverse="_set_rf_compilato",
                                 string="Registration form compilato (pdf)")
    rf_fname = fields.Char(string="File name")
    data_inizio_corso = fields.Date(string="Inizio corso", related="corso_id.data_inizio", store=True, index=True)
    data_fine_corso = fields.Date(string="Fine corso", related="corso_id.data_fine", store=True, index=True)
    prezzo_corso = fields.Float(string="Prezzo totale corso")
    prezzo_scontato = fields.Boolean(string="Scontato", index=True)
    # documenti_marittimo
    documento_ids = fields.One2many(related='marittimo_id.documento_ids', string="Documenti marittimo")
    #viene inizializzata solo nel momento in cui viene pigiato il bottone "crea iscrizione"
    iscrizione_id = fields.Many2one("ey.iscrizione", string="Iscrizione collegata", index=True)
    #esiti
    esito = fields.Selection(_ESITI, string="Esito", index=True, required=True, default="In attesa")
    note_esito = fields.Text(string="Note esito")

    @api.model
    def create(self, vals):
        vals['created'] = True
        iscrizione = super(PreIscrizione, self).create(vals)
        return iscrizione
