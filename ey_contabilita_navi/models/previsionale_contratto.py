# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class PrevisionaleContratto(models.Model):
    _name = "ey_contabilita_navi.previsionale_contratto"
    _order = "anno_inizio desc, mese_inizio desc"

    _MESI = [
        ('01', 'Gennaio'),
        ('02', 'Febbraio'),
        ('03', 'Marzo'),
        ('04', 'Aprile'),
        ('05', 'Maggio'),
        ('06', 'Giugno'),
        ('07', 'Luglio'),
        ('08', 'Agosto'),
        ('09', 'Settembre'),
        ('10', 'Ottobre'),
        ('11', 'Novembre'),
        ('12', 'Dicembre')
    ]

    _STATE = [
        ('Previsionale', 'Previsionale'),
        ('Consolidato', 'Consolidato'),
        ('Chiuso', 'Chiuso')
    ]

    def stato_previsionale(self):
        return self.write({'state': 'Previsionale'})

    def stato_consolidato(self):
        if (self.state_change == False):
            self.bilancio_preventivo = self.contratto_id.saldo_attuale
            self.state_change = True
        return self.write({'state': 'Consolidato'})

    def stato_chiuso(self):
        for rec in self:
            for spesa in rec.spesa_ids:
                if spesa.confermata == False:
                    raise ValidationError("Tutte le spese devono essere confermate prima di poter chiudere il previsionale!")
        return self.write({'state': 'Chiuso'})

    @api.depends('spesa_ids', 'spesa_ids.effettivo', 'spesa_ids.previsto', 'cifra_totale')
    def _compute_totali(self):
        """
        Compute i totali
        """
        for rec in self:
            anticipati = self.cifra_totale
            richiesto = 0.0
            speso = 0.0
            for spesa in rec.spesa_ids:
                richiesto += spesa.previsto
                speso += spesa.effettivo
            rec.totale_richiesto = richiesto
            rec.totale_speso = speso
            rec.bilancio = anticipati - speso

    @api.depends('contratto_id', 'contratto_id.name', 'mese_inizio', 'anno_inizio')
    def _compute_name(self):
        for rec in self:
            name = ""
            if rec.contratto_id:
                name += rec.contratto_id.name + " PERIODO "
            if rec.mese_inizio and rec.anno_inizio:
                name += rec.mese_inizio + "/" + rec.anno_inizio
            rec.name = name

    @api.onchange('spesa_ids_no_create')
    def set_spesa_ids(self):
        self.ensure_one()
        self.spesa_ids = self.spesa_ids_no_create

    # BUTTON
    def button_stampa_preventivo(self):
        self.ensure_one()

        data = {
            'ids': [self.id]
        }
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'ey_contabilita_navi_previsionale_contratto_preventivo_report',
            'report_type': 'py3o',
            'data': data,
        }
    
    def button_stampa_consuntivo(self):
        self.ensure_one()

        data = {
            'ids': [self.id]
        }
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'ey_contabilita_navi_previsionale_contratto_consuntivo_report',
            'report_type': 'py3o',
            'data': data,
        }
    
    def button_stampa_consuntivo_dettaglio(self):
        self.ensure_one()

        data = {
            'ids': [self.id]
        }
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'ey_contabilita_navi_previsionale_contratto_consuntivo_dettaglio_report',
            'report_type': 'py3o',
            'data': data,
        }
    
    def button_stampa_richiesta_fondi(self):
        self.ensure_one()

        data = {
            'ids': [self.id]
        }
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'ey_contabilita_navi_previsionale_contratto_richiesta_fondi_report',
            'report_type': 'py3o',
            'data': data,
        }

    @api.depends('anticipi_armatore_ids')
    def _compute_cifra_totale(self):
        for rec in self:
            tot = 0
            for anticipi in rec.anticipi_armatore_ids:
                tot += anticipi.cifra
            rec.cifra_totale = tot

    ##### RETURN MONTH NAME
    @api.model
    def return_month_name(self, month_number):
        self.ensure_one()
        month = str(month_number)
        if month == "01":
            return 'Gennaio'
        elif month == "02":
            return 'Febbraio'
        elif month == "03":
            return 'Marzo'
        elif month == "04":
            return 'Aprile'
        elif month == "05":
            return 'Maggio'
        elif month == "06":
            return 'Giugno'
        elif month == "07":
            return 'Luglio'
        elif month == "08":
            return 'Agosto'
        elif month == "09":
            return 'Settembre'
        elif month == "10":
            return 'Ottobre'
        elif month == "11":
            return 'Novembre'
        elif month == "12":
            return 'Dicembre'

    ##### RETURN PERIOD
    @api.model
    def return_next_period_month(self):
        self.ensure_one()
        mesi_periodicita = self.contratto_id.periodo_id.mesi % 12
        anni_periodicita = self.contratto_id.periodo_id.mesi / 12
        next_year = self.anno_inizio
        next_month = self.mese_inizio
        next_year = int(next_year) + anni_periodicita
        next_month = int(next_month) + mesi_periodicita
        if next_month > 12:
            next_month = next_month % 12
        next_month = str(next_month)
        if len(next_month) == 1:
            next_month = '0' + next_month

        return next_month
    
    @api.model
    def return_next_period_year(self):
        self.ensure_one()
        mesi_periodicita = self.contratto_id.periodo_id.mesi % 12
        anni_periodicita = self.contratto_id.periodo_id.mesi / 12
        next_year = self.anno_inizio
        next_month = self.mese_inizio
        next_year = int(next_year) + anni_periodicita
        next_month = int(next_month) + mesi_periodicita
        if next_month > 12:
            next_year += next_month / 12
            next_month = next_month % 12
        next_year = str(next_year)[:4]

        return next_year

    ##### RETURN RIMESSA DA EFFETTUARE
    def return_rimessa(self):
        self.ensure_one()
        symbol = self.currency_id.symbol
        return symbol + " " + str(format((self.totale_richiesto - self.bilancio_preventivo), ",.2f"))

    ##### RETURN LISTA PER CONSUNTIVO
    def return_merged_list(self):
        self.ensure_one()
        # preparo le variabili
        spese = self.spesa_ids
        spese_array = []
        ricavi = self.anticipi_armatore_ids
        ricavi_array = []
        symbol = self.currency_id.symbol

        #ciclo le spese interne al previsionale e le inserisco nell'array relativo
        for spesa in spese:
            if spese_array == []:
                spese_array.append({'id': spesa.tipo_id.id, 'descrizione': spesa.tipo_id.name, 'data': spesa.data_conferma.strftime('%d/%m/%Y'), 'dare': spesa.effettivo, 'avere': ''})
            elif spese_array != [] :
                # controllo se il tipo della spesa attuale esiste già nell'array oppure no
                # se esiste verrà modificato il contenuto del tipo già esistente
                # se non esiste invece verrà inserita la spesa come nuovo elemento
                enter = False
                for d in spese_array :
                    if d['id'] == spesa.tipo_id.id:
                        d['dare'] += spesa.effettivo
                        # controllo per prendere l'ultima data disponibile per quel tipo spesa
                        if datetime.strptime(d['data'], '%d/%m/%Y') < datetime.strptime(spesa.data_conferma.strftime('%d/%m/%Y'), '%d/%m/%Y'):
                            d['data'] = spesa.data_conferma.strftime('%d/%m/%Y')
                        enter = True
                if enter == False:
                    spese_array.append({'id': spesa.tipo_id.id, 'descrizione': spesa.tipo_id.name, 'data': spesa.data_conferma.strftime('%d/%m/%Y'), 'dare': spesa.effettivo, 'avere': ''})
        
        # aggiungo il simbolo della currency nella spesa per gestire meglio la grafica lato template
        for s in spese_array:
            s['dare'] = symbol + " " + str(format(s['dare'], ",.2f"))

        for ricavo in ricavi:
            ricavi_array.append({'id': ricavo.id, 'descrizione': ricavo.name, 'data': ricavo.data.strftime('%d/%m/%Y'), 'dare': '', 'avere': ricavo.cifra})

        for r in ricavi_array:
            r['avere'] = symbol + " " + str(format(r['avere'], ",.2f"))

        # unisco le spese con i ricavi e poi ordino il tutto per la data
        merged_list = spese_array
        merged_list.extend(ricavi_array)
        merged_list_sorted = sorted(merged_list, key=lambda d: datetime.strptime(d['data'], "%d/%m/%Y"))

        return merged_list_sorted

    ##### RETURN LISTA PER CONSUNTIVO DETTAGLIO
    def return_merged_list_detail(self):
        self.ensure_one()
        # preparo le variabili
        spese = self.spesa_ids
        spese_array = []
        ricavi = self.anticipi_armatore_ids
        ricavi_array = []
        symbol = self.currency_id.symbol

        #ciclo le spese interne al previsionale e le inserisco nell'array relativo
        for spesa in spese:
            spese_array.append({'id': spesa.tipo_id.id, 'descrizione': spesa.name, 'data': spesa.data_conferma.strftime('%d/%m/%Y'), 'dare': symbol + " " + str(format(spesa.effettivo, ",.2f")), 'avere': ''})

        for ricavo in ricavi:
            ricavi_array.append({'id': ricavo.id, 'descrizione': ricavo.name, 'data': ricavo.data.strftime('%d/%m/%Y'), 'dare': '', 'avere': symbol + " " + str(format(ricavo.cifra, ",.2f"))})

        # unisco le spese con i ricavi e poi ordino il tutto per la data
        merged_list_detail = spese_array
        merged_list_detail.extend(ricavi_array)
        merged_list_detail_sorted = sorted(merged_list_detail, key=lambda d: datetime.strptime(d['data'], "%d/%m/%Y"))

        return merged_list_detail_sorted
    
    ##### RETURN LISTA PER RICHIESTA FONDI
    def return_merged_list_richiesta_fondi(self):
        self.ensure_one()
        # preparo le variabili
        spese = self.spesa_ids
        spese_array = []
        symbol = self.currency_id.symbol

        #ciclo le spese interne al previsionale, filtro le righe a zero e le inserisco nell'array relativo
        for spesa in spese:
            if spesa.previsto != 0:
                spese_array.append({'id': spesa.tipo_id.id, 'tipo': spesa.tipo_id.name, 'descrizione': spesa.name, 'previsto': symbol + " " + str(format(spesa.previsto, ",.2f"))})

        # unisco le spese con i ricavi e poi ordino il tutto per la data
        return spese_array

    ##### RETURN BILANCIO CONSUNTIVO
    def return_bilancio_consuntivo(self):
        saldo_attuale = self.contratto_id.saldo_attuale
        totale_anticipi = saldo_attuale + self.cifra_totale
        bilancio_consuntivo = totale_anticipi - self.totale_speso
        return format(bilancio_consuntivo, ",.2f")

    ##### RETURN CURRENCY SYMBOL
    def return_currency_symbol(self):
        self.ensure_one()
        symbol = self.currency_id.symbol
        return symbol

    ##### RETURN CONSUNTIVO NOME STAMPA
    def return_nome_stampa_consuntivo(self):
        self.ensure_one()
        #nave = self.contratto_id.nave_id.name
        #nome_tagliato = self.contratto_id.name.split(" - ")
        return self.contratto_id.nave_id.name
    
    def return_nome_stampa_preventivo(self):
        self.ensure_one()
        nave = self.contratto_id.nave_id.name
        nome_tagliato = self.contratto_id.name.split(" - ")
        return nave + " - " + nome_tagliato[1]

    def return_nome_stampa_richiesta_fondi(self):
        self.ensure_one()
        nave = self.contratto_id.nave_id.name
        nome_tagliato = self.contratto_id.name.split(" - ")
        return "Richiesta Fondi " + nave + " - " + nome_tagliato[1]

    def return_currency_format(self, valore):
        self.ensure_one()
        symbol = self.currency_id.symbol
        return symbol + " " + str(format(valore, ",.2f"))

    def return_partita_iva(self):
        self.ensure_one()
        if (self.contratto_id.soggetto_riferimento_id.vat != False) :
            return "Partita IVA : " + self.contratto_id.soggetto_riferimento_id.vat
        else :
            return ""
        
    def return_codice_fiscale(self):
        self.ensure_one()
        if (self.contratto_id.soggetto_riferimento_id.fiscalcode != False) :
            return "Codice fiscale : " + self.contratto_id.soggetto_riferimento_id.fiscalcode
        else :
            return ""

    def return_last_date(self):
        spese = self.spesa_ids
        spese_date_array = []

        for spesa in spese:
            spese_date_array.append(spesa.data_conferma)

        return max(spese_date_array)

    name = fields.Char(string="Contratto", compute="_compute_name", store=True)
    state = fields.Selection(_STATE, string="State", index=True, default="Previsionale")
    totale_richiesto = fields.Float(string="Totale richiesto", compute="_compute_totali", store=True)
    totale_speso = fields.Float(string="Totale speso", compute="_compute_totali", store=True)
    bilancio = fields.Float(string="Bilancio", compute="_compute_totali", store=True)
    mese_inizio = fields.Selection(_MESI, string="Mese", index=True)
    anno_inizio = fields.Char(string="Anno", size=4, index=True)

    cifra_totale = fields.Monetary(string="Totale anticipo", compute="_compute_cifra_totale")
    bilancio_preventivo = fields.Float(string="Bilancio")
    state_change = fields.Boolean(string="State change", default=False)

    # CAMPI MANY2ONE
    currency_id = fields.Many2one("res.currency", string="Valuta", required=True, related='contratto_id.currency_id')
    contratto_id = fields.Many2one("ey_contabilita_navi.contratto_nave", string="Contratto collegato", required=True, index=True)
    durata_id = fields.Many2one("ey_contabilita_navi.periodo_contratto", string="Durata", related="contratto_id.periodo_id", store=True)

    # CAMPI ONE2MANY
    spesa_ids = fields.One2many("ey_contabilita_navi.spesa_previsionale", "previsionale_id", string="Spese")
    spesa_ids_no_create = fields.One2many("ey_contabilita_navi.spesa_previsionale", "previsionale_id", string="Spese")
    anticipi_armatore_ids = fields.One2many("ey_contabilita_navi.anticipi_armatore", "previsionale_id", string="Anticipi armatore")


class SpesaPrevisionale(models.Model):
    _name = "ey_contabilita_navi.spesa_previsionale"

    @api.onchange('tipo_id')
    def onchange_tipo_id(self):
        if self.tipo_id and self.tipo_id.name:
            self.name = self.tipo_id.name

    def button_crea_linea_contabile(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_collegamento_linea_spesa': 'contabilita_nave', 'default_spesa_previsionale_id': self.id}
            }
        
    @api.depends('account_move_ids')
    def _compute_account_move_id(self):
        for p in self:
            p.account_move_id = p.account_move_ids[:1].id

    @api.onchange('confermata')
    def onchange_current_date(self):
        self.ensure_one()
        if self.confermata == True :
            self.data_conferma = datetime.today().strftime("%Y-%m-%d")
        elif self.confermata == False :
            self.data_conferma = None

    name = fields.Char(string="Descrizione", required=True)
    previsto = fields.Monetary(string="Spesa prevista")
    effettivo = fields.Monetary(string="Spesa effettiva")
    confermata = fields.Boolean(string="Confermata", index=True, default=False)
    status_account = fields.Selection(string="Status contabile", related='account_move_id.state')
    data_conferma = fields.Date(string="Data conferma")

    # CAMPI MANY2ONE
    currency_id = fields.Many2one("res.currency", string="Valuta", required=True, related='previsionale_id.currency_id')
    tipo_id = fields.Many2one("ey_contabilita_navi.tipo_spesa_previsionale", string="Spesa", index=True, required=True)
    previsionale_id = fields.Many2one("ey_contabilita_navi.previsionale_contratto", index=True)
    account_move_id = fields.Many2one("account.move", string="Contabilita", compute="_compute_account_move_id")

    # CAMPI ONE2MANY
    account_move_ids = fields.One2many("account.move", "spesa_previsionale_id", string="Contabilita")


class TipoSpesaPrevisionale(models.Model):
    _name = "ey_contabilita_navi.tipo_spesa_previsionale"

    name = fields.Char(string="Tipo spesa", index=True, required=True)


class AnticipiArmatore(models.Model):
    _name = "ey_contabilita_navi.anticipi_armatore"

    ##### FUNZIONI PER IL SET E IL GET DEL BINARY
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

    def _set_document(self):
        self.ensure_one()
        max_id = 0
        cr = self._cr
        cr.execute("SELECT max(id) AS id FROM ey_corsi_documento_corso")
        dati = cr.dictfetchone()
        if dati['id']:
            max_id = int(dati['id']) + 1
        else:
            max_id = 1
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'documenti_contratto_' + str(max_id),
            'datas_fname': 'documenti_contratto_' + str(max_id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments and not self.document:
            return attachments.unlink()
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    def button_crea_linea_contabile(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_collegamento_linea_spesa': 'anticipi_armatore', 'default_anticipi_armatore_id': self.id}
            }
    

    @api.depends('account_move_ids')
    def _compute_account_move_id(self):
        for p in self:
            p.account_move_id = p.account_move_ids[:1].id

    name = fields.Char(string="Descrizione", index=True, required=True)
    data = fields.Date(string="Data", required=True)
    cifra = fields.Monetary(string="Spesa", required=True)
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Documento")
    document_fname = fields.Char(string="File name")

    # CAMPI MANY2ONE
    previsionale_id = fields.Many2one("ey_contabilita_navi.previsionale_contratto", index=True)
    currency_id = fields.Many2one("res.currency", string="Valuta", required=True, related='previsionale_id.currency_id')
    account_move_id = fields.Many2one("account.move", string="Contabilita", compute="_compute_account_move_id")
    status_account = fields.Selection(string="Status contabile", related='account_move_id.state')

    # CAMPI ONE2MANY
    account_move_ids = fields.One2many("account.move", "anticipi_armatore_id", string="Contabilita")
