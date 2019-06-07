import requests
import re
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import helpers.main as helpers


BASE = 'http://www.senado.cl'
PATH = 'appsenado/index.php'


def fetch_last_legislation():
    query = {
        'mo': 'sesionessala',
        'ac': 'asistenciaSenadores',
        'camara': 'S',
        'legiid': 490,
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    legislations = []
    for option in soup.find('select').find_all('option'):
        lid = int(option['value'])
        pattern = re.compile(r'^(.*) \((.*) - (.*)\)$')
        number, fecha_i, fecha_t = re.search(pattern, option.text).groups()
        legislations.append({
            'lid': int(lid),
            'number': int(number),
            'fecha_i': fecha_i,
            'fecha_t': fecha_t
        })

    return max(legislations, key=lambda legislation: legislation['number'])


def fetch_new_asistencias():
    to_fetch = fetch_last_legislation()
    print(to_fetch)
    fecha_inicio = datetime.strptime(
        to_fetch['fecha_i'], "%d/%m/%Y").strftime('%Y-%d-%m')
    fecha_fin = datetime.strptime(
        to_fetch['fecha_t'], "%d/%m/%Y").strftime('%Y-%d-%m')

    query = {
        'mo': 'sesionessala',
        'ac': 'asistenciaSenadores',
        'camara': 'S',
        'legiid': to_fetch['lid'],
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    seccion = soup.find(class_=['seccion2', 'sans'])
    table = seccion.find('table', class_='clase_tabla')
    total_sesiones = int(seccion.find('h2').text.split(':')[1])

    asistencias_ = []
    pointer = table.find('tr')
    pointer = pointer.find_next_sibling()
    while pointer:
        pattern = re.compile(r'.*parlid=(.*)&.*')
        sid = int(re.search(pattern, pointer.find('a')['href']).group(1))

        _, asistencias, inasistencias_just = pointer.find_all('td')

        asistencias = int(asistencias.text.strip())
        if inasistencias_just.text.strip() != '':
            inasistencias_just = int(inasistencias_just.text.strip())
        else:
            inasistencias_just = 0

        inasistencias_no_just = total_sesiones - inasistencias_just - asistencias
        if inasistencias_no_just < 0:
            inasistencias_no_just = 0

        asistencias_.append({
            'lid': to_fetch['lid'],
            'sid': sid,
            'asistencias': asistencias,
            'inasistencias_just': inasistencias_just,
            'inasistencias_no_just': inasistencias_no_just,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        })

        pointer = pointer.find_next_sibling().find_next_sibling()

    return asistencias_
