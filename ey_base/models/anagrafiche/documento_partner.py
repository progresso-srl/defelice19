# -*- coding: utf-8 -*-
from odoo import models, fields


class DocumentoPartner(models.Model):
    _name = 'ey_base.documento_partner'
    _description = 'Documento amministrativo partner / nave'
    _order = 'data_inserimento desc'

    partner_id = fields.Many2one('res.partner', index=True)
    nave_id = fields.Many2one('ey_base.unita', index=True, ondelete='cascade')
    name = fields.Char(string='Descrizione', required=True, index=True)
    data_inserimento = fields.Date(string='Data inserimento', default=fields.Date.today)
    data_documento = fields.Date(string='Data documento')

    # attachment=True: Odoo 13+ gestisce store/retrieve automaticamente
    document = fields.Binary(string='Documento', attachment=True)
    document_fname = fields.Char(string='Nome file')
