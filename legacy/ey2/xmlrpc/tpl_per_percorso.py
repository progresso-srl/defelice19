from libraries import openerp

percorsi = openerp.search("ey2.percorso_tpl_corso", [])

print openerp.method("ey2.percorso_tpl_corso", "get_tpl_attivi", percorsi)
