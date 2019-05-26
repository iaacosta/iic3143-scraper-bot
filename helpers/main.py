import datetime
from os import path
from functools import reduce


def logger(message):
    date = datetime.datetime.now()
    msg = '[{} UTC] {}'.format(date.strftime('%d-%m-%Y %H:%M'), message)
    print(msg)
    with open(path.join(path.dirname(__file__), '..', '.log'), 'a') as f:
        f.write('{}\n'.format(msg))
    return msg


def process_phone_number(phone_number):
    if type(phone_number) is not str:
        return None
    elif '+5632' in phone_number:
        return phone_number

    no_spaces = phone_number.replace(' ', '')

    if '(56-32)' in no_spaces:
        no_code = no_spaces.split(
            '(56-32)')[1] if '(56-32)' in phone_number else phone_number
        no_code = no_code.split('(56 32)')[
            1] if '(56 32)' in no_code else no_code
        if len(no_code.strip()) != 7:
            return None
        else:
            return '+5632{}'.format(no_code.strip())
    elif no_spaces[:2] == '32':
        no_spaces = no_spaces.split(
            '-')[0] if len(no_spaces) > 12 and '-' in no_spaces else no_spaces
        no_hyphens = no_spaces.replace('-', '')
        return '+56{}'.format(no_hyphens)
    elif '(56)32' in no_spaces:
        return '+56{}'.format(no_spaces[4:])


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


def sql_value_parser(val):
    return str(val) if type(val) == int else "'{}'".format(val)


def parse_estado(estado):
    if ('publicado' in estado.lower()):
        return 'aprobado'

    parser = {
        'En tramitación': 'tramitacion',
        'Archivado': 'suspendido',
        'Retirado': 'rechazado',
        'Rechazado': 'rechazado',
        'Consulta archivo': 'suspendido',
        'Solicitud archivo': 'suspendido',
        'Inconstitucional': 'rechazado',
        'Inadmisible': 'rechazado'
    }

    return parser[estado]
