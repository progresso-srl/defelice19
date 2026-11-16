# Migrazione modulo ey_pratiche da Odoo 12 a Odoo 19

## Data migrazione
21/09/2026

## Modifiche effettuate

### 1. Migrazione XML Views (Odoo 12 → 19)
- ✅ Convertiti tutti gli attributi `colors` in `decoration-*`
- ✅ Convertiti tutti gli attributi `fonts` in `decoration-bf` e `decoration-it`
- ✅ Rimossi attributi `string` dai tag `<search>`
- ✅ Aggiornati attributi `states` deprecati
- ✅ Convertiti tutti i tag `<tree>` in `<list>` (Odoo 19)

#### File modificati:
- `views/pratiche/pratica.xml`
- `views/pratiche/follow_up_pratica.xml`
- `views/pratiche/ente.xml`
- `views/pratiche/tpl.xml`
- `views/normativa/normativa.xml` (tree → list)

### 2. Rimozione decoratori obsoleti (@api.multi, @api.one)

#### File Python modificati:
- `models/pratiche/pratica.py` - Rimossi 8 decoratori
- `models/pratiche/elementi_pratica.py` - Rimossi 4 decoratori
- `models/pratiche/ente.py` - Rimosso 1 decoratore
- `models/report/py3o.py` - Rimossi 5 decoratori
- `models/report/ir_actions_report.py` - Rimosso 1 decoratore

**Totale decoratori rimossi: 19**

### 3. Aggiunta dipendenza report_py3o
**Problema risolto**: Il modulo ereditava da `py3o.template` e `py3o.report` ma mancava la dipendenza.

**Soluzione**:
- Aggiunto `report_py3o` alle dipendenze in `__manifest__.py`

### 4. Correzione modello ContattoPraticaNave
**Problema risolto**: Il modello tentava di ereditare da `ey_base.contatto_pratica_nave` che non esisteva in ey_base.

**Soluzione**:
- Cambiato da `_inherit` a `_name` in `models/pratiche/elementi_pratica.py`
- Aggiunto campo `name` required e `_description`
- Corretto file `security/ir.model.access.csv` (rimossi duplicati)

### 5. Correzione security.xml (res.groups)
**Problemi risolti**: Campi non più validi in `res.groups` in Odoo 19.

**Soluzione**:
- Rimosso campo `category_id` (obsoleto)
- Rimosso campo `users` (non più valido in XML)
- Rimosso campo `implied_ids` (gestito diversamente)
- Semplificati i record dei gruppi - solo nome richiesto

### 6. Note importanti
- I file nella directory `models/old/` non sono stati modificati (sono backup vecchi)
- La compatibilità è stata mantenuta con le versioni precedenti ove possibile
- Tutti i metodi ora utilizzano il comportamento di default di Odoo (recordset)
- Il modello `ey_base.contatto_pratica_nave` è ora definito in ey_pratiche

## Verifica
Per testare il modulo:
```bash
odoo-bin -c odoo19.conf -u ey_pratiche --stop-after-init
```

## Stato
La migrazione del modulo installa su Odoo 19, ma restano aperti i punti qui
sotto. Il codice Odoo 8 di riferimento è in `legacy/ey2`; i file Odoo 8 che
erano in questo modulo (`models/old`, `views/old`, `norm_ODOO8.xml`) e la
bozza dei report py3o (`views/report_TODO`) sono in `legacy/ey_pratiche`.

## Da fare
Prima stava in `TODO/todo.txt`.

- Come funzionano i referenti pratica? Quando si inseriscono partner o nave?
- Cercare tutti i nomi dei vecchi modelli su Odoo 8 e vedere se ci sono
  altre cose da aggiungere (viste, cron, ecc.).
- Nelle funzioni dei modelli che hanno `pratica_id` ricontrollare nel codice
  Odoo 8 se faceva distinzioni tra pratiche navi e pratiche soggetti.
- Controllare tutti i valori delle selection di Odoo 8 quando vengono usati
  nel codice vecchio.
- Report py3o: in Odoo 8 alla creazione della pratica veniva impostato il
  parser; va rifatto su `py3o.report` (vedi TODO in `pratica.py`).
