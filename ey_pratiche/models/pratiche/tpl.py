# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Tpl(models.Model):
    _name = "ey_pratiche.tpl"
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Nome già utilizzato!')
    ]


    name = fields.Char(string="Argomento", index=True, required=True)

  
    def button_duplica(self):
        self.ensure_one()
        tpl_vals = {
            'name': self.name + " (COPIA)",
            'stato_template': 'attivo',
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
        ('attivo', 'Attivo'),
        ('non_attivo', 'Non Attivo')
    ]
    
    _TIPO_TEMPLATE = [
        ('navi', 'Navi'),
        ('soggetti', 'Soggetti')
    ]

    _TIPO_PRATICA = [
        ('imbarco', 'Imbarco'),
        ('sbarco', 'Sbarco'),
        ('altro', 'Altro'),
        ('pratica STED', 'Pratica STED'),
        ('noleggio', 'Noleggio'),
        ('compravendita', 'Compravendita'),
        ('pratica doganale', 'Pratica doganale'),
        ('gestione continuativa', 'Gestione continuativa')
    ]
    

    # created = fields.Boolean(string="Created", index=True)
    name = fields.Char(string="Nome", required=True, index=True)
    tipo_template = fields.Selection(_TIPO_TEMPLATE, string="Tipo template", index=True)
    versione = fields.Char(string="Versione", index=True)
   
    document_ids = fields.One2many("ey_pratiche.documento_tpl", "tpl_id", string="Documenti per report")
    allegato_ids = fields.One2many("ey_pratiche.allegato_tpl", "tpl_id", string="Allegati")
    chiave_ids = fields.One2many("ey_pratiche.chiave_tpl", "tpl_id", string="Chiavi")
   
    stato_template = fields.Selection(_STATO_TEMPLATE, string="Stato", index=True, required=True,
                                      default="attivo")
    tipo_pratica = fields.Selection(_TIPO_PRATICA, String="Tipo pratica", index=True, required=True)
    info_operatore = fields.Text(string="Info operatore")
        
    
    # partendo dai documenti collegati risalgo ai report collegati ai documenti
    def _get_ir_actions_reports(self):
        self.ensure_one()
        ids_documents = self.document_ids.ids
        ir_actions_reports = self.env['ir.actions.report'].search([('documento_pratica_id','in',ids_documents)])
        return ir_actions_reports    
      
    def write(self, vals):
        result = super(Tpl, self).write(vals)
        report_model = self.env['ir.actions.report']
        # guardo se aggiungi documenti
        if 'document_ids' in vals:
            for template in self:
                # cerco i report collegati
                report_collegati = template._get_ir_actions_reports()
                # se ci sono meno report rispetto ai documenti collegati al tpl
                if len(report_collegati) < len(template.document_ids): #TODO Vedere se è il caso di togliere questo if per sicurezza
                    for doc in template.document_ids:
                        exist = False
                        for rc in report_collegati:
                            if rc.documento_pratica_id == doc:
                                exist = True
                                break
                            
                        if not exist:
                            # creo il py3o template
                            py3o_template = self.env['py3o.template'].create({
                                'name':doc.name, 
                                'filetype':doc.format, 
                                'py3o_template_data':doc.document
                                })

                            # aggiungo il nuovo report
                            vals_nuovo_report = {
                                'name': doc.name,
                                'report_type':'py3o',
                                'model':'ey_pratiche.tpl',
                                'report_name':"ey_pratiche.report_" + doc.name.lower().replace(' ','_').replace('/','-') + "_" + str(py3o_template.id), #concateno l'id del nuovo template per essere sicuro di non avere doppioni
                                'py3o_filetype':doc.format,#imposto il formato di output uguale a quello di input
                                'py3o_template_id': py3o_template.id, 
                                'documento_pratica_id': doc.id       
                            }
                            report_model.create(vals_nuovo_report)      
                
        # se cambia il nome, lo cambio anche al report e al py3o.template
        #TODO impedire di modificare report e py3o template se collegati a un tpl
        if 'name' in vals:
            for template in self:
                report_collegati = template._get_ir_actions_reports()
                for rc in report_collegati:
                    new_rc_name = u"Tpl: " + template.name + " -- Documento: " + rc.documento_pratica_id.name
                    rc.name = new_rc_name
                    rc.py3o_template_id.name = new_rc_name
                    
        return result

    @api.model
    def create(self, vals):
        
        # essendo un campo che diventa readonly in questa casistica, forzo il valore nei vals
        if not 'tipo_pratica' in vals and 'tipo_template' in vals and vals['tipo_template'] == 'soggetti':
            vals['tipo_pratica'] = 'altro'
            
        template = super(Tpl, self).create(vals)
        # CREO I REPORT Py3o
        # cerco il mimetype odt
        report_model = self.env['ir.actions.report']
        # creo i record py3o.template e ir.actions.report per ogni documento
        for doc in template.document_ids:
            
            nome_report = u"Tpl: " + template.name + " -- Documento: " + doc.name
            # creo il py3o template
            py3o_template = self.env['py3o.template'].create({
                'name': nome_report, 
                'filetype':doc.format, 
                'py3o_template_data':doc.document
                })
            
            # creo il report
            vals_report = {
                'name': nome_report,
                'report_type':'py3o',
                'model':'ey_pratiche.tpl',
                'report_name':"ey_pratiche.report_" + doc.name.lower().replace(' ','_').replace('/','-') + "_" + str(py3o_template.id), #concateno l'id del nuovo template per essere sicuro di non avere doppioni
                'py3o_filetype':doc.format,#imposto il formato di output uguale a quello di input
                'py3o_template_id': py3o_template.id,                 
                'documento_pratica_id': doc.id    
            }
            # ir.actions.report ha un many2one py3o_template_id, 
            # quindi risalgo al report cercando quello che hanno documento_pratica_id == doc.id
            # e al py3o_template tramite il py3o_template_id del report
            
            report_model.create(vals_report)          
        return template

    def unlink(self):
        # PARTE INHERIT
        pratica_model = self.env['ey_pratiche.pratica']
        # # controllo che non esistano pratiche per il template che si vuol cancellare
        for rec in self:
            pratiche = pratica_model.search([('tpl_id', '=', rec.id)])
            if pratiche:
                raise ValidationError("Impossibile cancellare un template con pratiche associate")
      
        # PARTE ORIGINALE
        report_model = self.env['ir.actions.report']
        # secondo for: se arrivo qui allora posso cancellare tutti i templates e i report associati
        for tpl in self:
            # nell unlink dei documenti viene gestito tutto il flusso di cancellazione dei py3o.template e dei report
            for doc in tpl.document_ids:
                doc.tpl_id = None
                doc.unlink()  
            # allegati, documenti e chiavi dall ondelete cascade sul tpl_id
        return super(Tpl, self).unlink()

    def copy(self, default=None):
        raise ValidationError("Per duplicare il template, premi sul pulsante 'Duplica'")
    
    @api.onchange('tipo_template')
    def onchange_tipo_template(self):
        if self.tipo_template == 'soggetti':
            self.tipo_pratica = 'altro'

class DocumentoTpl(models.Model):
    _name = "ey_pratiche.documento_tpl"
    _order = "priority asc"
    
    _FORMAT = [ #TODO fare delle prove su quali sono i formati validi per py3o
        ('odt', 'odt'),
        ('ods', 'ods')
    ]
    
    name = fields.Char(string="Nome", required=True, index=True)
    tpl_id = fields.Many2one("ey_pratiche.tpl", index=True)
    format = fields.Selection(_FORMAT, string="Formato input", index=True, required=True, default="odt")
    document = fields.Binary(attachment=True, string="Documento")
    document_fname = fields.Char(string="File name")
    priority = fields.Integer(string=u"Priorità", index=True, default=0)
    duplica = fields.Boolean(string="Duplica", default=True)  
   
    @api.constrains('name')
    def _validate_fields(self, context=None):
        # il name non può contenere la stringa " --  Documento: " altrimenti non funziona il duplica
        if self.name:
            index = self.name.find("--  Documento:")
            if index != -1:
                raise ValidationError("Togliere la stringa '--  Documento:' dal nome")
    
    def unlink(self):
        
        report_model = self.env['ir.actions.report']
        # gestisco tutto il flusso di cancellazione dei py3o.template e dei report  
        for doc in self:
            if doc.tpl_id:
                raise ValidationError("Questo documento è collegato a un template di pratica") #TODO INSERIRE QUALE PRATICA    
            # cerco l'ir.actions.report collegato al documento
            report = report_model.search([('documento_pratica_id','=',doc.id)], limit=1)
            # metto a null il collegamento verso il documento, che altrimenti mi impedirebbe di eliminare sia il report che il py3o.template ad esso associato
            report.documento_pratica_id = None
            # adesso posso eliminare il template py3o e il report
            report.py3o_template_id.unlink()
            report.unlink()     
            
            # i py3o template vengono cancellati dall unlink del ir actions report, mentre allegati, documenti e chiavi dall ondelete cascade sul tpl_id
        return super(DocumentoTpl, self).unlink()
    
    def apri_py3o_template(self):
        self.ensure_one()
        report = self.env['ir.actions.report'].search([('documento_pratica_id','=',self.id)], limit=1)
        py3o_template = report.py3o_template_id
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'py3o.template',
                'res_id': py3o_template.id,
                'target': 'new',
            }


class ChiaveTpl(models.Model):
    _name = "ey_pratiche.chiave_tpl"
    _order = "priority asc"    

    @api.onchange('tipo_chiave')
    def onchange_tipo_chiave(self):
        if self.tipo_chiave and self.tipo_chiave == "Campo":
            self.valore = ""

    tpl_id = fields.Many2one("ey_pratiche.tpl", index=True, ondelete="cascade")
    chiave = fields.Char(string="Chiave", index=True, required=True)
    descrizione = fields.Char(string="Descrizione")
    tipo_chiave = fields.Selection([('valore', 'Valore'), ('campo', 'Campo')], string="Tipo", default="campo",
                                   index=True, required=True)
    valore = fields.Char(string="Valore")
    priority = fields.Integer(string=u"Priorità", index=True, default=0)

class AllegatoTpl(models.Model):
    _name = "ey_pratiche.allegato_tpl"  
    
    #TODO chiedere conferma che siano modificabili sempre

    name = fields.Char(string="Descrizione", required=True, index=True)
    tpl_id = fields.Many2one("ey_pratiche.tpl", index=True, ondelete="cascade")
    document = fields.Binary(attachment=True, string="Documento")
    document_fname = fields.Char(string="File name")