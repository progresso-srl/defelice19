# -*- coding: utf-8 -*-

from odoo import Command, api, fields, models
from ..vendor import ey_pratiche_utils

class EyPraticheNormativa(models.Model):
    _name = "ey_pratiche.normativa"    
    _description = "Normativa"
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
                name += " - " + ey_pratiche_utils.format_date(normativa.data_provvedimento)
            if normativa.testo_descrittivo:
                name += " - " + normativa.testo_descrittivo
            normativa.name = name

    name = fields.Char(string="Nome", index=True, compute="_compute_name", store=True)
    # tipo_id = fields.Many2one("ey_pratiche.tipo_normativa", string="Tipologia")
    argomento_id = fields.Many2one("ey_pratiche.argomento_normativa", string="Argomento", index=True, required=True)
    ambito_id = fields.Many2one("ey_pratiche.ambito_normativa", string="Ambito", index=True, required=True)
    categoria_id = fields.Many2one("ey_pratiche.categoria_normativa", string="Categoria", index=True)
    natura_id = fields.Many2one("ey_pratiche.natura_normativa", string="Natura", index=True)
    documento_ids = fields.One2many("ey_pratiche.allegato_normativa", "normativa_id", string="Allegati")
    data_provvedimento = fields.Date(string="Data provvedimento", index=True)
    numero_provvedimento = fields.Char(string="Numero provvedimento", index=True, size=15)
    note = fields.Text(string="Note")
    normative_collegate = fields.Many2many(comodel_name="ey_pratiche.normativa", relation="ey_pratiche_normative_collegate_rel", column1="normativa1_id",
                                           column2="normativa2_id", string="Normative collegate", index=True)
    #campi sito
    pubblicato = fields.Boolean(string="Pubblicato sul sito", index=True)
    titolo_sito = fields.Char(string="Titolo per sito")
    descrizione_sito = fields.Text(string="Descrizione per sito")
    #aggiunte campi
    testo_descrittivo = fields.Char(string="Testo descrittivo", index=True)
    ufficio_emissione_id = fields.Many2one("ey_pratiche.ue_normativa", string="Ufficio emissione", index=True)
    attivo = fields.Boolean(string="Attivo", default=True, index=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        normative = super().create(vals_list)
        for normativa, vals in zip(normative, vals_list):
            if 'normative_collegate' in vals:
                normativa._ey_sincronizza_collegate({normativa.id: set()})
        return normative

    def write(self, vals):
        prima = {n.id: set(n.normative_collegate.ids) for n in self} if 'normative_collegate' in vals else None
        res = super().write(vals)
        if prima is not None:
            self._ey_sincronizza_collegate(prima)
        return res

    def _ey_sincronizza_collegate(self, prima):
        """Rende simmetrico il collegamento fra normative.

        ``prima``: {id normativa: set degli id collegati prima della modifica}.
        Se A collega B, anche B collega A; se A scollega B, anche B scollega
        A. Prima lo faceva SQL scritto a mano sulla tabella di relazione; le
        righe di una normativa cancellata le toglie il database (cascade).
        """
        if self.env.context.get('ey_sync_collegate'):
            return
        altre = self.with_context(ey_sync_collegate=True)
        for n in self:
            dopo = set(n.normative_collegate.ids)
            before = prima.get(n.id, set())
            for nid in dopo - before:
                altre.browse(nid).write({'normative_collegate': [Command.link(n.id)]})
            for nid in before - dopo:
                altre.browse(nid).write({'normative_collegate': [Command.unlink(n.id)]})


class UfficioEmissioneNormativa(models.Model):
    _name = "ey_pratiche.ue_normativa"
    _description = "Ue normativa"

    name = fields.Char(string="Ufficio emissione", index=True, required=True)



# class TipoNormativa(models.Model):
#     _name = "ey_pratiche.tipo_normativa"

#     name = fields.Char(string="Tipologia", index=True, required=True)


    
class AmbitoNormativa(models.Model):
    _name = "ey_pratiche.ambito_normativa"
    _description = "Ambito normativa"

    name = fields.Char(string="Ambito", index=True, required=True)


class CategoriaNormativa(models.Model):
    _name = "ey_pratiche.categoria_normativa"
    _description = "Categoria normativa"

    name = fields.Char(string="Categoria", index=True, required=True)


class NaturaNormativa(models.Model):
    _name = "ey_pratiche.natura_normativa"
    _description = "Natura normativa"

    name = fields.Char(string="Natura provvedimento", index=True, required=True)

class AllegatoNormativa(models.Model):
    _name = "ey_pratiche.allegato_normativa"
    _description = "Allegato normativa"
    _inherit = ["ey_base.documento_allegato_mixin"]
    _ey_document_prefix = "allegato_normativa"

    name = fields.Char(string="Descrizione", required=True, index=True)
    normativa_id = fields.Many2one("ey_pratiche.normativa", index=True)
    evidenza = fields.Boolean(string="In evidenza")
    
    