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


from openerp.report import report_sxw
from openerp import SUPERUSER_ID
import datetime


class TemplateParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(TemplateParser, self).__init__(cr, SUPERUSER_ID, name, context)
        self.context = context

        self.keys = self._get_fields(cr, uid, self.context)
        #in context['active_ids'] ci sono gli id degli attestati di frequenza da stampare
        self.pratica = self._get_this(cr, uid, context)
        self.localcontext.update({
            "format": self.format,
            "format_date": self.format_date,
            "format_datetime": self.format_datetime,
            "chiavi": self.keys,
            "pratica": self.pratica
        })

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
