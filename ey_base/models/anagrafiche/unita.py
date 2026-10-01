# -*- coding: utf-8 -*-
from odoo import models, fields, api

_INFO_DOVUTE = [
    ('si', 'Sì'),
    ('no', 'No'),
    ('non_dovute', 'Non dovute'),
]


class Unita(models.Model):
    _name = 'ey_base.unita'
    _description = 'Unità navale'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'riferimento desc'

    # ── INTESTAZIONE ────────────────────────────────────────────────
    name = fields.Char(
        string='Nome', required=True, tracking=True,
    )
    riferimento = fields.Char(
        string='Riferimento', index=True, copy=False,
        readonly=True, default='Nuovo',
    )

    # ── INFO GENERALI ────────────────────────────────────────────────
    gestione_continuativa = fields.Boolean(
        string='Gestione continuativa', index=True, tracking=True,
    )
    bandiera_id = fields.Many2one(
        comodel_name='res.country', string='Bandiera',
        required=True, index=True, tracking=True,
    )
    porto_id = fields.Many2one(
        comodel_name='ey_base.porto', string='Porto di iscrizione',
        required=True, index=True,
    )
    nr_on = fields.Char(string='Nr. / O.N.', index=True)
    tipo_registro_id = fields.Many2one(
        comodel_name='ey_base.tipo_registro_unita', string='Tipo registro',
        required=True, index=True,
    )
    utilizzo_id = fields.Many2one(
        comodel_name='ey_base.utilizzo_nave', string='Utilizzo',
        required=True, index=True,
    )
    imo_nr = fields.Char(string='IMO Nr.', index=True)
    nominativo_interno = fields.Char(string='Nominativo internazionale', index=True)
    mmsi = fields.Char(string='MMSI', index=True)
    hin_cin = fields.Char(string='HIN / CIN', index=True)

    # dimensioni
    lunghezza = fields.Float(string='Lunghezza f.t. mt.', required=True, index=True)
    lunghezza_galleggiamento = fields.Float(string='Lunghezza al gallegg. mt.')
    lunghezza_mt = fields.Float(string='Larghezza mt.')
    pescaggio = fields.Float(string='Pescaggio mt.')
    stazza_lorda = fields.Float(string='Stazza lorda')
    stazza_netta = fields.Float(string='Stazza netta')
    dislocamento = fields.Float(string='Dislocamento')
    portata_max_kg = fields.Float(string='Portata max kg')

    # classificazione
    abbr_tipo_id = fields.Many2one(comodel_name='ey_base.abbr_tipo_nave', string='Abbr. tipo', index=True)
    limite_navigazione_id = fields.Many2one(comodel_name='ey_base.limite_navigazione', string='Limiti di navigazione', index=True)
    tipo_unita_id = fields.Many2one(comodel_name='ey_base.tipo_unita', string='Tipo', index=True)
    anno_costruzione = fields.Integer(string='Anno costr.', index=True)
    propulsione_id = fields.Many2one(comodel_name='ey_base.propulsione', string='Propulsione', index=True)
    tab_min_arm = fields.Float(string='Tab. min. arm.')
    nr_max_persone_trasportabili = fields.Integer(string='Nr max persone trasportabili')
    soggetto_fatturazione_id = fields.Many2one(comodel_name='res.partner', string='Soggetto fatturazione')

    # ── PROPRIETARI / ARMATORI / RAPPRESENTANTI ─────────────────────
    proprietario_ids = fields.One2many(
        comodel_name='ey_base.proprietario_armatore',
        inverse_name='nave_proprietario_id',
        string='Proprietari',
    )
    armatore_ids = fields.One2many(
        comodel_name='ey_base.proprietario_armatore',
        inverse_name='nave_armatore_id',
        string='Armatori',
    )
    rappresentante_ruolo_ids = fields.One2many(
        comodel_name='ey_base.rappresentante_ruolo',
        inverse_name='nave_id',
        string='Rappresentanti / altri ruoli',
    )

    # ── EQUIPAGGIO ───────────────────────────────────────────────────
    equipaggio_ids = fields.One2many(
        comodel_name='ey_base.equipaggio_nave',
        inverse_name='nave_id',
        string='Equipaggio',
    )

    # ── CONTATTI E RECAPITI ──────────────────────────────────────────
    contatto_nave_ids = fields.One2many(
        comodel_name='ey_base.contatto_nave',
        inverse_name='nave_id',
        string='Contatti operativi',
    )
    ulteriore_recapito_ids = fields.One2many(
        comodel_name='ey_base.ulteriore_recapito',
        inverse_name='nave_id',
        string='Ulteriori recapiti',
    )

    # ── DATI AMMINISTRATIVI (fatturazione) ───────────────────────────
    iva_id = fields.Many2one(comodel_name='account.tax', string='Regime IVA')
    periodicita_id = fields.Many2one(comodel_name='ey_base.periodo_fatturazione_nave', string='Periodicità')
    importo = fields.Float(string='Importo periodico')

    # ── GESTIONE PREVIDENZIALE / ASSICURAZIONI ───────────────────────
    # INPS
    inps = fields.Selection(selection=_INFO_DOVUTE, string='INPS', index=True)
    matricola_inps = fields.Char(string='Matricola INPS')
    password_inps = fields.Char(string='Password INPS')
    sede_inps = fields.Char(string='Sede INPS')
    # INAIL
    inail = fields.Selection(selection=_INFO_DOVUTE, string='INAIL', index=True)
    pam_inail = fields.Char(string='PAM')
    pin_pam_inail = fields.Char(string='PIN del PAM')
    certificato_inail = fields.Char(string='Certificato INAIL')
    # FANIMAR
    fanimar = fields.Selection(selection=_INFO_DOVUTE, string='FANIMAR', index=True)
    codice_ditta_fanimar = fields.Char(string='Codice ditta')
    password_fanimar = fields.Char(string='Password FANIMAR')
    nr_ass_fanimar = fields.Char(string='Nr assicurati')
    nr_deter_fanimar = fields.Char(string='Nr contratti determinati')
    nr_indet_fanimar = fields.Char(string='Nr contratti indeterminati')
    nr_comand_dir_mach_fanimar = fields.Char(string='Nr Comandanti + Dir. Macchina')
    nr_ufficiali_fanimar = fields.Char(string='Nr ufficiali')
    # adempimenti fiscali
    imposte = fields.Selection(selection=_INFO_DOVUTE, string='Imposte', index=True)
    stipendi = fields.Selection(selection=_INFO_DOVUTE, string='Stipendi', index=True)
    fatture = fields.Selection(selection=_INFO_DOVUTE, string='Fatture fornitori', index=True)
    # assicurazioni
    assicurazione_equipaggio = fields.Selection(selection=_INFO_DOVUTE, string='Ass. equipaggio', index=True)
    assicurazione_rc_terzi = fields.Selection(selection=_INFO_DOVUTE, string='Ass. RC terzi', index=True)
    assicurazione_pi = fields.Selection(selection=_INFO_DOVUTE, string='Ass. P&I', index=True)
    assicurazione_hm = fields.Selection(selection=_INFO_DOVUTE, string='Ass. H&M', index=True)
    assicurazione_corpi = fields.Selection(selection=_INFO_DOVUTE, string='Ass. corpi', index=True)
    assicurazione_tender = fields.Selection(selection=_INFO_DOVUTE, string='Ass. tender', index=True)

    # ── INFO VARIE ───────────────────────────────────────────────────
    epirb = fields.Boolean(string='EPIRB')
    gmdss = fields.Boolean(string='GMDSS')
    ssb = fields.Boolean(string='SSB')
    nr_componenti_equipaggio = fields.Integer(string='Nr componenti equipaggio')
    gest_stazione_radiotel = fields.Boolean(string='Gestione stazione radiotelef.')
    tipo_canone_id = fields.Many2one(comodel_name='ey_base.tipo_canone_rai', string='Tipo canone RAI', index=True)
    porto_base_id = fields.Many2one(comodel_name='ey_base.porto', string='Porto base (art.2 D.Lgs 171)', index=True)
    ente_sorveglianza_id = fields.Many2one(comodel_name='ey_base.ente_sorveglianza', string='Ente di sorveglianza')
    societa_concessionaria_id = fields.Many2one(comodel_name='ey_base.societa_concessionaria', string='Società concessionaria', index=True)
    porto_ormeggio_id = fields.Many2one(comodel_name='ey_base.porto', string='Porto di ormeggio', index=True)
    ente_classifica_id = fields.Many2one(comodel_name='ey_base.ente_sorveglianza', string='Ente di classifica')
    colore_scafo = fields.Char(string='Colore scafo')
    blacklist = fields.Boolean(string='Black list')
    note = fields.Text(string='Note')

    # ── CERTIFICATI DI BORDO ─────────────────────────────────────────
    certificato_bordo_ids = fields.One2many(
        comodel_name='ey_base.certificato_bordo',
        inverse_name='nave_id',
        string='Certificati di bordo',
    )

    # ── DOCUMENTI AMMINISTRATIVI ──────────────────────────────────────
    doc_amministrativi_ids = fields.One2many(
        comodel_name='ey_base.documento_partner',
        inverse_name='nave_id',
        string='Documenti amministrativi',
    )

    # ── APPARATI ELETTRONICI ──────────────────────────────────────────
    apparato_elettronico_ids = fields.One2many(
        comodel_name='ey_base.apparato_elettronico',
        inverse_name='nave_id',
        string='Apparati elettronici',
    )

    # ── SCHEDA TECNICA ────────────────────────────────────────────────
    modello = fields.Char(string='Modello')
    id_cantiere = fields.Char(string='Numero costruzione', index=True)
    ufficio = fields.Char(string='Ufficio', index=True)
    progettisti_interni = fields.Char(string='Progettisti interni')
    progettisti_esterni = fields.Char(string='Progettisti esterni')
    rnc = fields.Char(string='RNC')
    immersione_massima = fields.Float(string='Immersione massima mt.')
    immersione_minima = fields.Float(string='Immersione minima mt.')
    altezza = fields.Float(string='Altezza mt.')
    classe = fields.Char(string='Classe')
    compliance = fields.Char(string='Compliance')
    autonomia_miglia = fields.Float(string='Autonomia miglia nautiche')
    velocita_crociera = fields.Float(string='Velocità di crociera nodi')
    max_nodi = fields.Float(string='Velocità massima nodi')
    max_ospiti = fields.Integer(string='Nr max ospiti', index=True)
    costruttore_id = fields.Many2one(comodel_name='ey_base.costruttore', string='Costruttore', index=True)
    materiale_costruzione_id = fields.Many2one(comodel_name='ey_base.materiale_costruzione', string='Materiale costruzione', index=True)
    ente_id = fields.Many2one(comodel_name='ey_base.ente_sorveglianza', string='Ente (scheda tecnica)', index=True)
    # STED
    sted_nr_dci = fields.Char(string='Nr. DCI', index=True)
    sted_data_dci = fields.Date(string='Data DCI', index=True)
    sted_ente_rilascio = fields.Many2one(comodel_name='ey_base.ente_sorveglianza', string='Ente rilascio DCI')
    # Motori
    motore_nave_ids = fields.One2many(comodel_name='ey_base.motore_nave', inverse_name='nave_id', string='Motori')
    motori_modello = fields.Char(string='Modello motori')
    numero_motori = fields.Integer(string='Nr motori')
    marca_motori = fields.Char(string='Marca motori')
    kw_motori = fields.Float(string='KW per motore')
    alimentazione = fields.Char(string='Alimentazione')
    trasmissione = fields.Char(string='Trasmissione')
    invertitori = fields.Char(string='Invertitori / riduttori')
    ore_navigazione = fields.Float(string='Ore navigazione')
    consumo_orario = fields.Float(string='Consumo orario (litri/h)')
    numero_alberi_mq = fields.Float(string='Nr alberi')
    superficie_velica_mq = fields.Float(string='Superficie velica mq')
    # Generatori
    generatori_marca = fields.Char(string='Marca generatori')
    generatori_modello = fields.Char(string='Modello generatori')
    generatori_potenza = fields.Float(string='Potenza generatori kw')
    generatori_volts = fields.Float(string='Volt generatori')
    generatori_fasi = fields.Integer(string='Fasi generatori')
    generatori_frequenza = fields.Float(string='Frequenza generatori Hz')
    # Batterie
    nr_batterie_principali = fields.Integer(string='Nr batterie principali')
    volts_batterie_principali = fields.Float(string='Volt batterie principali')
    ah_batterie_principali = fields.Float(string='Ah batterie principali')
    nr_batterie_generatori = fields.Integer(string='Nr batterie generatori')
    volts_batterie_generatori = fields.Float(string='Volt batterie generatori')
    ah_batterie_generatori = fields.Float(string='Ah batterie generatori')
    nr_batterie_servizi = fields.Integer(string='Nr batterie servizi')
    volts_batterie_servizi = fields.Float(string='Volt batterie servizi')
    ah_batterie_servizi = fields.Float(string='Ah batterie servizi')
    nr_batterie_emergenza = fields.Integer(string='Nr batterie emergenza')
    volts_batterie_emergenza = fields.Float(string='Volt batterie emergenza')
    ah_batterie_emergenza = fields.Float(string='Ah batterie emergenza')
    # Macchinari ausiliari
    volts_alimentazione_terra = fields.Integer(string='Volt alimentazione da terra')
    fasi_alimentazione_terra = fields.Float(string='Fasi alimentazione da terra')
    frequenza_alimentazione_terra = fields.Float(string='Frequenza alimentazione da terra')
    sep_olio_marca = fields.Char(string='Marca separatore olio')
    sep_olio_modello = fields.Char(string='Modello separatore olio')
    dep_carburante_marca = fields.Char(string='Marca depuratore carburante')
    dep_carburante_modello = fields.Char(string='Modello depuratore carburante')
    save_system_marca = fields.Char(string='Marca sewage system')
    save_system_modello = fields.Char(string='Modello sewage system')
    elica_prua_marca = fields.Char(string='Marca elica di prua')
    elica_prua_modello = fields.Char(string='Modello elica di prua')
    dissalatore_marca = fields.Char(string='Marca dissalatore')
    dissalatore_modello = fields.Char(string='Modello dissalatore')
    ac_marca = fields.Char(string='Marca aria condizionata')
    ac_modello = fields.Char(string='Modello aria condizionata')
    # Capacità casse
    litri_carburante = fields.Float(string='Carburante litri')
    litri_acqua = fields.Float(string='Acqua litri')
    litri_olio_lubr = fields.Float(string='Olio lubrificante litri')
    litri_olio_esausto = fields.Float(string='Olio esausto litri')
    # Info commerciali
    prezzo_richiesto_vendita = fields.Monetary(string='Prezzo richiesto vendita', currency_field='currency_id')
    prezzo_richiesto_noleggio = fields.Monetary(string='Prezzo richiesto noleggio', currency_field='currency_id')
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Valuta',
        default=lambda self: self.env.company.currency_id,
    )
    iva_assolta = fields.Boolean(string='IVA assolta')
    note_scheda_tecnica = fields.Text(string='Note scheda tecnica')

    # ── ADEMPIMENTI ───────────────────────────────────────────────────
    adempimenti = fields.Many2many(
        comodel_name='ey_base.adempimento_nave',
        relation='ey_base_unita_adempimenti_rel',
        string='Adempimenti',
    )

    # ── STORICI ───────────────────────────────────────────────────────
    storico_nome_ids = fields.One2many(
        comodel_name='ey_base.storico_nave', inverse_name='nave_id',
        string='Storico nomi', domain=[('nome', '!=', False)],
    )
    storico_porto_ids = fields.One2many(
        comodel_name='ey_base.storico_nave', inverse_name='nave_id',
        string='Storico porti iscrizione', domain=[('porto_id', '!=', False)],
    )
    storico_nr_on_ids = fields.One2many(
        comodel_name='ey_base.storico_nave', inverse_name='nave_id',
        string='Storico Nr. / O.N.', domain=[('nr_on', '!=', False)],
    )
    storico_bandiera_ids = fields.One2many(
        comodel_name='ey_base.storico_nave', inverse_name='nave_id',
        string='Storico bandiere', domain=[('bandiera_id', '!=', False)],
    )

    # ── SEQUENCE ─────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('riferimento', 'Nuovo') == 'Nuovo':
                vals['riferimento'] = self.env['ir.sequence'].next_by_code(
                    'ey_base.riferimento_nave'
                ) or 'Nuovo'
        return super().create(vals_list)


class StoricoNave(models.Model):
    _name = 'ey_base.storico_nave'
    _description = 'Storico variazioni nave'
    _order = 'data_inizio desc'

    nave_id = fields.Many2one(comodel_name='ey_base.unita', index=True, ondelete='cascade')
    nome = fields.Char(string='Nome', index=True)
    porto_id = fields.Many2one(comodel_name='ey_base.porto', string='Porto di iscrizione', index=True)
    nr_on = fields.Char(string='Nr. / O.N.', index=True)
    bandiera_id = fields.Many2one(comodel_name='res.country', string='Bandiera', index=True)
    data_inizio = fields.Date(string='Inizio')
    data_fine = fields.Date(string='Fine')
