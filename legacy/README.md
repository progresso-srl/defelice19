# legacy

Codice Odoo 8/12 tenuto come **riferimento per la migrazione**. Non è
installabile su Odoo 19. Odoo lo ignora anche se il repo è nell'`addons_path`:
`legacy/` non è un modulo, e i moduli qui dentro hanno solo `__openerp__.py`.

| Cartella | Che cos'è |
|---|---|
| `ey2/` | Il gestionale E-Yacht su Odoo 8: anagrafiche nave, corsi ed esami, pratiche, normativa, saldi navi, script XML-RPC (Python 2) |
| `ey_account/` | Estensioni contabili Odoo 8: partner ledger, registro IVA, fatture. Non migrate; in `ey_corsi` le dipendenze OCA relative sono annotate come da riaggiungere |
| `config_tpl_master/` | Configuratore di template di stampa su `report_aeroo` (Odoo 8) |
| `ey_pratiche/` | I file Odoo 8 che erano dentro `ey_pratiche` (`models/old`, `views/old`, `norm_ODOO8.xml`) e la bozza dei report py3o (`views/report_TODO`) |
| `ey_report/` | I due template del Mastro generale (colonne ridotte, "saldo di periodo" con `set_to_zero`) e la casella nel wizard. Erano scritti per i template OCA 12 e in OCA 19 mandavano in errore la stampa del Mastro. Da rifare sui template di OCA 19; il campo `set_to_zero` è ancora nel wizard |

Quando la migrazione è finita, questa cartella si può cancellare: resta nella
storia di git.
