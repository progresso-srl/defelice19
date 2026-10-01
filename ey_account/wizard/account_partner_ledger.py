from openerp import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class AccountPartnerLedger(models.TransientModel):
    _inherit = 'account.partner.ledger'

    nave_id = fields.Many2one('ey.unita', String='Nave')

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        _logger.info('Context')
        _logger.info(context)
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['initial_balance', 'filter', 'page_split', 'amount_currency', 'nave_id'])[0])
        if data['form'].get('page_split') is True:
            return self.pool['report'].get_action(cr, uid, [], 'account.report_partnerledgerother', data=data,
                                                  context=context)
        _logger.info('Data')
        _logger.info(data)
        return self.pool['report'].get_action(cr, uid, [], 'ey_account.account_report_mastro', data=data, context=context)

    @api.onchange('nave_id')
    def _onchange_nave_id(self):
        partner_id = self.env.context.get('active_id')
        armatori = self.env['ey2.proprietario_armatore'].search([('partner_id', '=', partner_id)])
        navi_ids = []
        for armatore in armatori:
            navi_ids.append(armatore.nave_armatore_id.id)

        return {
            'domain': {
                'nave_id': [('id', 'in', navi_ids)]
            }
        }


