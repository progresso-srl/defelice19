# DeFelice19 — E-Yacht su Odoo 19

Moduli Odoo 19 del gestionale E-Yacht (De Felice): anagrafiche nave,
contabilità navi, corsi ed esami del personale marittimo, pratiche marittime.
Migrazione da Odoo 8/12.

## Moduli

| Modulo | Che cosa fa | Dipende da |
|---|---|---|
| [`ey_base`](ey_base/) | Anagrafiche: navi (`ey_base.unita`), motori, apparati, certificati di bordo, equipaggio, proprietari e armatori, agenda scadenze nave. Il mixin per i documenti salvati come allegato | `account`, `mail` |
| [`ey_contabilita_navi`](ey_contabilita_navi/) | Contratti nave, previsionali per periodo, spese e anticipi armatore, collegamento delle righe contabili | `ey_base`, `report_py3o` |
| [`ey_corsi`](ey_corsi/) | Corsi ed esami: template, iscrizioni e preiscrizioni, attestati e certificati (report QWeb), agenda del marittimo, anagrafica marittimo sul partner (cognome/nome) | `account`, `ey_base` |
| [`ey_pratiche`](ey_pratiche/) | Pratiche marittime su nave o soggetto, template di pratica con documenti py3o, enti, normativa, follow up e alert | `mail`, `report_py3o`, `ey_base`, `ey_corsi` |
| [`ey_report`](ey_report/) | Opzione "saldo di periodo" sul Mastro generale OCA. **Oggi solo il campo**: i template sono da rifare (vedi sotto) | `account_financial_report`, `date_range` |
| [`account_invoice_sequential_dates`](account_invoice_sequential_dates/) | Blocca la registrazione di una fattura cliente con data precedente a una fattura con numero più basso dello stesso registro | `account` |

[`legacy/`](legacy/) contiene il codice Odoo 8/12 tenuto come riferimento per
la migrazione: Odoo lo ignora.

## Installazione

Il repo va nell'`addons_path`, insieme a OCA 19 (`reporting-engine` per
`report_py3o`, `account-financial-reporting`, `server-ux` per `date_range`).

```
task install DB_NAME=<database>     # installa i moduli
task update  DB_NAME=<database>     # aggiorna i moduli
task --list                         # tutti i comandi
```

Senza `task`: `odoo-bin -c odoo19.conf -d <database> -i
account_invoice_sequential_dates,ey_base,ey_contabilita_navi,ey_corsi,ey_pratiche,ey_report`.

## Diritti

Ogni modulo ha i suoi gruppi *Manager* e *User* (il Manager include lo User),
visibili nel form utente sotto la propria categoria. All'installazione
l'amministratore entra nei gruppi Manager.

## Punti aperti

- **Codice fiscale.** `ey_pratiche` e `ey_contabilita_navi` leggono
  `res.partner.fiscalcode`, che è di `l10n_it_fiscalcode` (OCA `l10n-italy`).
  Non è fra le dipendenze e non è nell'`addons_path` di Odoo 19, quindi oggi
  il codice fiscale nelle pratiche e nei previsionali resta vuoto. Se in
  produzione c'è `l10n-italy`, va aggiunto alle dipendenze dei due moduli.
- **Mastro generale.** I template di `ey_report` (colonne ridotte e saldo di
  periodo) erano quelli di OCA 12 e mandavano in errore la stampa del Mastro.
  Sono in `legacy/ey_report`, da rifare sui template di OCA 19.
- **Nave sulle righe contabili.** `ey_base/models/account/` (campo
  `unita_id` su fattura e righe, onchange del prodotto in stile Odoo 12) non
  è importato, e in `ey_contabilita_navi` la vista che lo usava è commentata.
  Da decidere se serve ancora.
- **Report py3o delle pratiche** e altri punti della migrazione di
  `ey_pratiche`: vedi [`ey_pratiche/MIGRATION_SUMMARY.md`](ey_pratiche/MIGRATION_SUMMARY.md).
