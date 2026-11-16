# -*- coding: utf-8 -*-
from odoo import fields, models


class DocumentoAllegatoMixin(models.AbstractModel):
    """Un documento salvato come ir.attachment del record.

    Prima era copiato in ogni modello (contratti, anticipi armatore,
    allegati normativa) con l'API di Odoo 12: ``datas_fname``, che non esiste
    piu', e un progressivo preso con ``max(id)`` dalla tabella sbagliata.
    L'allegato e' legato al record con ``res_model``/``res_id`` e senza
    ``res_field``, come i dati gia' migrati.
    """
    _name = "ey_base.documento_allegato_mixin"
    _description = "Documento salvato come allegato"

    # Il nome dell'allegato quando manca il nome del file.
    _ey_document_prefix = "documento"

    document = fields.Binary(
        string="Documento", compute="_compute_document", inverse="_inverse_document")
    document_fname = fields.Char(string="File name")

    def _ey_document_attachments(self):
        return self.env["ir.attachment"].search([
            ("res_model", "=", self._name),
            ("res_id", "in", self.ids),
            ("res_field", "=", False),
        ])

    def _compute_document(self):
        per_record = {}
        for att in self._ey_document_attachments():
            per_record.setdefault(att.res_id, att)
        for rec in self:
            att = per_record.get(rec.id)
            rec.document = att.datas if att else False

    def _inverse_document(self):
        attachments = self._ey_document_attachments()
        for rec in self:
            mine = attachments.filtered(lambda a, rec=rec: a.res_id == rec.id)
            if not rec.document:
                mine.unlink()
                continue
            vals = {
                "name": rec.document_fname or "%s_%s" % (self._ey_document_prefix, rec.id),
                "datas": rec.document,
            }
            if mine:
                mine.write(vals)
            else:
                self.env["ir.attachment"].create(
                    dict(vals, res_model=self._name, res_id=rec.id))
