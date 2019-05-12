from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
import re
import helpers.main as helpers

BASE = 'http://www.senado.cl'
PATH = 'appsenado/index.php'


def fetch_periodos(ids):
    index_query = {'mo': 'senadores', 'ac': 'periodos'}
    index = requests.get(urljoin(BASE, '{}{}'.format(
        PATH, helpers.query_parser(index_query))))
    index_soup = BeautifulSoup(index.text, 'html.parser')

    database_data = []
    cargos = {'S': 'senador', 'D': 'diputado'}

    for _id in ids:
        helpers.logger('\tsid={}'.format(_id))
        search_param = re.compile('id={}'.format(_id))
        row = index_soup.find('a', href=search_param).find_parent('tr')

        periodos = row.find_all('td')[1].text.strip().split(', ')
        for periodo in periodos:
            cargo, intervalo = periodo.split(': ')
            cargo = cargos[cargo]
            inicio, final = intervalo.split('-')
            database_data.append({
                'sid': _id,
                'cargo': cargo,
                'inicio': int(inicio),
                'final': int(final),
            })

    return database_data
