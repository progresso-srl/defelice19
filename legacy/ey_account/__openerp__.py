# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
{
    'name': 'De Felice Invoicing',
    'version': '1.1',
    'author' : 'Progresso S.r.l.',
    'category': 'Agenzia De Felice Accounting & Finance',
    'description': """
Accounting and Financial Management for Agenzia De Felice
====================================
Additional behaviours:
--------------------------------------------
    * Boat on account move live
    * Text field in account invocie line
    """,
    'website': 'https://www.progresso.srl',
    'depends' : ['account', 'ey2', 'l10n_it_vat_registries'],
    'data': [
        'reports.xml',
        'wizard/message_wizard_view.xml',
        'wizard/print_registro_iva.xml',
        'wizard/update_move_lines_view.xml',
        'views/account_invoice_view.xml',
        'views/report_registro_iva.xml',
        'wizard/account_partner_ledger.xml',
        'views/report_partner_ledger_template.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
