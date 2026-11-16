# ey_pratiche

Le pratiche marittime, su una nave o su un soggetto.

- **Configuratore pratiche**: i template di pratica, con le chiavi da
  compilare e i documenti py3o da stampare. Per ogni documento del template
  nasce un report.
- **Pratiche**: alla creazione la pratica copia dal template chiavi e report,
  e dalla nave o dal soggetto i dati che servono ai documenti (registro,
  porto, proprietari, armatori, equipaggio, dati del marittimo). Poi stati,
  enti coinvolti, allegati, attività, follow up e alert (con un cron).
- **Gestione normative**: provvedimenti con allegati e normative collegate.

Il collegamento fra pratiche, e quello fra normative, vale nei due versi: se
A collega B anche B collega A, e scollegando o cancellando sparisce da tutte
e due. Prima lo faceva SQL scritto a mano; ora lo fa l'ORM.

Una pratica su una nave o un soggetto in black list non si salva.

## Dipendenze

`ey_corsi` serve perché la pratica legge cognome, nome, stato civile e
cittadinanza del partner. Il codice fiscale (`fiscalcode`) è di
`l10n_it_fiscalcode`, che non è fra le dipendenze: senza quel modulo resta
vuoto. Vedi i punti aperti nel README del repo.

Lo stato della migrazione e le cose da fare sono in
[`MIGRATION_SUMMARY.md`](MIGRATION_SUMMARY.md).
