# -*- coding: utf-8 -*-
from odoo import models, fields


class Porto(models.Model):
    _name = 'ey_base.porto'
    _description = 'Porto'
    _rec_name = 'name'

    name = fields.Char(string='Porto', required=True, index=True)


class TipoRegistroUnita(models.Model):
    _name = 'ey_base.tipo_registro_unita'
    _description = 'Tipo registro unità navale'
    _rec_name = 'name'

    name = fields.Char(string='Tipo registro', required=True, index=True)


class UtilizzoNave(models.Model):
    _name = 'ey_base.utilizzo_nave'
    _description = 'Utilizzo nave'
    _rec_name = 'name'

    name = fields.Char(string='Utilizzo', required=True, index=True)


class TipoUnita(models.Model):
    _name = 'ey_base.tipo_unita'
    _description = 'Tipo unità navale'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class AbbrTipoNave(models.Model):
    _name = 'ey_base.abbr_tipo_nave'
    _description = 'Abbreviazione tipo nave'
    _rec_name = 'name'

    name = fields.Char(string='Abbreviazione', required=True, index=True)


class LimiteNavigazione(models.Model):
    _name = 'ey_base.limite_navigazione'
    _description = 'Limite di navigazione'
    _rec_name = 'name'

    name = fields.Char(string='Limite', required=True, index=True)


class Propulsione(models.Model):
    _name = 'ey_base.propulsione'
    _description = 'Tipo propulsione'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class PeriodoFatturazioneNave(models.Model):
    _name = 'ey_base.periodo_fatturazione_nave'
    _description = 'Periodicità fatturazione nave'
    _rec_name = 'name'

    name = fields.Char(string='Periodicità', required=True, index=True)


class TipoCanoneRai(models.Model):
    _name = 'ey_base.tipo_canone_rai'
    _description = 'Tipo canone RAI'
    _rec_name = 'name'

    name = fields.Char(string='Tipo canone', required=True, index=True)


class EnteSorveglianza(models.Model):
    _name = 'ey_base.ente_sorveglianza'
    _description = 'Ente di sorveglianza / classifica'
    _rec_name = 'name'

    name = fields.Char(string='Ente', required=True, index=True)


class SocietaConcessionaria(models.Model):
    _name = 'ey_base.societa_concessionaria'
    _description = 'Società concessionaria'
    _rec_name = 'name'

    name = fields.Char(string='Società', required=True, index=True)


class Costruttore(models.Model):
    _name = 'ey_base.costruttore'
    _description = 'Costruttore navale'
    _rec_name = 'name'

    name = fields.Char(string='Nome', required=True, index=True)


class MaterialeCostruzione(models.Model):
    _name = 'ey_base.materiale_costruzione'
    _description = 'Materiale di costruzione scafo'
    _rec_name = 'name'

    name = fields.Char(string='Materiale', required=True, index=True)


class AdempimentoNave(models.Model):
    _name = 'ey_base.adempimento_nave'
    _description = 'Adempimento nave'
    _rec_name = 'name'

    name = fields.Char(string='Descrizione', required=True, index=True)
    tipo_id = fields.Many2one(
        comodel_name='ey_base.tipo_adempimento_nave',
        string='Tipo',
        index=True,
    )


class TipoAdempimentoNave(models.Model):
    _name = 'ey_base.tipo_adempimento_nave'
    _description = 'Tipo adempimento nave'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class RuoloRappresentante(models.Model):
    _name = 'ey_base.ruolo_rappresentante'
    _description = 'Ruolo rappresentante'
    _rec_name = 'name'

    name = fields.Char(string='Ruolo', required=True, index=True)


class TipoContatto(models.Model):
    _name = 'ey_base.tipo_contatto'
    _description = 'Tipo contatto nave'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class TipoRecapito(models.Model):
    _name = 'ey_base.tipo_recapito'
    _description = 'Tipo recapito'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class TipoCertBordo(models.Model):
    _name = 'ey_base.tipo_cert_bordo'
    _description = 'Tipo certificato di bordo'
    _rec_name = 'name'

    name = fields.Char(string='Tipo', required=True, index=True)


class TipoAppElett(models.Model):
    _name = 'ey_base.tipo_app_elett'
    _description = 'Tipo apparato elettronico'
    _rec_name = 'name'

    name = fields.Char(string='Apparato', required=True, index=True)


class MarcaAppElett(models.Model):
    _name = 'ey_base.marca_app_elett'
    _description = 'Marca apparato elettronico'
    _rec_name = 'name'

    name = fields.Char(string='Marca', required=True, index=True)
