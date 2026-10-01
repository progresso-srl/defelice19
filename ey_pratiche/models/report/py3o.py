# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime
import num2words
class Py3oTemplate(models.Model):
    _inherit = "py3o.template" 
    
    # #TODO fare in modo che se i record collegati ai tpl di pratiche  essi non siano modificabili ne cancellabili, PERò DEVONO POTER COLLEGARE UN NUOVO TEMPLATE 
  
    def unlink(self):
        # L'unico modo per eliminare un py3o collegato a un report a sua volta collegato a un documento di una pratica è durante l unlink del tpl a cui è associato il documento, durante il quale viene settato documento_pratica_id a null 
        for rec in self:
            report_doc_pratica = self.env['ir.actions.report'].search([('documento_pratica_id','!=',False),('py3o_template_id','=',rec.id)], limit=1)
            if report_doc_pratica:
                tpl_pratica_name = report_doc_pratica.tpl_pratica_id.name
                id_tpl_pratica = str(report_doc_pratica.tpl_pratica_id.id)
                raise ValidationError("Questo template Py3o non può essere eliminato perché è associato al seguente template di pratica: " + tpl_pratica_name + " (ID " + id_tpl_pratica + ")") 
              
        return super(Py3oTemplate, self).unlink()
    
class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"
    
    # variabili utente
    mystorage = {}
    
    def _extend_parser_context(self, context, report_xml):
      
        super(Py3oReport, self)._extend_parser_context(context, report_xml)     
        self.mystorage = {}
        # se entra qua vuol dire che ho eseguito stampa_pratica()
        if report_xml.documento_pratica_id and 'id_pratica' in context:
            tpl = report_xml.tpl_pratica_id
            pratica = self.env['ey_pratiche.pratica'].search([('id','=',context['id_pratica'])], limit=1)
            context['pratica'] = pratica
            context['model_pratica'] = 'ey_pratiche.pratica'
            # keys
            keys = {}
            for chiave in pratica.chiave_ids:
                keys[chiave.chiave] = chiave.valore
            context['chiavi'] = keys
            context['rappresentante'] = self.get_rappresentante    
            #TODO TESTARE QUESTI SOTTO        
            context['ente'] = self.get_ente 
            context['mese'] = self.mese_string
            context['numero_string'] = self.numero_string
            context['numero_string_en'] = self.numero_string_en
            context['force_number'] = self.force_number
            context['format'] = self.format
            context['formatta_data'] = self.formatta_data 
            context['formatta_dataora'] = self.formatta_dataora 
            context['get_anno'] = self.get_anno
            context['maggiore'] = self.maggiore
            context['myset'] = self.myset
            context['myget'] = self.myget
            
        
            if tpl.tipo_template == 'navi':
                self._get_parser_navi(pratica, context)
            else:
                self._get_parser_soggetti(pratica, context)
    
        
        
      
    
    def get_rappresentante(self, pratica, identificatore):
        for rappresentante in pratica.rappresentante_ids:
            if identificatore == rappresentante.identificatore:
                return rappresentante
        return None
    
    def get_ente(self, pratica, identificatore):
        for ente in pratica.ente_ids:
            if identificatore == ente.identificatore:
                return ente
        return None
    

    def mese_string(self, mese):
        convert = {
            '01': 'Gennaio',
            '02': 'Febbraio',
            '03': 'Marzo',
            '04': 'Aprile',
            '05': 'Maggio',
            '06': 'Giugno',
            '07': 'Luglio',
            '08': 'Agosto',
            '09': 'Settembre',
            '10': 'Ottobre',
            '11': 'Novembre',
            '12': 'Dicembre'
        }
        if mese in convert:
            return convert[mese]
        raise ValueError("Mese " + mese + " indefinito")
    
    def maggiore(self, number1, number2):
        if isinstance(number1, str) :
            number1 = float(number1.replace(',','.'))
        if isinstance(number2, str):
            number2 = float(number2.replace(',','.'))
      
        return number1 > number2
    
    def numero_string(self, number):
        if isinstance(number, str) :
            number = float(number.replace(',','.'))
        intero = num2words.num2words(int(number), lang="it")
        # prendo la parte decimale
        decimali = number - int(number)
        # arrotondo e tolgo la virgola
        decimali = int(round(decimali, 2) * 100)      
        
        if decimali < 10:
            decimali = '0' + str(decimali)
        else:
            decimali = str(decimali)
            
        return intero + '/' + decimali

    def numero_string_en(self, number):
        intero = num2words.num2words(int(number))
        # prendo la parte decimale
        decimali = number - int(number)
        # arrotondo e tolgo la virgola
        decimali = int(round(decimali, 2) * 100)      
        
        if decimali < 10:
            decimali = '0' + str(decimali)
        else:
            decimali = str(decimali)
            
        return intero + '/' + decimali
    
    def force_number(self, value):
        if isinstance(value, str):
            value = value.replace(",",".")
        if not value:
            value=0
        value = float(value)
        return value

    def format(self, value):
        if not value:
            return ""
        return value

    # formatta_data e formatta_dataora hanno il nome in italiano perche poi py3o va a inserire da se format_date e format_datetime
    def formatta_data(self, date):
        if not date:
            return ""
        return date.strftime("%d/%m/%Y")

    def formatta_dataora(self, date_time):
        date_time_split = str(date_time).split(" ")
        if len(date_time_split) != 2:
            return ''
        
        date = self.formatta_data(date_time.date())
        return date + "\t" + date_time_split[1]
    

    def get_anno(self, data):
        return data.year
    
    
    
    
        
    def _get_parser_navi(self, pratica, ctx):
        # {'model_pratica':'ey_pratiche.pratica'}
        self.ensure_one()
        ctx["armatore"] = self.get_armatore
        ctx["proprietario"] = self.get_proprietario
        ctx["equipaggio"] = self.get_membro_equipaggio
        
        
    def _get_parser_soggetti(self, pratica, ctx):
        # {'model_pratica':'ey_pratiche.pratica'}
        self.ensure_one()
        
    
        
    ##########################################################################################
     
    #TODO VEDERE CHE NON CI SIANO GIA QUESTE FUNZIONI
    def _numberToText(self, x, pos=2):
        """ Ritorna un numero tradotto in lettere
            secondo un formato 'finanziario'
        """
        sign = ""
        if x < 0:
            sign = "meno"
            x = abs(x)
        x = round(x, pos)
        n = int(x)
        frmt = "{0:0." + "{0:d}".format(pos) + "f}"
        spic = frmt.format(x - n)[2:]
        if n == 0:
            num = "zero"
        else:
            num = self._numberToTextInteger(n)
        return sign + num + "/" + spic
    
    def _numberToTextInteger(self, n):
        if n == 0:
            return ""
        elif n <= 19:
            return ("uno", "due", "tre", "quattro", "cinque",
                    "sei", "sette", "otto", "nove", "dieci",
                    "undici", "dodici", "tredici",
                    "quattordici", "quindici", "sedici",
                    "diciassette", "diciotto", "diciannove")[n - 1]
        elif n <= 99:
            decine = ("venti", "trenta", "quaranta",
                      "cinquanta", "sessanta",
                      "settanta", "ottanta", "novanta")
            letter = decine[int(n / 10) - 2]
            t = n % 10
            if t == 1 or t == 8:
                letter = letter[:-1]
            return letter + self._numberToTextInteger(n % 10)
        elif n <= 199:
            return "cento" + self._numberToTextInteger(n % 100)
        elif n <= 999:
            m = n % 100
            m = int(m / 10)
            letter = "cent"
            if m != 8:
                letter = letter + "o"
            return self._numberToTextInteger(int(n / 100)) + \
                   letter + \
                   self._numberToTextInteger(n % 100)
        elif n <= 1999:
            return "mille" + self._numberToTextInteger(n % 1000)
        elif n <= 999999:
            return self._numberToTextInteger(int(n / 1000)) + \
                   "mila" + \
                   self._numberToTextInteger(n % 1000)
        elif n <= 1999999:
            return "unmilione" + self._numberToTextInteger(n % 1000000)
        elif n <= 999999999:
            return self._numberToTextInteger(int(n / 1000000)) + \
                   "milioni" + \
                   self._numberToTextInteger(n % 1000000)
        elif n <= 1999999999:
            return "unmiliardo" + self._numberToTextInteger(n % 1000000000)
        else:
            return self._numberToTextInteger(int(n / 1000000000)) + \
                   "miliardi" + \
                   self._numberToTextInteger(n % 1000000000)



    ###### METODI PER NAVE ##########################
    def get_armatore(self, pratica, identificatore):
        for armatore in pratica.armatore_ids:
            if identificatore == armatore.identificatore:
                return armatore
        return None
    
    def get_proprietario(self, pratica, identificatore):
        for proprietario in pratica.proprietario_ids:
            if identificatore == proprietario.identificatore:
                return proprietario
        return None
    
    def get_membro_equipaggio(self, pratica, identificatore):
        for eq in pratica.equipaggio_ids:
            if identificatore == eq.identificatore:
                return eq
        return None
    
    # #dichiarare e leggere variabili
    def myset(self, pair):
        if isinstance(pair, dict):
            self.mystorage.update(pair)
        # return ''

    def myget(self, key):
        if key in self.mystorage and self.mystorage[key]:
            return self.mystorage[key]
        return False