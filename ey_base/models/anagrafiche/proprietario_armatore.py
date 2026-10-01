# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProprietarioArmatore(models.Model):
    _name = 'ey_base.proprietario_armatore'
    _description = 'Proprietario / Armatore nave'
    _order = 'data_inizio desc'

    nave_proprietario_id = fields.Many2one(
        comodel_name='ey_base.unita', string='Nave (come proprietario)', index=True, ondelete='cascade',
    )
    nave_armatore_id = fields.Many2one(
        comodel_name='ey_base.unita', string='Nave (come armatore)', index=True, ondelete='cascade',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Cognome e nome / Rag. sociale',
        required=True, index=True,
    )
    identificatore = fields.Char(string='Identificatore', index=True)
    data_inizio = fields.Date(string='Inizio', required=True)
    data_fine = fields.Date(string='Fine')
    carati = fields.Char(string='Carati')
    riferimento = fields.Boolean(string='Attivo', index=True, default=True)

    # ── campi calcolati per la vista dal partner ──────────────────────
    armatore_proprietario = fields.Char(
        string='Ruolo', compute='_compute_riepilogo_nave',
    )
    nave_name = fields.Char(string='Nave', compute='_compute_riepilogo_nave')
    nave_tipo_registro = fields.Char(string='Tipo registro', compute='_compute_riepilogo_nave')
    nave_nr_on = fields.Char(string='Nr. / O.N.', compute='_compute_riepilogo_nave')
    nave_porto = fields.Char(string='Porto', compute='_compute_riepilogo_nave')
    nave_bandiera = fields.Char(string='Bandiera', compute='_compute_riepilogo_nave')

    @api.depends('nave_proprietario_id', 'nave_armatore_id')
    def _compute_riepilogo_nave(self):
        for rec in self:
            nave = rec.nave_proprietario_id or rec.nave_armatore_id
            if rec.nave_proprietario_id:
                rec.armatore_proprietario = 'Proprietario'
            elif rec.nave_armatore_id:
                rec.armatore_proprietario = 'Armatore'
            else:
                rec.armatore_proprietario = False

            rec.nave_name = nave.name if nave else False
            rec.nave_tipo_registro = nave.tipo_registro_id.name if nave else False
            rec.nave_nr_on = nave.nr_on if nave else False
            rec.nave_porto = nave.porto_id.name if nave else False
            rec.nave_bandiera = nave.bandiera_id.name if nave else False
