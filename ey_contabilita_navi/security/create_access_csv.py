# -*- coding: utf-8 -*-

import csv
import os

# Lista dei permessi per i modelli
# 1 posto => module
# 2 posto => model
# 3 posto => dict con la seguente struttura:
#   - chiave ruolo (la stessa del dict ROLES)
#   - lista di permessi con il seguente ordine: (read, write, create, unlink)
MODELS = (
    ('ey_contabilita_navi', 'ey_contabilita_navi.contratto_nave', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.periodo_contratto', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.previsionale_contratto', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.spesa_previsionale', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.tipo_spesa_previsionale', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'account.move', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'account.move.line', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.documenti_contratto', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.tipo_documento', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.anticipi_armatore', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    # wizard: da Odoo 17 anche i TransientModel vogliono i diritti d'accesso
    ('ey_contabilita_navi', 'ey_contabilita_navi.wiz_crea_prossimo_previsionale', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 1)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.wiz_collega_linea_spesa_nave', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 1)}),
    ('ey_contabilita_navi', 'ey_contabilita_navi.wiz_collega_linea_spesa_armatore', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 1)}),
)

# Lista di ruoli
# 1 livello => chiave ruolo
# 2 livello => lista con la seguente struttura: (modulo, nome gruppo)
ROLES = {
    'manager': ('ey_contabilita_navi', 'group_ey_contabilita_navi_manager'),
    'user': ('ey_contabilita_navi', 'group_ey_contabilita_navi_user'),
}


def main(models, roles):
    file_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ir.model.access.csv'))
    with open(file_csv, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['id', 'name', 'model_id:id', 'group_id:id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'])

        for model in models:
            module_name = model[0]
            model_name = model[1]
            model_name_underscored = model[1].replace('.','_')
            for role_key, perms in model[2].items():
                role_module = roles[role_key][0]
                role_name = roles[role_key][1]
                writer.writerow([
                    "access_%s_%s" % (model_name_underscored, role_key),
                    model_name,
                    "%s.model_%s" % (module_name, model_name_underscored),
                    "%s.%s" % (role_module, role_name),
                    perms[0], perms[1], perms[2], perms[3],
                ])


if __name__ == "__main__":
    main(MODELS, ROLES)
