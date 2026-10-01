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
    ('ey_pratiche', 'ey_pratiche.normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.categoria_normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.natura_normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.allegato_normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.ambito_normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    # ('ey_pratiche', 'ey_pratiche.tipo_normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.argomento_normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.ue_normativa', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    
    ('ey_pratiche', 'ey_pratiche.tpl', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.documento_tpl', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.allegato_tpl', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.chiave_tpl', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    
    ('ey_pratiche', 'ey_pratiche.pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.chiave_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.report_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 0, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.ente', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.sede_ente', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.ufficio_ente', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.prop_arm_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.qualifica_pratica_nave', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.ente_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.indirizzo_partner', {'manager': (1, 1, 1, 1), 'user': (1, 0, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.allegato_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.att_sistema_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.att_operatore_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.follow_up_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.alert_pratica_nave', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_pratiche', 'ey_pratiche.rappresentante_armatore', {'manager': (1, 1, 1, 1), 'user': (1, 0, 0, 0)}),
    ('ey_pratiche', 'ey_pratiche.equipaggio_nave_pratica', {'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)}),
    ('ey_base', 'ey_base.contatto_pratica_nave', { 'user': (1, 1, 1, 0)}),
    ('ey_base', 'ey_base.contatto_pratica_nave', { 'user': (1, 1, 1, 0)}),
    ('base','res.partner',{'manager': (1, 1, 1, 1), 'user': (1, 1, 1, 0)})
    
)

# Lista di ruoli
# 1 livello => chiave ruolo
# 2 livello => lista con la seguente struttura: (modulo, nome gruppo)
ROLES = {
    'manager': ('ey_pratiche', 'group_ey_pratiche_manager'),
    'user': ('ey_pratiche', 'group_ey_pratiche_user'),
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
