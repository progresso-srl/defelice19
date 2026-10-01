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
    'name': 'E-Yacht Pratiche navi',
    'version': '1.0',
    'category': 'Yachts',
    'summary': 'Gestione di navi, equipaggi e pratiche correlate',
    'description': "Gestione navi, armatori, proprietari, equipaggi e setting custom di pratiche correlate",
    'author': 'Progresso S.r.l.',
    'depends': ['config_tpl', 'ey'],
    'data': [
        #GENERALE
        'ey2.xml',
        'ey2_data.xml',
        'ey2_menuitems.xml',
        #BASE
        'base/res_partner_view.xml',
        'base/ey2_follow_up_marittimo.xml',
        'base/ey2_adempimenti_marittimo_view.xml',
        #NAVE
        'nave/ey2_rappresentante_armatore_view.xml',
        'nave/ey2_unita_view.xml',
        'nave/ey2_immagine_nave_view.xml',
        'nave/ey2_scadenza_nave_view.xml',
        'nave/ey2_follow_up_nave_view.xml',
        'nave/ey2_adempimenti_nave_view.xml',
        #PRATICA
        'pratica/config_tpl_tpl_navi_view.xml',
        'pratica/config_tpl_tpl_soggetti_view.xml',
        'pratica/ey2_documento_partner_view.xml',
        'pratica/config_tpl_pratica_view.xml',
        'pratica/config_tpl_pratica_soggetto_view.xml',
        'pratica/ey2_ente_view.xml',
        'pratica/ey2_follow_up_pratica_view.xml',
        #EY
        'ey/ey_template_corso_view.xml',
        'ey/ey_corso_view.xml',
        'ey/ey_iscrizione_view.xml',
        'ey/ey2_pre_iscrizione_view.xml',
        'ey/ey2_pre_iscrizione_esame_view.xml',
        #NORMATIVA
        'normativa/ey2_normativa_view.xml',
        #SALDO NAVI
        'saldo_navi/ey2_previsionale_nave_view.xml',
        'saldo_navi/ey2_contratto_nave_view.xml',
        #WIZARDS
        'wizards/add_soggetto_pratica_view.xml',
        'wizards/add_soggetto_pratica_soggetto_view.xml',
        'wizards/crea_prossimo_previsionale_view.xml',
        #SCHEDULER
        'ey2_scheduler.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}
