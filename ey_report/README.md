# ey_report

Estensione del Mastro generale di OCA `account_financial_report`: l'opzione
**saldo di periodo** (`set_to_zero` sul wizard), che passa ai dati del report.

## Stato

Oggi il modulo aggiunge solo il campo e lo passa ai dati, senza la casella
nel wizard. I template che lo usavano, insieme a un layout con meno colonne,
erano quelli di OCA 12. In OCA 19 mandavano in errore la stampa del Mastro,
quindi sono stati tolti dal manifest e spostati in `legacy/ey_report`. Vanno
rifatti sui template di OCA 19.

Anche il wizard riscriveva per intero i dati del report con campi di OCA 12
che non esistono più. Ora parte dai dati di OCA e aggiunge solo
`set_to_zero`.
