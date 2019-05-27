import requests
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import helpers.main as helpers


BASE = 'http://www.senado.cl'
PATH = 'appsenado/index.php'


def fetch_new_comisiones():
    query = {
        'mo': 'tramitacion',
        'ac': 'comisiones',
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    data = []
    rows = soup.find_all('tr')[1:-1]
    for row in rows:
        _id, camara, tipo, nombre, _ = row.find_all('td')
        if 'diputados' in camara.text.lower() or 'mixta' in tipo.text.lower():
            continue

        nombre = nombre.text[3:] if 'de ' == nombre.text[:3] else nombre.text
        data.append({
            'id': int(_id.text),
            'tipo': tipo.text.lower(),
            'nombre': nombre
        })

    return data


def fetch_detail(comision):
    query = {
        'mo': 'comisiones',
        'ac': 'ficha',
        'id': comision['id'],
        'tipo_comision': 10
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    detalle = soup.find(
        class_=['col1', 'integrantes', 'shadow-down', 'center'])

    detalle = detalle.find_next_sibling().find_all('tr')[-2:]
    email = detalle[0].find_all('td')[1].text.strip()
    telefono = detalle[1].find_all('td')[1].text.strip()

    comision['email'] = email if email != '' else None
    comision['telefono'] = helpers.process_phone_number(telefono)


def fetch_integrantes(cid):
    query = {
        'mo': 'comisiones',
        'ac': 'ficha',
        'id': cid,
        'tipo_comision': 10
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    detalle = soup.find(
        class_=['col1', 'integrantes', 'shadow-down', 'center'])

    integrantes_data = []

    integrantes = detalle.find_all('article')
    for integrante in integrantes:
        parl_img_url = integrante.find('img')['src'].split('?')[1]
        query = helpers.query_parser(parl_img_url)
        integrantes_data.append({
            'cid': cid,
            'sid': int(query['fid']),
        })

    return integrantes_data


def fetch_proyectos_in_comision(cid):
    query = {
        'mo': 'tramitacion',
        'ac': 'boletin_x_fecha',
        'comiid': cid
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    boletines = []

    radicados, _, informados, _ = soup.find_all('table')
    for row in radicados.find_all('tr')[1:]:
        _, boletin, _, _, _, _ = row.find_all('td')
        boletines.append(boletin.text)

    for row in informados.find_all('tr')[1:]:
        _, boletin, _, _, _, _ = row.find_all('td')
        boletines.append(boletin.text)

    print(boletines)
    return set(boletines)
