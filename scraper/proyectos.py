import requests
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import helpers.main as helpers


BASE = 'http://www.senado.cl'
PATH = 'appsenado/index.php'


def fetch_new_proyectos(custom_last_date):
    today = datetime.now().date()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    query = {
        'mo': 'tramitacion',
        'ac': 'avanzada_resultado',
        'cadena': '0~S~1~0~{}~{}~~~0~0~~~~'.format(
            yesterday.strftime(
                '%d/%m/%Y') if custom_last_date is None else custom_last_date,
            today.strftime('%d/%m/%Y'),
        )
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    data = []

    rows = soup.find_all('tr')[1:-1]
    if (len(rows) == 0):
        return data

    for proyecto in rows:
        info = proyecto.find_all('td')
        date = info[0].text.strip()
        boletin = info[1].text.strip()
        estado_raw = info[3].text.strip()

        data.append({
            'fecha': datetime.strptime(date, '%d/%m/%Y'),
            'boletin': boletin,
            'estado': helpers.parse_estado(estado_raw)
        })

    return data


def fetch_resumen(proyecto):
    query = {
        'mo': 'tramitacion',
        'ac': 'datos_proy',
        'nboletin': proyecto['boletin']
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    id_criteria = re.compile('proyid\\s*=\\s*(.*?);')
    proyecto['id'] = int(id_criteria.findall(
        soup.find_all('script')[0].string)[0])

    info_table = soup.find_all('table')[1]

    proyecto['resumen'] = re.sub(' +', ' ', info_table.find_all('tr')
                                 [0].find_all('td')[1].text.replace('\n', '').strip())

    proyecto['url'] = 'http://www.senado.cl/appsenado/templates/tramitacion/index.php?boletin_ini={}'.format(
        proyecto['boletin']
    )


def fetch_autores(pid):
    query = {
        'mo': 'tramitacion',
        'ac': 'autores',
        'proyid': pid
    }

    main = requests.get(
        urljoin(BASE, '{}{}'.format(PATH, helpers.query_parser(query))))
    soup = BeautifulSoup(main.text, 'html.parser')

    info_table = soup.find('table')
    autores = []
    for row in info_table.find_all('tr')[1:]:
        info = row.find_all('td')
        sid = info[0].text.strip()
        cargo = info[2].text.strip()

        if cargo != 'S':
            continue

        autores.append({
            'pid': pid,
            'sid': int(sid)
        })

    return autores
