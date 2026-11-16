# -*- coding: utf-8 -*-
{
    'name': 'ey_report',
    'version': '19.0.1.0.1',
    'summary': 'E-Yacht — Estensioni report contabili',
    'category': 'Accounting/Reporting',
    'author': 'Progresso SRL',
    'website': 'https://www.progresso.srl',
    'depends': ['account', 'account_financial_report', 'date_range'],
    # I template del Mastro (saldo di periodo, colonne) erano quelli di OCA 12
    # e mandavano in errore la stampa: sono in legacy/ey_report, da rifare
    # sui template di OCA 19.
    'data': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}