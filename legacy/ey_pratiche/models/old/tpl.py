# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class DocumentoTpl(models.Model):
    _name = "ey_pratiche.documento_tpl"
    _order = "priority asc"

    _FORMAT = [
        ('odt', 'odt'),
        ('ods', 'ods')
    ]

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
            'name': 'documento_tpl_pratica_' + str(self.id),
            'datas_fname': 'documento_tpl_pratica' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    ####VALIDATE
    @api.one
    @api.constrains('name')
    def _validate_fields(self, context=None):
        # il name non può contenere la stringa " --  Documento: " altrimenti non funziona il duplica
        if self.name:
            index = self.name.find("--  Documento:")
            if index != -1:
                raise ValidationError("Togliere la stringa '--  Documento:' dal nome")

    name = fields.Char(string="Nome", required=True, index=True)
    tpl_id = fields.Many2one("ey_pratiche.tpl", index=True)
    format = fields.Selection(_FORMAT, string="Formato input", index=True, required=True, default="odt")
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Documento")
    document_fname = fields.Char(string="File name")
    priority = fields.Integer(string=u"Priorità", index=True, default=0)
    duplica = fields.Boolean(string="Duplica", default=True)


class ChiaveTpl(models.Model):
    _name = "ey_pratiche.chiave_tpl"
    _order = "priority asc"

    @api.onchange('tipo_chiave')
    def onchange_tipo_chiave(self):
        if self.tipo_chiave and self.tipo_chiave == "Campo":
            self.valore = ""

    tpl_id = fields.Many2one("ey_pratiche.tpl", index=True)
    chiave = fields.Char(string="Chiave", index=True, required=True)
    descrizione = fields.Char(string="Descrizione")
    tipo_chiave = fields.Selection([('Valore', 'Valore'), ('Campo', 'Campo')], string="Tipo", default="Campo",
                                   index=True, required=True)
    valore = fields.Char(string="Valore")
    priority = fields.Integer(string=u"Priorità", index=True, default=0)


class AllegatoTpl(models.Model):
    _name = "ey_pratiche.allegato_tpl"

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
            'name': 'allegato_tpl_pratica_' + str(self.id),
            'datas_fname': 'allegato_tpl_pratica' + str(self.id),
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
    tpl_id = fields.Many2one("ey_pratiche.tpl", index=True)
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Documento")
    document_fname = fields.Char(string="File name")


class Tpl(models.Model):
    _name = "ey_pratiche.tpl"

    @api.multi
    def button_duplica(self):
        self.ensure_one()
        tpl_vals = {
            'name': self.name + " (COPIA)",
            'stato_template': 'Attivo',
            'tipo_pratica': self.tipo_pratica,
            'info_operatore': self.info_operatore,
            'document_ids': [],
            'chiave_ids': [],
            'allegato_ids': []
        }
        #documenti
        for doc in self.document_ids:
            if doc.duplica:
                tpl_vals['document_ids'].append((0, 0, {
                    'name': doc.name,
                    'format': doc.format,
                    'document': doc.document,
                    'document_fname': doc.document_fname,
                    'priority': doc.priority
                }))
        #chiavi
        for chiave in self.chiave_ids:
            tpl_vals['chiave_ids'].append((0, 0, {
                'chiave': chiave.chiave,
                'tipo_chiave': chiave.tipo_chiave,
                'descrizione': chiave.descrizione,
                'priority': chiave.priority,
                'valore': chiave.valore
            }))
        #allegati
        for allegato in self.allegato_ids:
            tpl_vals['allegato_ids'].append((0, 0, {
                'name': allegato.name,
                'document': allegato.document,
                'document_fname': allegato.document_fname
            }))
        template = self.env["ey_pratiche.tpl"].create(tpl_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ey_pratiche.tpl',
            'view_mode': 'form',
            'res_id': template.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    _STATO_TEMPLATE = [
        ('Attivo', 'Attivo'),
        ('Non Attivo', 'Non Attivo')
    ]

    _TIPO_PRATICA = [
        ('Imbarco', 'Imbarco'),
        ('Sbarco', 'Sbarco'),
        ('Altro', 'Altro'),
        ('Pratica STED', 'Pratica STED'),
        ('Noleggio', 'Noleggio'),
        ('Compravendita', 'Compravendita'),
        ('Pratica doganale', 'Pratica doganale'),
        ('Gestione continuativa', 'Gestione continuativa')
    ]

    _TIPO_TEMPLATE = [
        ('Navi', 'Navi'),
        ('Soggetti', 'Soggetti')
    ]

    ##### COLUMNS
    created = fields.Boolean(string="Created", index=True)
    name = fields.Char(string="Nome", required=True, index=True)
    versione = fields.Char(string="Versione", index=True)
    document_ids = fields.One2many("ey_pratiche.documento_tpl", "tpl_id", string="Documenti per report", ondelete="cascade")
    allegato_ids = fields.One2many("ey_pratiche.allegato_tpl", "tpl_id", string="Allegati", ondelete="cascade")
    chiave_ids = fields.One2many("ey_pratiche.chiave_tpl", "tpl_id", string="Chiavi")
    stato_template = fields.Selection(_STATO_TEMPLATE, string="Stato", index=True, required=True, default="Attivo")
    tipo_pratica = fields.Selection(_TIPO_PRATICA, String="Tipo pratica", index=True, required=True)
    info_operatore = fields.Text(string="Info operatore")
    tipo_template = fields.Selection(selection=_TIPO_TEMPLATE, string="Tipo template", index=True)

    # RENDO UNIVOCO IL NOME
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Nome già utilizzato!')
    ]

    @api.multi
    def write(self, vals):
        result = super(Tpl, self).write(vals)
        report_model = self.env['ir.actions.report.xml']
        # guardo se aggiungi documenti
        if 'document_ids' in vals:
            for template in self:
                tplr = report_model.search(
                    [("report_name", 'ilike', "%_" + str(template.id) + "_tpl_report")])
                if len(tplr) < len(template.document_ids):
                    for doc in template.document_ids:
                        exist = False
                        for report in tplr:
                            if report.report_name == str(doc.id) + "_" + str(template.id) + "_tpl_report":
                                exist = True
                                break
                        if not exist:
                            out_domain = [
                                ('code', '=', 'oo-' + doc.format), ('compatible_types', '=', 'oo-' + doc.format)]
                            out_format = self.env['report.mimetypes'].search(
                                out_domain, limit=1)
                            in_format = 'oo-' + str(doc.format)
                            af_report_vals = {
                                'name': u"Tpl: " + template.name + " --  Documento: " + doc.name,
                                'model': 'ey_pratiche.tpl',
                                'report_name': str(doc.id) + "_" + str(template.id) + "_tpl_report",
                                'report_type': 'aeroo',
                                'in_format': in_format,
                                'out_format': out_format.id,
                                'parser_state': 'loc',
                                'parser_loc': 'ey_pratiche/report/template_parser.py',
                                'tml_source': 'database',
                                'report_sxw_content_data': doc.document
                            }
                            report_model.create(af_report_vals)
        # guardo se cambia il nome
        if 'name' in vals:
            for template in self:
                tplr = report_model.search(
                    [("report_name", 'ilike', "%_" + str(template.id) + "_tpl_report")])
                for report in tplr:
                    old_name = report.name
                    start_new_name = old_name[0:5]
                    last_index = old_name.find(" --  Documento: ")
                    end_new_name = ""
                    while last_index != -1:
                        end_new_name = old_name[last_index:]
                        last_index = end_new_name[17].find(" --  Documento: ")
                    report.write({'name': start_new_name + template.name + end_new_name})
        return result

    @api.model
    def create(self, vals):
        vals['created'] = True
        template = super(Tpl, self).create(vals)
        # CREO I REPORT AEROO
        # cerco il mimetipe odt
        
        return template

    @api.multi
    def unlink(self):
        corso_model = self.env['ey_pratiche.pratica_nave']
        # controllo che non esistano corsi per il template che si vuol cancellare
        for rec in self:
            pratiche = corso_model.search([('tpl_id', '=', rec.id)])
            if pratiche:
                raise ValidationError("Impossibile cancellare un template con pratiche associate")
        return super(Tpl, self).unlink()

    @api.one
    def copy(self, default=None):
        raise ValidationError("Utilizzare altro pulsante")
