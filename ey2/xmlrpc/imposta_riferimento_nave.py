from libraries import openerp

nave_ids = openerp.search('ey.unita', [('riferimento', '=', False)], order='id asc')

start = 1
for nave_id in nave_ids:
    str_start = str(start)
    riferimento = 'ADF / 000'
    if len(str_start) < 2:
        riferimento += '0'
    riferimento += str_start
    openerp.write('ey.unita', [nave_id], {'riferimento': riferimento})
    print str(riferimento) + " - id: " + str(nave_id)
    start += 1

