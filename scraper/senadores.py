from functools import reduce
from requests import get
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup

BASE = 'http://www.senado.cl'
PATH = 'appsenado/index.php'


def query_parser(query):
    if type(query) == dict:
        str_query = reduce(lambda accum, tuple: accum +
                           '{}={}&'.format(*tuple), query.items(), '?')
        return str_query[:-1]
    elif type(query) == str:
        queries = query.replace('?', '').split('&')
        return dict(map(lambda query: (*query.split('='),), queries))
    raise TypeError('query should be a dict or a string')


def fetch_table_actuales():
    query = {
        'mo': 'senadores',
        'ac': 'listado'
    }

    main = get(urljoin(BASE, '{}{}'.format(PATH, query_parser(query))))
    return BeautifulSoup(main.text, 'html.parser').find(class_='clase_tabla')


def fetch_ids(table):
    ids = []
    pointer = table.find('tr').find_next_sibling('tr')
    while pointer:
        fila_foto, _ = pointer.find('table').find_all('td')
        url_foto = '{}{}'.format(BASE, fila_foto.find('img')['src'])
        id_senador = parse_qs(
            urlparse('{}{}'.format(BASE, url_foto)).query)['fid'][0]
        ids.append(int(id_senador))
        pointer = pointer.find_next_sibling('tr')
    return ids


def fetch_detail(sid):
    query = {
        'mo': 'senadores',
        'ac': 'fichasenador',
        'id': sid
    }

    main = get(urljoin(BASE, '{}{}'.format(PATH, query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    datos = soup.find(class_='datos').find_all('strong')
    valid_strong = ['Partido:', 'Teléfono:', 'Mail:', 'Currículum']
    datos = list(
        filter(lambda dato: dato.text in valid_strong or dato.find('a'), datos))

    partido = datos[0].next_sibling.strip()
    telefono = datos[1].next_sibling.strip()
    email = datos[2].next_sibling.strip()
    curriculum_uri = '{}{}'.format(BASE, datos[3].find('a')['href'])

    return {
        'sid': sid,
        'partido': partido,
        'telefono': telefono,
        'email': email,
        'curriculum_uri': curriculum_uri
    }
