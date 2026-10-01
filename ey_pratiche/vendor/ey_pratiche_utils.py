# -*- coding: utf-8 -*-

def format_date(date):
    """
    Funzione che trasforma una data da yyyy-mm-dd a dd/mm/yyyy
    :param date: la data
    :return:la data formattata come dd/mm/yyyy
    """
    date_list = str(date).split("-")
    return date_list[2] + "/" + date_list[1] + "/" + date_list[0]
