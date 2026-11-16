# ey_base

Le anagrafiche di E-Yacht. Crea il menu **E-Yacht** e i gruppi *Manager* e
*Utente*.

- **Unità navali** (`ey_base.unita`): dati della nave, registro, porto,
  bandiera, motori, apparati elettronici, certificati di bordo, equipaggio,
  storico, soggetto di fatturazione, black list.
- **Armatori / Proprietari** e **Altri soggetti**: proprietari, armatori e
  rappresentanti della nave, contatti, recapiti, documenti del partner.
- **Adempimenti** e **Agenda → Scadenze navi**: l'agenda delle scadenze
  della nave. I certificati di bordo con scadenza entrano in agenda da soli.
- Le tabelle di supporto (tipi unità, porti, costruttori, enti di
  sorveglianza, ...).

## Documenti come allegato

`ey_base.documento_allegato_mixin` dà a un modello i campi `document` e
`document_fname`. Il file è salvato come `ir.attachment` del record, con il
nome del file. Lo usano i documenti dei contratti e gli anticipi armatore
(`ey_contabilita_navi`) e gli allegati della normativa (`ey_pratiche`).
Prima ogni modello aveva una copia con l'API di Odoo 12, che non funzionava più.

## Da sapere

`models/account/` (nave sulle fatture e sulle righe, onchange del prodotto in
stile Odoo 12) **non è importato**: vedi i punti aperti nel README del repo.
