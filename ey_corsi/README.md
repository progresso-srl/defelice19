# ey_corsi

Corsi ed esami per il personale marittimo.

- **Soggetti → Marittimi / Personale docente**: il partner diventa
  un'anagrafica del marittimo (cognome e nome, codice IAMI, qualifica,
  cittadinanza, nascita, documenti, CV, certificati, esperienze, privacy).
- **Gestione corsi** ed **esami**: template, corsi ed esami, preiscrizioni e
  iscrizioni, costi, personale, documenti.
- **Gestione certificati/attestati**: attestati di frequenza e certificati
  d'esame, stampati con report QWeb, e certificati esterni.
- **Agenda marittimo**: le scadenze del marittimo. I certificati entrano in
  agenda da soli.

## Cognome e nome

Sul partner il nome completo è *cognome nome*. Un partner creato con il solo
`name` (da Odoo o da altri moduli) prende il nome come cognome. Il cognome è
obbligatorio nel form dei contatti, non sul modello: sul modello bloccava gli
indirizzi senza nome e l'installazione su un database con partner esistenti.
All'installazione i partner che esistono già prendono il nome come cognome.
