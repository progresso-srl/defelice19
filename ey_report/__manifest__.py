# -*- coding: utf-8 -*-
{
    'name': 'ey_report',
    'version': '19.0.1.0.0',
    'summary': 'E-Yacht — Estensioni report contabili',
    'category': 'Accounting/Reporting',
    'author': 'Progresso SRL',
    'website': '#',
    'depends': ['account', 'account_financial_report', 'date_range'],
    'data': [
        'views/report_general_ledger/report_general_ledger_view.xml',
        'report/templates/general_ledger_view.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}