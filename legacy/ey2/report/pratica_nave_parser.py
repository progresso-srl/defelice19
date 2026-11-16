# -*- coding: utf-8 -*-
##############################################################################
#
#    CAMSPM module for OpenERP
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


import os
import imp
from openerp.report import report_sxw
from openerp import SUPERUSER_ID
from num2words import num2words
import datetime

#config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'config_tpl', 'report'))
#parser = imp.load_source('template_parser', os.path.join(config_path, 'template_parser.py'))


class Parser(report_sxw.rml_parse):#(parser.TemplateParser):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, SUPERUSER_ID, name, context)
        #super(Parser, self).__init__(cr, uid, name, context)

        ###############################################################
        self.context = context

        self.keys = self._get_fields(cr, uid, self.context)
        # in context['active_ids'] ci sono gli id degli attestati di frequenza da stampare
        self.pratica = self._get_this(cr, uid, context)
        #################################################################

        self.localcontext.update({
            "armatore": self.get_armatore,
            "proprietario": self.get_proprietario,
            "rappresentante": self.get_rappresentante,
            "ente": self.get_ente,
            "mese": self.mese_string,
            "numero_string": self.numero_string,
            "numero_string_en": self.numero_string_en,
            #################################################################
            "format": self.format,
            "format_date": self.format_date,
            "format_datetime": self.format_datetime,
            "chiavi": self.keys,
            "pratica": self.pratica,
            #################################################################
            'myset': self.myset,
            'myget': self.myget,
            'storage': {}
        })

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

    def format(self, value):
        if not value:
            return ""
        return value

    def format_date(self, date):
        if not date:
            return ""
        d = datetime.datetime.strptime(date, "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")

    def format_datetime(self, date):
        date_split = date.split(" ")
        return self.format_date(date_split[0]) + "\t" + date_split[1]

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

    def numero_string(self, number):
        number = float(number)
        return self._numberToText(number)

    def numero_string_en(self, number):
        return num2words(number)

    #funzione che scorre tutti gli attestati di frequenza passati
    def _get_fields(self, cr, uid, context):
        result = {}
        pratica = self.pool.get(context['model_pratica']).browse(cr, uid, context['pratica_id'], context=context)
        for chiave in pratica.chiave_ids:
            result[chiave.chiave] = chiave.valore
        return result

    def _get_this(self, cr, uid, context):
        pratica = self.pool.get(context['model_pratica']).browse(cr, uid, context['pratica_id'], context=context)
        return pratica

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

    # funzione wrapper
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

    #dichiarare e leggere variabili
    def myset(self, pair):
        if isinstance(pair, dict):
            self.localcontext['storage'].update(pair)
        return False

    def myget(self, key):
        if key in self.localcontext['storage'] and self.localcontext['storage'][key]:
            return self.localcontext['storage'][key]
        return False