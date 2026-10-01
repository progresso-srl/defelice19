from libraries import openerp

corso_model = "ey.corso"

corsi = openerp.method(corso_model, "list_corsi_sito", '2018-08-31')

print corsi
