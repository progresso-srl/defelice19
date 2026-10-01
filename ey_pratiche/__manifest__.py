# -*- coding: utf-8 -*-
{
    'name': 'ey_pratiche',
    'version': '19.0.1.0.0',
    'summary': 'E-Yacht — Gestione pratiche marittime',
    'category': 'Services',
    'author': 'Progresso SRL',
    'website': '#',
    'depends': ['base', 'mail', 'report_py3o', 'ey_base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ey_pratiche_menu.xml',
        'data/ir_sequence.xml',
        'views/normativa/normativa.xml',
        'views/pratiche/tpl.xml',
        'views/pratiche/documento_tpl.xml',        
        'views/pratiche/pratica.xml',
        'views/pratiche/ente.xml',
        'views/pratiche/follow_up_pratica.xml',
        'data/ir_cron.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
