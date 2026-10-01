# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # fields Many2one
    unita_id = fields.Many2one(comodel_name='ey_base.unita', string='Unità')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Override per mantenere compatibilità con logica Odoo 12"""
        domain = {}
        
        if not self.move_id:
            return
        
        move = self.move_id
        partner = move.partner_id
        fiscal_position = move.fiscal_position_id
        company = move.company_id
        currency = move.currency_id
        move_type = move.move_type

        if not partner:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a partner.'),
            }
            return {'warning': warning}

        if not self.product_id:
            if move_type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['product_uom_id'] = []
            if fiscal_position:
                self.account_id = fiscal_position.map_account(self.account_id)
        else:
            self_lang = self
            if partner.lang:
                self_lang = self.with_context(lang=partner.lang)

            product = self_lang.product_id
            
            # In Odoo 19, l'account viene gestito diversamente
            if move_type in ('out_invoice', 'out_refund'):
                account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
            else:
                account = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id
                
            if fiscal_position and account:
                account = fiscal_position.map_account(account)
            
            if account:
                self.account_id = account.id

            # Imposta le tasse
            if move_type in ('out_invoice', 'out_refund'):
                self.tax_ids = product.taxes_id.filtered(lambda t: t.company_id == company)
            else:
                self.tax_ids = product.supplier_taxes_id.filtered(lambda t: t.company_id == company)
            
            if fiscal_position:
                self.tax_ids = fiscal_position.map_tax(self.tax_ids)

            if not self.name:
                if product.description_sale and move_type in ('out_invoice', 'out_refund'):
                    self.name = product.description_sale
                elif product.description_purchase and move_type in ('in_invoice', 'in_refund'):
                    self.name = product.description_purchase
                else:
                    self.name = product.display_name

            if not self.product_uom_id or product.uom_id.category_id.id != self.product_uom_id.category_id.id:
                self.product_uom_id = product.uom_id.id
            
            domain['product_uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:
                if self.product_uom_id and self.product_uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.product_uom_id)
        
        return {'domain': domain}
