# -*- coding: utf-8 -*-
# © 2016 Apulia Software srl <info@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """Check invoice date consistency to ensure sequential numbering."""

    _inherit = 'account.move'

    def _post(self, soft=True):
        """Override _post to check date consistency before posting."""
        # Check date consistency before posting
        for move in self:
            # Only check for customer invoices and refunds
            if move.move_type in ('out_invoice', 'out_refund') and move.name and move.name != '/':
                # Search if exists a posted invoice with a later date but earlier number
                domain = [
                    ('move_type', '=', move.move_type),
                    ('invoice_date', '>', move.invoice_date),
                    ('name', '<', move.name),
                    ('journal_id', '=', move.journal_id.id),
                    ('state', '=', 'posted'),
                    ('id', '!=', move.id),
                ]
                if self.search(domain, limit=1):
                    raise UserError(
                        _('Cannot post invoice!\n'
                          'There is already a posted invoice with a later date '
                          'but an earlier number. Please post the invoice with '
                          'a greater date to maintain sequential order.'))
        
        return super()._post(soft=soft)
