# -*- coding: utf-8 -*-
##############################################################################
#
#    CASE module for OpenERP
#    Copyright (C) 20013 Future Tech srl (http://www.futuretechsrl.it).
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

from openerp import api, fields, models
from ..vendor import ey2_utils


class UfficioEmissioneNormativa(models.Model):
    _name = "ey2.ue_normativa"

    name = fields.Char(string="Ufficio emissione", index=True, required=True)



class TipoNormativa(models.Model):
    _name = "ey2.tipo_normativa"

    name = fields.Char(string="Tipologia", index=True, required=True)


class AmbitoNormativa(models.Model):
    _name = "ey2.ambito_normativa"

    name = fields.Char(string="Ambito", index=True, required=True)


class CategoriaNormativa(models.Model):
    _name = "ey2.categoria_normativa"

    name = fields.Char(string="Categoria", index=True, required=True)


class NaturaNormativa(models.Model):
    _name = "ey2.natura_normativa"

    name = fields.Char(string="Natura provvedimento", index=True, required=True)


class AllegatoNormativa(models.Model):
    _name = "ey2.allegato_normativa"

    ##### FUNZIONI PER IL SET E IL GET DEL BINARY
    @api.multi
    def _get_document(self):
        ids = []
        for rec in self:
            ids.append(rec.id)
        ir_attachment_model = self.env['ir.attachment']
        domain_attachment = [('res_model', '=', self._name), ('res_id', 'in', ids)]
        attachments = ir_attachment_model.search(domain_attachment)
        for att in attachments:
            for rec in self:
                if rec.id == att.res_id:
                    rec.document = att.datas
                    break

    @api.one
    def _set_document(self):
        ir_attachment_model = self.env['ir.attachment']
        dati = {
            'name': 'allegato_normativa_' + str(self.id),
            'datas_fname': 'allegato_normativa' + str(self.id),
            'res_model': self._name,
            'res_id': self.id,
            'datas': self.document
        }
        attachments = ir_attachment_model.search([('res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments:
            return attachments.write(dati)
        else:
            return ir_attachment_model.create(dati)

    name = fields.Char(string="Descrizione", required=True, index=True)
    normativa_id = fields.Many2one("ey2.normativa", index=True)
    document = fields.Binary(compute="_get_document", inverse="_set_document", string="Documento")
    document_fname = fields.Char(string="File name")


class Normativa(models.Model):
    _name = "ey2.normativa"
    _order = 'data_provvedimento desc'

    @api.depends('natura_id', 'natura_id.name', 'numero_provvedimento', 'data_provvedimento', 'testo_descrittivo')
    def _compute_name(self):
        for normativa in self:
            name = ""
            if normativa.natura_id:
                name += normativa.natura_id.name
            if normativa.numero_provvedimento:
                name += " - " + normativa.numero_provvedimento
            if normativa.data_provvedimento:
                name += " - " + ey2_utils.format_date(normativa.data_provvedimento)
            if normativa.testo_descrittivo:
                name += " - " + normativa.testo_descrittivo
            normativa.name = name

    name = fields.Char(string="Nome", index=True, compute="_compute_name", store=True)
    tipo_id = fields.Many2one("ey2.tipo_normativa", string="Tipologia", index=True, required=True)
    ambito_id = fields.Many2one("ey2.ambito_normativa", string="Ambito", index=True)
    categoria_id = fields.Many2one("ey2.categoria_normativa", string="Categoria", index=True)
    natura_id = fields.Many2one("ey2.natura_normativa", string="Natura", index=True)
    documento_ids = fields.One2many("ey2.allegato_normativa", "normativa_id", string="Allegati")
    data_provvedimento = fields.Date(string="Data provvedimento", index=True)
    numero_provvedimento = fields.Char(string="Numero provvedimento", index=True, size=15)
    note = fields.Text(string="Note")
    normative_collegate = fields.Many2many(comodel_name="ey2.normativa", relation="ey2_normative_collegate_rel", column1="normativa1_id",
                                           column2="normativa2_id", string="Normative collegate", index=True)
    #campi sito
    pubblicato = fields.Boolean(string="Pubblicato sul sito", index=True)
    titolo_sito = fields.Char(string="Titolo per sito")
    descrizione_sito = fields.Text(string="Descrizione per sito")
    #aggiunte campi
    testo_descrittivo = fields.Char(string="Testo descrittivo", index=True)
    ufficio_emissione_id = fields.Many2one("ey2.ue_normativa", string="Ufficio emissione", index=True)
    attivo = fields.Boolean(string="Attivo", default=True, index=True)

    @api.model
    def create(self, vals):
        normativa = super(Normativa, self).create(vals)
        if 'normative_collegate' in vals:
            for nc in normativa.normative_collegate:
                query = "INSERT INTO ey2_normative_collegate_rel (normativa1_id, normativa2_id) VALUES (" + str(nc.id) + ", " + str(normativa.id) + ")"
                self.env.cr.execute(query)
        return normativa

    @api.multi
    def write(self, vals):
        for n in self:
            if 'normative_collegate' in vals:
                nc_copy = []
                for nc_id in vals['normative_collegate'][0][2]:
                    nc_copy.append(nc_id)
                for nc in n.normative_collegate:
                    if nc.id in nc_copy:
                        nc_copy.remove(nc.id)
                        continue
                    else:
                        query = "DELETE FROM ey2_normative_collegate_rel WHERE normativa1_id=" + str(nc.id) + " AND normativa2_id=" + str(n.id)
                        self.env.cr.execute(query)
                for nc_id in nc_copy:
                    query = "INSERT INTO ey2_normative_collegate_rel (normativa1_id, normativa2_id) VALUES (" + str(nc_id) + ", " + str(n.id) + ")"
                    self.env.cr.execute(query)
        return super(Normativa, self).write(vals)

    @api.multi
    def unlink(self):
        for p in self:
            for nc in p.normative_collegate:
                query = "DELETE FROM ey2_normative_collegate_rel WHERE normativa1_id=" + str(nc.id) + " AND normativa2_id=" + str(p.id)
                self.env.cr.execute(query)
        return super(Normativa, self).unlink()
