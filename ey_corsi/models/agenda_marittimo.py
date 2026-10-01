# -*- coding: utf-8 -*-
from odoo import models, fields


class AgendaMarittimo(models.Model):
    _name = 'ey_corsi.agenda_marittimo'
    _description = 'Agenda scadenze marittimo'
    _rec_name = 'name'
    _order = 'data_scadenza desc'

    name = fields.Char(string='Descrizione', required=True, index=True)
    categoria_id = fields.Many2one(
        'ey_corsi.categoria_agenda_marittimo', string='Categoria',
        required=True, index=True,
    )
    categoria_name = fields.Char(
        string='Nome categoria', related='categoria_id.name', store=True,
    )
    # uniq_id: chiave esterna usata dai moduli che creano voci agenda in modo automatico
    uniq_id = fields.Char(index=True)
    data_scadenza = fields.Date(string='Data scadenza', required=True, index=True)
    data_alert = fields.Date(string='Data alert', required=True, index=True)
    in_consegna = fields.Boolean(string='Preso in consegna', index=True)
    completato = fields.Boolean(string='Completato', index=True)


class CategoriaAgendaMarittimo(models.Model):
    _name = 'ey_corsi.categoria_agenda_marittimo'
    _description = 'Categoria agenda marittimo'
    _rec_name = 'name'

    name = fields.Char(string='Categoria', required=True, index=True)
