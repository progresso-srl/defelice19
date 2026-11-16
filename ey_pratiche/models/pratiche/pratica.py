# -*- coding: utf-8 -*-
from odoo import Command, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

class Pratica(models.Model):
    _name = "ey_pratiche.pratica"
    _description = "Pratica"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "state asc, data_pratica desc"
    
    ##### FUNZIONI PER IL CAMBIAMENTO DI STATO
    def stato_preventivo(self):
        return self.write({'state': 'c_preventivo'})
    
    def stato_in_corso(self):
        to_write = {'state': 'h_in_corso'}
        # #TODO CHIARIRE QUESTA PARTE, ANCHE NELLA CREATE PER LE NAVI
        # il riferimento pratica viene inserito nella create solo per le pratiche soggetto, è giusto?
        if self.tipo_template == 'navi':            
            if not self.riferimento_pratica:
                domain_sequence = [
                    ("code", '=', "ey_pratiche.riferimento_pratica"),
                ]
                sequence = self.env['ir.sequence'].search(domain_sequence, limit=1)
                next_code = sequence.next_by_id()
                to_write['riferimento_pratica'] = next_code
                to_write['protocollo_data'] = (datetime.strftime(datetime.now(), '%Y-%m-%d'))
        
        return self.write(to_write)
    
    def stato_da_fatturare(self):
        return self.write({'state': 'p_da_fatturare'})
    
    def stato_fatturata(self):
        return self.write({'state': 's_fatturata'})
    
    def stato_pagata(self):
        return self.write({'state': 'v_pagata'})

    def stato_sospesa(self):
        return self.write({'state': 'x_sospesa'})

    def stato_annullata(self):
        return self.write({'state': 'z_annullata'})
    
    _TIPO_TEMPLATE = [
        ('navi', 'Navi'),
        ('soggetti', 'Soggetti')
    ]
    
    _STATO_PRATICA = [
        ("c_preventivo", "Preventivo"),
        ("h_in_corso", "In corso"),
        ("p_da_fatturare", "Da fatturare"),
        ("s_fatturata", "Fatturata"),
        ("v_pagata", "Pagata"),
        ("x_sospesa", "Sospesa"),
        ("z_annullata", "Annullata"),
        ("a_alert", "Alert")
    ]

    @api.depends('tpl_id', 'tpl_id.name', 'tipo_template','nave_id','nave_id.name','partner_id', 'partner_id.name')
    def _compute_name(self):
        for pratica in self:
            name = ""
            if pratica.tpl_id:
                name += pratica.tpl_id.name
            if pratica.tipo_template == 'navi' and pratica.nave_id:
                name += ' - ' + pratica.nave_id.name
            if pratica.tipo_template == 'soggetti' and pratica.partner_id:
                name += " - " + pratica.partner_id.name
            pratica.name = name

    name = fields.Char(string="Nome pratica", index=True, required=True, compute="_compute_name")
    tpl_id = fields.Many2one("ey_pratiche.tpl", string="Template", required=True, index=True)
    tipo_template = fields.Selection(related="tpl_id.tipo_template", string="Tipo template")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Soggetto", index=True) #TODO controllo che ci sia sul tipo pratica soggetti
    
    
    
    report_ids = fields.One2many("ey_pratiche.report_pratica", "pratica_id", string="Reports")
    chiave_ids = fields.One2many("ey_pratiche.chiave_pratica", "pratica_id", string="Chiavi")
    data_pratica = fields.Date(string="Data pre-istruzione / apertura", index=True, required=True) 
    riferimento_pratica = fields.Char(string="N. Protocollo / Riferimento pratica", index=True)
    state = fields.Selection(_STATO_PRATICA, string="Stato pratica", index=True, required=True,
                            tracking=True) #default diverso per i due tipi di pratiche
    
    
    tipo_pratica = fields.Char(string="Tipo pratica", index=True)
    # tipo_documento_id commentato - ey_corsi non installato e tabella vuota
    # tipo_documento_id = fields.Many2one("ey_corsi.tipo_documento", string="Tipo documento", index=True)
    
    
    ente_ids = fields.One2many("ey_pratiche.ente_pratica", "pratica_id", string="Enti")
    
    # allegati
    info_operatore = fields.Text(string="Info operatore")
    allegati = fields.Many2many(comodel_name="ey_pratiche.allegato_tpl", relation="ey_pratiche_pratica_allegato_tpl",
                                string="Allegati", index=True)
    
    # documenti
    documenti_pratica_ids = fields.One2many("ey_pratiche.allegato_pratica", "pratica_id", string="Documenti pratica") #track_visibility="onchange"
   
    # soggetto per fatturazione
    soggetto_fatturazione_id = fields.Many2one("res.partner", string="Soggetto fatturazione", tracking=True)
    
    # attività di sistema
    att_sistema_ids = fields.One2many("ey_pratiche.att_sistema_pratica", "pratica_id", string=u"Attività di sistema")
    
    # attività operatore
    ultima_attivita = fields.Char(string=u"Ultima attività", compute="_compute_ultima_attivita")
    att_operatore_ids = fields.One2many("ey_pratiche.att_operatore_pratica", "pratica_id", string=u"Attività operatore") #track_visibility="onchange"
    
    # contatti pratica
    contatto_pratica_ids = fields.One2many("ey_base.contatto_pratica_nave", 'pratica_id', string="Contatti") #track_visibility="onchange"
    
    # pratiche collegate
    pratiche_collegate = fields.Many2many(comodel_name="ey_pratiche.pratica", relation="ey_pratiche_pratiche_collegate_rel",
                                          column1="pratica1_id", column2="pratica2_id", string="Pratiche collegate",
                                          index=True) #, track_visibility="onchange"
 
    # #follow up
    follow_up_ids = fields.One2many("ey_pratiche.follow_up_pratica", "pratica_id", string="Follow up") #, track_visibility="onchange"
    # #alerts
    alert_ids = fields.One2many("ey_pratiche.alert_pratica_nave", "pratica_id", string="Alerts") #track_visibility="onchange"
    
    #responsabile della pratica
    user_id = fields.Many2one("res.users", string="Responsabile", index=True, required=True,
                              default=lambda self: self.env.user)
    protocollo_data = fields.Date(string="Protocollo data", index=True)
    
    #sted
    sted_nr_dci = fields.Char(string="Nr.DCI", index=True)
    sted_nr_pratica = fields.Char(string="Nr. Pratica", index=True)
    sted_data_dci = fields.Date(string="Data DCI", index=True)
    sted_data_pratica = fields.Date(string="Data pratica", index=True)
    # sted_ente_rilascio commentato - modello ey_base.ente_sorveglianza non esiste
    # sted_ente_rilascio = fields.Many2one("ey_base.ente_sorveglianza", string="Ente rilascio DCI")
        
    
    ##### CAMPI NAVE ####################
    #####################################
    nave_id = fields.Many2one("ey_base.unita", string="Nave", index=True) 
    partner_riferimento_id = fields.Many2one("res.partner", string="Marittimo di riferimento", index=True) 
    qualifica_id = fields.Many2one("ey_pratiche.qualifica_pratica_nave", string="Qualifica", index=True)
    
    ##### Campi Nave da congelare
    nome_nave = fields.Char(string="Nome nave", index=True)
    riferimento_nave = fields.Char(string="Riferimento nave", index=True)
    tipo_registro_nave = fields.Char(string="Tipo registro nave", index=True)
    numero_registro_nave = fields.Char(string="Numero registro nave", index=True)
    porto_nave = fields.Char(string="Porto di registro nave", index=True)
    bandiera_nave = fields.Char(string="Bandiera nave", index=True)
    stazza_lorda_nave = fields.Char(string="Stazza lorda nave")
    utilizzo_nave =  fields.Char(string="Utilizzo", index=True)
    
    ##### Campi Marittimo da congelare
    cognome_marittimo = fields.Char(string="Cognome marittimo")
    nome_marittimo = fields.Char(string="Nome marittimo")
    cf_marittimo = fields.Char(string="Codice fiscale marittimo")
    
    indirizzo_marittimo_id = fields.Many2one("ey_pratiche.indirizzo_partner", string="Indirizzo marittimo")
    stato_civile_marittimo = fields.Char(string="Stato civile marittimo")
    cittadinanza_marittimo = fields.Char(string="Cittadinanza marittimo")
    tipo_documento_marittimo = fields.Char(string="Tipo documento marittimo")
    numero_documento_marittimo = fields.Char(string="Numero documento marittimo")
    rilascio_documento_marittimo = fields.Char(string="Uff. rilascio documento marittimo")
    luogo_rilascio_documento_marittimo = fields.Char(string="Luogo rilascio documento marittimo")
    categoria_documento_marittimo = fields.Char(string="Categoria documento marittimo")
    documento_marittimo_id = fields.Many2one("ey_corsi.documento", string="Documento marittimo")
    
    # armatori e proprietari
    armatore_ids = fields.One2many("ey_pratiche.prop_arm_pratica", "pratica_armatore_id", string="Armatori")
    proprietario_ids = fields.One2many("ey_pratiche.prop_arm_pratica", "pratica_proprietario_id", string="Proprietari")
    rappresentante_ids = fields.One2many("ey_pratiche.prop_arm_pratica", "pratica_rappresentante_id", string="Rappresentanti")
    equipaggio_ids = fields.One2many("ey_pratiche.equipaggio_nave_pratica", "pratica_id", string="Equipaggio")
    ##### CAMPI SOGGETTO ####################
    #####################################
    
    #campi da congelare sicuramente
    cognome_soggetto = fields.Char(string="Cognome soggetto")
    nome_soggetto = fields.Char(string="Nome soggetto")
    cf_soggetto = fields.Char(string="Codice fiscale soggetto")
    indirizzo_soggetto_id = fields.Many2one("ey_pratiche.indirizzo_partner", string="Indirizzo soggetto")
    stato_civile_soggetto = fields.Char(string="Stato civile soggetto")
    cittadinanza_soggetto = fields.Char(string="Cittadinanza soggetto")
    tipo_documento_soggetto = fields.Char(string="Tipo documento soggetto")
    numero_documento_soggetto = fields.Char(string="Numero documento soggetto")
    rilascio_documento_soggetto = fields.Char(string="Uff. rilascio documento soggetto")
    luogo_rilascio_documento_soggetto = fields.Char(string="Luogo rilascio documento soggetto")
    categoria_documento_soggetto = fields.Char(string="Categoria documento soggetto")
    documento_soggetto_id = fields.Many2one("ey_corsi.documento", string="Documento soggetto")
    
    @api.constrains('tipo_template','partner_id','nave_id')
    def check_subject_pratica(self):
        for rec in self:
            if rec.tipo_template == 'navi' and not rec.nave_id:
                raise ValidationError("Il campo Nave è obbligatorio per questo tipo di template")
            elif rec.tipo_template == 'soggetti' and not rec.partner_id:
                raise ValidationError("Il campo Soggetti è obbligatorio per questo tipo di template")
            
    @api.constrains('partner_id','nave_id')
    def _ey_in_blacklist(self):
        # blacklist sul partner lo aggiunge ey_corsi, che non e' una
        # dipendenza di ey_pratiche: se manca, il partner non e' in black list.
        return bool(self.nave_id.blacklist or getattr(self.partner_id, 'blacklist', False))

    # Era un override di _validate_fields con la firma di Odoo 12: in Odoo 19
    # mandava in errore ogni salvataggio e, senza super(), avrebbe spento
    # tutti gli altri vincoli del modello.
    @api.constrains('nave_id', 'partner_id')
    def _check_blacklist(self):
        for pratica in self:
            if pratica._ey_in_blacklist():
                raise ValidationError("Errore di inserimento. Contattare amministratore")

    @api.onchange("partner_id","nave_id")
    def onchange_partner_id(self):
        if self._ey_in_blacklist():
            raise ValidationError("Errore di inserimento. Contattare amministratore")
        
    
    @api.onchange('tipo_template')
    def onchange_tipo_template(self):
        self.nave_id = None
        self.partner_id = None
        self.partner_riferimento_id = None
        # self.tipo_documento_id = None  # commentato - ey_corsi non installato
        self.qualifica_id = None
        
        if not self.state and self.tipo_template == 'navi':
            self.state = 'c_preventivo'
        elif not self.state and self.tipo_template == 'soggetti':
            self.state = 'h_in_corso'
    


    @api.model
    def default_get(self, fields):
        rec = super(Pratica, self).default_get(fields)
        rec.update({'data_pratica': datetime.now().date()})      
        return rec
    
    
    @api.model_create_multi
    def create(self, vals_list):
        # Odoo 19: create riceve sempre una lista; la logica resta per record.
        return self.browse().concat(*(self._ey_create_one(vals) for vals in vals_list))

    def _ey_create_one(self, vals):
        name = ''
        if vals.get('tpl_id'):
            name += self.env['ey_pratiche.tpl'].browse([vals['tpl_id']])[0].name
            
        #TODO AGGIUNGERE CONTROLLI RISPETTIVAMENTE CHE IL TIPO TEMPLATE SIA NAVI IN UN CASO E SOGGETTI NELL ALTRO
        if vals.get('nave_id'):
            # pratica nave
            name += " - " + self.env['ey_base.unita'].browse([vals['nave_id']])[0].name
        elif vals.get('partner_id'):
            # pratica soggetto
            name += " - " + self.env['res.partner'].browse([vals['partner_id']])[0].name
        
        if vals.get('partner_riferimento_id'):
            name += " - " + self.env['res.partner'].browse([vals['partner_riferimento_id']])[0].name
        vals['name'] = name
        pratica = super(Pratica, self).create(vals)    
        
        if pratica.tipo_template == 'soggetti':
            # sequenza
            domain_sequence = [
                ("code", '=', "ey_pratiche.riferimento_pratica"),
            ]
            sequence = self.env['ir.sequence'].search(domain_sequence, limit=1)
            next_code = sequence.next_by_id()
            pratica.write({'riferimento_pratica': next_code})
        else:
            nave = pratica.nave_id
            riferimento_nave, tipo_registro_nave, numero_registro_nave, porto_nave, bandiera_nave = ("", "", "", "", "")
            riferimento_nave = nave.riferimento
            if nave.nr_on:
                numero_registro_nave = nave.nr_on
            utilizzo_nave = ""
            if nave.utilizzo_id:
                utilizzo_nave = nave.utilizzo_id.name
            tipo_registro_nave = nave.tipo_registro_id.name
            porto_nave = nave.porto_id.name
            bandiera_nave = nave.bandiera_id.name
            soggetto_fatturazione_nave_id = False
            if nave.soggetto_fatturazione_id:
                soggetto_fatturazione_nave_id = nave.soggetto_fatturazione_id.id
        # campi partner_riferimento
        doc_obj = None
        cognome_marittimo, nome_marittimo, cf_marittimo, indirizzo_marittimo = ("", "", "", "")
        cittadinanza_marittimo, stato_civile_marittimo = ("", "")
        partner_rif = pratica.partner_id if pratica.tipo_template == 'soggetti' else pratica.partner_riferimento_id
        if partner_rif:
            cognome_marittimo = partner_rif.cognome
            nome_marittimo = partner_rif.nome
            # fiscalcode e' di l10n_it_fiscalcode (OCA), non fra le dipendenze
            cf_marittimo = getattr(partner_rif, 'fiscalcode', '') or ''
            indirizzo_marittimo = self._get_address(partner_rif)
            if partner_rif.stato_civile:
                stato_civile_marittimo = partner_rif.stato_civile.name
            if partner_rif.nazionalita_id:
                cittadinanza_marittimo = partner_rif.nazionalita_id.name
            # COMMENTATO - tipo_documento_id non esiste più
            # # cerco il documento del marittimo
            # max_date = ""
            # for doc in partner_rif.documento_ids:
            #     # confronto il nome anziché gli id perché ci sono varie tipologie diverse con lo stesso nome e vanno bene lo stesso
            #     if doc.tipo_id.name.lower() == pratica.tipo_documento_id.name.lower():
            #         scadenza = str(doc.data_scadenza) if doc.data_scadenza else ""
            #         if scadenza >= max_date:
            #             doc_obj = doc
            #             max_date = scadenza
            # if not doc_obj:
            #     if pratica.tipo_template == 'soggetti':
            #         raise ValidationError("Il soggetto in questione non ha un documento di tipo " + pratica.tipo_documento_id.name)
            #     else:
            #         raise ValidationError("Il marittimo in questione non ha un documento di tipo " + pratica.tipo_documento_id.name)
        if pratica.tipo_template == 'soggetti':
            campi_da_congelare = {
            'info_operatore': pratica.tpl_id.info_operatore,
            "tipo_pratica": pratica.tpl_id.tipo_pratica,
            # "nome_nave": pratica.partner_id.name,
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
        else:
            campi_da_congelare = {
            'info_operatore': pratica.tpl_id.info_operatore,
            "tipo_pratica": pratica.tpl_id.tipo_pratica,
            "nome_nave": pratica.nave_id.name,
            "stazza_lorda_nave": ("%.2f" % pratica.nave_id.stazza_lorda).replace(".", ","),
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
            campi_da_congelare['sted_nr_dci'] = pratica.nave_id.sted_nr_dci
            campi_da_congelare['sted_data_dci'] = pratica.nave_id.sted_data_dci
            # sted_ente_rilascio commentato - modello non esiste
            # if pratica.nave_id.sted_ente_rilascio:
            #     campi_da_congelare['sted_ente_rilascio'] = pratica.nave_id.sted_ente_rilascio.id
        pratica.write(campi_da_congelare)
        # PARTE IN CUI SETTO IL VALORE DELLE CHIAVI
        # models
        cp_model = self.env['ey_pratiche.chiave_pratica']
        rp_model = self.env['ey_pratiche.report_pratica']
        ir_model = self.env['ir.actions.report']
        # inizializzo le chiavi
        tpl = pratica.tpl_id
        obj_pratica = pratica.partner_id if pratica.tipo_template == 'soggetti' else pratica.nave_id
        for chiave in tpl.chiave_ids:
            
            key = chiave.chiave
            descrizione = chiave.descrizione
       
            if chiave.tipo_chiave == 'campo':
                #TODO CONTROLLARE SE VA BENE
                arr_value = key.split(".")
          
                value = ""
                is_valore = False
                # inizializzo obj con l oggetto della pratica; successivamente può cambiare se il valore di un campo è un many2one
                obj = obj_pratica
                 # mi salvo in una variabile il nome del modello; anch'esso ovviamente può cambiare se il valore di un campo è un many2one
                current_model = self.env[obj._name]
                try:
                   
                    # se la chiave è un campo di un many2one devo continuare a scorrere le parti di chiave divise dai "." finché non arrivo al valore finale
                    for field in arr_value:
                        current_value = getattr(obj, field)
                        
                        if arr_value.index(field) != len(arr_value) - 1:
                            # Se non è l ultima parte della stringa, l'oggetto di riferimento diventa il valore corrente, quindi cambia anche il modello corrente
                            obj = current_value
                            current_model =  self.env[obj._name]                            
                        else:
                            # controllo che il field finale appartenga effettivamente ai campi del modello corrente
                            current_field = current_model._fields.get(field)
                            # elaboro il current value in base al tipo di campo
                            if current_field: 
                                tcf = current_field.type
                                if tcf in ["char","text"]:
                                    value = current_value
                                elif tcf in ["float","integer"]:
                                    value = str(current_value) if current_value != None else '' #TODO TESTARE
                                elif tcf in ["boolean"]:
                                    if current_value == True:
                                        value = 'Sì'
                                    elif current_value == False:
                                        value = 'No'
                                    else:
                                        value = ''
                                elif tcf == "selection":
                                    if current_value:
                                        #dict(pratica._fields['state'].selection).get(pratica.state)    
                                        selection_value_string = dict(obj._fields[field].selection).get(obj[field])
                                        value = selection_value_string if selection_value_string else ''
                                    else:
                                        value = ''
                                elif tcf == 'date':
                                    value = current_value.strftime("%d-%m-%Y") if current_value else ''
                                elif tcf == 'datetime':
                                    value = current_value.strftime("%d-%m-%Y %H:%M:%S")
                                elif tcf == 'monetary':
                                    value = str(current_value) if current_value!=None else '' 
                                    #TODO AGGIUNGERE VALUTA
                                else:
                                    # gli altri tipi di campo non possono essere convertiti in stringa perciò restituisco ''
                                    value = ''
                               
                            else:         
                                value = ''                                 
                   
                except Exception as e:                    
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
        if pratica.tipo_template == 'navi':
            self._compute_prop_arm(pratica.nave_id.armatore_ids, 'pratica_armatore_id', pratica.id)
            self._compute_prop_arm(pratica.nave_id.proprietario_ids, 'pratica_proprietario_id', pratica.id)
            self._compute_prop_arm(pratica.nave_id.rappresentante_ruolo_ids, 'pratica_rappresentante_id', pratica.id,
                                prop_arm=False)
            pratica._crea_equipaggio()
        # inizializzo i reports
        for doc in tpl.document_ids:
            rp = ir_model.search([('documento_pratica_id','=',doc.id)], limit=1)
            if rp:
                rp_vals = {
                    'pratica_id': pratica.id,
                    'report_id': rp.id,
                    'priority': doc.priority
                }
                rp_model.create(rp_vals)   
        #TODO in odoo 8 qua veniva settato il parser corretto. Adesso va settato su py3o (mi pare py3o.report)
        stato_pratica = dict(pratica._fields['state'].selection).get(pratica.state)        
       
        # as_vals = {            
        #     'pratica_id': pratica.id,
        #     'descrizione': "Creata pratica in stato " + stato_pratica
        # }
        # self.env['ey_pratiche.att_sistema_pratica'].create(as_vals)
        for val in vals.get('ente_ids') or []:
            if val[0] == Command.CREATE:
                pratica._ey_nota_ente_aggiunto(val[2])
         
        
        #PRATICHE COLLEGATE: il collegamento vale nei due versi
        if 'pratiche_collegate' in vals:
            pratica._ey_sincronizza_collegate({pratica.id: set()})
        return pratica

    def _ey_nota_ente_aggiunto(self, ente_vals):
        ente = self.env['ey_pratiche.ente'].browse(ente_vals.get('partner_id'))
        identificatore = " (%s)" % ente_vals['identificatore'] if ente_vals.get('identificatore') else ''
        self.message_post(body="Aggiunto Ente: %s%s" % (ente.denominazione or '', identificatore))

    def _ey_sincronizza_collegate(self, prima):
        """Rende simmetrico il collegamento fra pratiche.

        ``prima``: {id pratica: set degli id collegati prima della modifica}.
        Se A collega B, anche B collega A; se A scollega B, anche B scollega
        A. Prima lo faceva SQL scritto a mano sulla tabella di relazione.
        """
        if self.env.context.get('ey_sync_collegate'):
            return
        altre = self.with_context(ey_sync_collegate=True)
        for p in self:
            dopo = set(p.pratiche_collegate.ids)
            before = prima.get(p.id, set())
            for pid in dopo - before:
                altre.browse(pid).write({'pratiche_collegate': [Command.link(p.id)]})
            for pid in before - dopo:
                altre.browse(pid).write({'pratiche_collegate': [Command.unlink(p.id)]})
    
    
    
    @api.depends('att_operatore_ids', 'att_operatore_ids.descrizione', 'att_operatore_ids.data')
    def _compute_ultima_attivita(self):
        for pratica in self:
            date = datetime.strptime("1970-01-01","%Y-%m-%d")
            descr = ""
            for att in pratica.att_operatore_ids:
                if att.data > date:
                    date = att.data
                    descr = att.descrizione
            if descr and len(descr) > 255:
                descr = descr[:252] + "..."
            pratica.ultima_attivita = descr
            
    
    def _compute_prop_arm(self, obj_list, field, pratica_id, prop_arm=True):
        """
        Funzione che aggiorna la lista degli armatori o dei proprietari
        :param obj_list: list lista degli armatori/proprietari della nave
        :param field: string 'pratica_proprietario_id' o 'pratica_armatore_id'
        :param pratica_id: integer id della pratica
        :param prop_arm: Boolean False se si crea un rappresentante
        :return: 
        """
        model = self.env['ey_pratiche.prop_arm_pratica']
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
                    'fiscalcode': getattr(partner, 'fiscalcode', False),
                }
                if not prop_arm:
                    vals['ruolo'] = item.ruolo_id.name
                    vals['testo_descrittivo'] = item.testo_descrittivo
                if field == 'pratica_proprietario_id':
                    vals['carati'] = item.carati
                model.create(vals)
                
    def _crea_equipaggio(self):
        equip_model = self.env["ey_pratiche.equipaggio_nave_pratica"]
        for rec in self:        
            for eq in rec.nave_id.equipaggio_ids:     
                # se il membro dell equipaggio è attivo lo inserisco nella pratica
                if eq.riferimento:           
                    vals = {
                        'pratica_id': rec.id,
                        'partner_id': eq.partner_id.id,
                        'cognome': eq.partner_id.cognome,
                        'nome': eq.partner_id.nome,
                        'identificatore': eq.identificatore,
                        'inizio': eq.inizio,
                        'fine': eq.fine,
                        'data_imbarco': eq.data_imbarco,
                        'data_sbarco': eq.data_sbarco,
                        'ruolo': eq.ruolo,
                    }
                    equip_model.create(vals)
            

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

    ################ SCHEDULER ALERT
    @api.model
    def scheduler_alert_pratica(self):
        today = datetime.now()
        pratiche = self.search([])
        for pratica in pratiche:
            if pratica.state != 'a_alert':
                for alert in pratica.alert_ids:
                    if alert.attivo:
                        alert_date = datetime.strptime(str(alert.data), '%Y-%m-%d')
                        if today >= alert_date:
                            pratica.with_context({'operatore_id': alert.operatore_id.id}).write({'state': 'a_alert'})


    def write(self, vals):
        for p in self:
            # passaggio di stato in attività di sistema
            if 'state' in vals and vals['state'] != p.state:
                state_before = dict(p._fields['state'].selection).get(p.state) #p.state.split("-")[1]
                state_after = dict(p._fields['state'].selection).get(vals['state']) #vals['state'].split("-")[1]
                descr = "Passaggio da " + state_before + " a " + state_after
                as_vals = {
                    'pratica_id': p.id,
                    'descrizione': descr
                }
                if state_after == 'Alert':
                    as_vals['operatore_id'] = self.env.context['operatore_id']
                self.env['ey_pratiche.att_sistema_pratica'].create(as_vals)
            
            
            if 'ente_ids' in vals and vals['ente_ids']:
                for val in vals['ente_ids']:
                    if val[0] == 2:
                        # Ente rimosso
                        ente_pratica =  p.ente_ids.filtered(lambda r:r.id == val[1])
                        identificatore = " (" + ente_pratica.identificatore + ")" if ente_pratica.identificatore else ''                
                        p.message_post(body="Rimosso Ente: %s%s" % (ente_pratica.partner_id.denominazione or '', identificatore))
                    elif val[0] == 0:
                        p._ey_nota_ente_aggiunto(val[2])

        prima = {p.id: set(p.pratiche_collegate.ids) for p in self} if 'pratiche_collegate' in vals else None
        res = super(Pratica, self).write(vals)
        if prima is not None:
            self._ey_sincronizza_collegate(prima)
        return res

class ChiavePratica(models.Model):
    _name = "ey_pratiche.chiave_pratica"
    _description = "Chiave pratica"
    _order = "priority asc"

    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    chiave = fields.Char(string="Chiave", index=True, required=True)
    descrizione = fields.Char(string="Descrizione")
    valore = fields.Char(string="Valore", index=True)
    is_valore = fields.Boolean(index=True)
    priority = fields.Integer(string=u"Priorità", index=True)
    
    
class ReportPratica(models.Model):
    _name = "ey_pratiche.report_pratica"
    _description = "Report pratica"
    _order = "priority asc"

    pratica_id = fields.Many2one("ey_pratiche.pratica", index=True)
    report_id = fields.Many2one("ir.actions.report", string="Report", index=True)    
    priority = fields.Integer(string=u"Priorità", index=True)

    def button_stampa_pratica(self):
        self.ensure_one()
        
        #return self.report_id.report_action(self.report_id.tpl_pratica_id)
        ################################
        
        # # passo il context
        # context = {}
        # for key in self.env.context.keys():
        #     context[key] = self.env.context[key]
        
        # active_record = self.pratica_id.nave_id if self.pratica_id.tipo_template == 'navi' else self.pratica_id.partner_id
        # context.update({'active_ids': [active_record.id]})
        # context.update({'pratica_id': self.pratica_id.id})
        # context.update({'model_pratica': 'ey_pratiche.pratica'})
        
        # #TODO NON STAMPA
        # return {
        #     'type': 'ir.actions.report',
        #     'report_name': self.report_id.report_name,
        #     'context': context
        # }
        
        context = self.env.context
        docids = self.pratica_id.tpl_id
        report = self.report_id
        if docids:
            if isinstance(docids, models.Model):
                active_ids = docids.ids
            elif isinstance(docids, int):
                active_ids = [docids]
            elif isinstance(docids, list):
                active_ids = docids
            context = dict(self.env.context, active_ids=active_ids)    
        data = {
            "ids":[self.pratica_id.tpl_id.id], #serve perche create_report() è stata estesa in ey_corsi e lo richiede
            "id_pratica":self.pratica_id.id, # serve per poter selezionare il parser giusto
            # 'context': '{ ',"options":"", "id_pratica":'+ str(self.pratica_id.id) +'}', 
            'context':'{}', # se non lo metti da errore, deve essere in stringa perché verrà eseguito il json.loads
            'options':{} # se non lo metti da errore
            }
        return {
            'context': context,
            'data': data,
            'type': 'ir.actions.report',
            'report_name': report.report_name,
            'report_type': report.report_type,
            'report_file': report.report_file,
            'name': report.name,
        }



