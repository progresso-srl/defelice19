# -*- coding: utf-8 -*-
{
    'name': 'ey_base',
    'version': '19.0.1.0.1',
    'summary': 'E-Yacht — Modulo base anagrafiche navali',
    'category': 'Services',
    'author': 'Progresso SRL',
    'website': 'https://www.progresso.srl',
    'depends': ['base', 'account', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/res_partner/res_partner_view.xml',
        'views/anagrafiche/lookup_views.xml',
        'views/anagrafiche/unita_view.xml',
        'views/agenda_scadenze/agenda_nave_view.xml',
        'data/menuitems.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
