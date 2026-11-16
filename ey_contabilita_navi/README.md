# ey_contabilita_navi

La contabilità delle navi in gestione. Menu **Gestione navi**.

- **Contratti nave**: nave, soggetto di riferimento, periodicità dei
  previsionali, saldo iniziale e saldo attuale, documenti. Il nome è
  progressivo più nome del contratto.
- **Previsionali** del contratto, uno per periodo, con le spese previste e
  gli anticipi dell'armatore. Il wizard *Crea prossimo previsionale* apre il
  periodo successivo.
- **Collegamento contabile**: da una fattura o scrittura si collega una
  riga a una spesa del previsionale o a un anticipo armatore (wizard
  *Collega linea spesa*). Lo stato contabile della spesa segue la scrittura.
- I report py3o di preventivo, consuntivo e richiesta fondi
  (`report/tpl/*.odt`).

## Diritti

*Manager* (tutto) e *User* (sola lettura dei dati, uso dei wizard). Il CSV
dei diritti si rigenera con `security/create_access_csv.py`: i modelli nuovi
vanno aggiunti lì, altrimenti la rigenerazione li toglie.
