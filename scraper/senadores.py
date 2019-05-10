from requests import get
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import re
import helpers.main as helpers

BASE = 'http://www.senado.cl'
PATH = 'appsenado/index.php'


def fetch_table_actuales():
    query = {
        'mo': 'senadores',
        'ac': 'listado'
    }

    main = get(urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
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
    index_query = {'mo': 'senadores', 'ac': 'periodos'}
    index = get(urljoin(BASE, '{}{}'.format(
        PATH, helpers.query_parser(index_query))))
    index_soup = BeautifulSoup(index.text, 'html.parser')

    detail_query = {'mo': 'senadores', 'ac': 'fichasenador', 'id': sid}
    detail = get(urljoin(BASE, '{}{}'.format(
        PATH, helpers.query_parser(detail_query))))
    detail_soup = BeautifulSoup(detail.text, 'html.parser')

    datos = detail_soup.find(class_='datos').find_all('strong')
    valid_strong = ['Partido:', 'Teléfono:', 'Mail:', 'Currículum']
    datos = list(
        filter(lambda dato: dato.text in valid_strong or dato.find('a'), datos))

    search_param = re.compile('id={}'.format(sid))
    nombre_completo = index_soup.find('a', href=search_param).text

    partido = datos[0].next_sibling.strip()
    telefono = helpers.process_phone_number(datos[1].next_sibling.strip())
    email = datos[2].next_sibling.strip()
    curriculum_uri = '{}{}'.format(BASE, datos[3].find('a')['href'])
    foto_uri = urljoin(BASE, detail_soup.find(
        'img', class_='foto_imag')['src'])

    return {
        'id': sid,
        'partido_politico': partido,
        'email': email,
        'telefono': telefono,
        'url_curriculum': curriculum_uri,
        'url_foto': foto_uri,
        **helpers.parse_name(nombre_completo)
    }
