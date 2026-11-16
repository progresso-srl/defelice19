# -*- coding: utf-8 -*-
# © 2016 Apulia Software srl <info@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """Check invoice date consistency to ensure sequential numbering."""

    _inherit = 'account.move'

    def _post(self, soft=True):
        # In Odoo 19 la fattura prende il numero dentro _post: il controllo va
        # fatto dopo, quando il numero c'e'. Prima lo si faceva prima di
        # super() e non scattava mai, perche' la bozza non ha numero. L'errore
        # annulla anche la registrazione.
        posted = super()._post(soft=soft)
        for move in posted.filtered(
                lambda m: m.move_type in ('out_invoice', 'out_refund')
                and m.sequence_prefix and m.invoice_date):
            later = self.search([
                ('move_type', '=', move.move_type),
                ('journal_id', '=', move.journal_id.id),
                ('sequence_prefix', '=', move.sequence_prefix),
                ('sequence_number', '<', move.sequence_number),
                ('invoice_date', '>', move.invoice_date),
                ('state', '=', 'posted'),
                ('id', '!=', move.id),
            ], limit=1)
            if later:
                raise UserError(_(
                    'Cannot post invoice %(move)s!\n'
                    'Invoice %(later)s has an earlier number but a later date '
                    '(%(date)s). Please post the invoice with a date not '
                    'earlier than %(date)s to keep the numbering sequential.',
                    move=move.name, later=later.name,
                    date=later.invoice_date.strftime('%d/%m/%Y')))
        return posted
