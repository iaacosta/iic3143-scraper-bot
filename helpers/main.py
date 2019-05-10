import datetime
from functools import reduce


def logger(message):
    date = datetime.datetime.now()
    print('[{}] {}'.format(date.strftime('%d-%M-%Y %H:%m'), message))
    return date


def process_phone_number(phone_number):
    if type(phone_number) is not str:
        return None
    elif '+5632' in phone_number:
        return phone_number
    no_code = phone_number.split(
        '(56-32)')[1] if '(56-32)' in phone_number else phone_number
    no_code = no_code.split('(56 32)')[1] if '(56 32)' in no_code else no_code
    if len(no_code.strip()) < 7:
        return None
    else:
        return '+5632{}'.format(no_code.strip())


def query_parser(query):
    if type(query) == dict:
        str_query = reduce(lambda accum, tuple: accum +
                           '{}={}&'.format(*tuple), query.items(), '?')
        return str_query[:-1]
    elif type(query) == str:
        queries = query.replace('?', '').split('&')
        return dict(map(lambda query: (*query.split('='),), queries))
    raise TypeError('query should be a dict or a string')


def parse_name(full_name):
    splitted = full_name.split(',')
    return {
        'nombre': splitted[1].strip(),
        'apellido_paterno': splitted[0].strip().split(' ')[0],
        'apellido_materno': splitted[0].strip().split(' ')[1]
    }
