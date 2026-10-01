# -*- coding: utf-8 -*-
##############################################################################
#
#    CAMSPM module for OpenERP
#    Copyright (C) 2014 Future Tech srl (http://www.futuretechsrl.it).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import xmlrpclib
import json
import os

dir_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.realpath(os.path.join(dir_path, '../openerp.json'))) as data_file:
    data = json.loads(data_file.read())

_url_openerp = data['url']
_dbname = data['dbname']
_username = data['username']
_pwd = data['password']

_connected = False
_uid = None
_sock_object = None


def connect():
    """
    funzione che si connette a OpenERP tramite XML-RPC
    """
    global _uid, _sock_object, _url_openerp, _dbname, _username, _pwd, _connected
    if _connected:
        return None
    try:
        if not _uid:
            _sock_common = xmlrpclib.ServerProxy('%s/common' % _url_openerp)
            _uid = _sock_common.login(_dbname, _username, _pwd)
        _sock_object = xmlrpclib.ServerProxy('%s/object' % _url_openerp, allow_none=True, verbose=False)
        _connected = True
        print("connected to OpenERP server")
    except xmlrpclib.Fault:
        print("couldn't connect to XML-RPC server")
        raise


def search(tabella, args=None, order=None):
    """
    funzione che lancia la ricerca di un oggetto
    :param tabella string
    :param args dictionary
    :param order dictionary
    :return list of ids
    """
    global _sock_object, _dbname, _uid, _pwd
    if not args:
        args = []
    return _sock_object.execute(_dbname, _uid, _pwd, tabella, 'search', args, 0, None, order)


def read(tabella, ids, fields=None):
    """
    funzione che lancia la lettura di un oggetto
    :param tabella string
    :param ids list
    :param fields list
    :return list of dictionary
    """
    global _sock_object, _dbname, _uid, _pwd
    if not fields:
        fields = []
    return _sock_object.execute(_dbname, _uid, _pwd, tabella, 'read', ids, fields)


def create(tabella, dati):
    """
    funzione che lancia la creazione di un oggetto tramite XML-RPC
    :param tabella string
    :param dati dictionary
    :return boolean
    """
    global _sock_object, _dbname, _uid, _pwd
    try:
        risultato = _sock_object.execute(_dbname, _uid, _pwd, tabella, 'create', dati)
    except xmlrpclib.Fault:
        #print("xmlrpclib exception per create %s" % [tabella, dati])
        raise
    return risultato


def write(tabella, ids, dati):
    """
    funzione che aggiorna un oggetto tramite XML-RPC
    :param tabella string
    :param ids list
    :param dati dictionary
    :return boolean
    """
    global _sock_object, _dbname, _uid, _pwd
    try:
        risultato = _sock_object.execute(_dbname, _uid, _pwd, tabella, 'write', ids, dati)
    except xmlrpclib.Fault:
        #print("xmlrpclib exception per write %s" % [tabella, dati])
        raise
    return risultato


def unlink(tabella, ids):
    """
    funzione che distrugge un oggetto tramite XML-RPC
    :param tabella string
    :param ids list
    :return boolean
    """
    global _sock_object, _dbname, _uid, _pwd
    return _sock_object.execute(_dbname, _uid, _pwd, tabella, 'unlink', ids)


def workflow(tabella, signal, id):
    """
    funzione che lancia un workflow tramite XML-RPC
    :param tabella string
    :param signal string
    :param id int
    :return boolean
    """
    global _sock_object, _dbname, _uid, _pwd
    return _sock_object.exec_workflow(_dbname, _uid, _pwd, tabella, signal, id)


def method(tabella, metodo, *args):
    """
    funzione che distrugge un oggetto tramite XML-RPC
    :param tabella string
    :param args list
    :return boolean
    """
    global _sock_object, _dbname, _uid, _pwd
    return _sock_object.execute(_dbname, _uid, _pwd, tabella, metodo, *args)

connect()
