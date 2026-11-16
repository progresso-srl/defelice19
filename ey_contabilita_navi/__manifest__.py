# -*- coding: utf-8 -*-
{
    'name': 'ey_contabilita_navi',
    'version': '19.0.1.0.1',
    'summary': 'E-Yacht — Gestione contabilità navi',
    'category': 'Accounting',
    'author': 'Progresso SRL',
    'website': 'https://www.progresso.srl',
    'depends': ['ey_base', 'report_py3o'],  # report_py3o: preventivo, consuntivo, richiesta fondi
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/report.xml',
        'data/ey_contabilita_navi_menu.xml',
        'data/ir_sequence.xml',
        'views/contratto_nave_view.xml',
        'views/previsionale_contratto_view.xml',
        'views/wizards/wiz_crea_prossimo_previsionale_view.xml',
        'views/wizards/wiz_collega_linea_spesa_nave_view.xml',
        'views/wizards/wiz_collega_linea_spesa_armatore_view.xml',
        'views/account/account_move_view.xml',
        'views/previsionale_spesa_view.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}