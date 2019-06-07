from unittest import main, TestCase
from unittest.mock import MagicMock
from test_helpers import html_asistencias, MockResponse
from scraper.asistencias import fetch_last_legislation, fetch_new_asistencias, requests


class FetchLastLegislation(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=sesionessala&ac=asistenciaSenadores&camara=S&legiid=490'

    def setUp(self):
        requests.get = MagicMock(return_value=MockResponse(html_asistencias))

    def test_should_call_right_url(self):
        fetch_last_legislation()
        requests.get.assert_called_once()
        requests.get.assert_called_with(self.url)

    def test_should_return_last_legislation(self):
        comisiones = fetch_last_legislation()
        expected_value = {
            'lid': 490,
            'number': 367,
            'fecha_i': '11/03/2019',
            'fecha_t': '10/03/2020'
        }

        self.assertDictEqual(expected_value, comisiones)


class FetchNewAssistances(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=sesionessala&ac=asistenciaSenadores&camara=S&legiid=490'

    def setUp(self):
        requests.get = MagicMock(return_value=MockResponse(html_asistencias))

    def test_should_call_right_url(self):
        fetch_new_asistencias()
        requests.get.assert_called()
        requests.get.assert_called_with(self.url)

    def test_should_return_new_assistances(self):
        comisiones = fetch_new_asistencias()
        expected_value = [
            {'lid': 490, 'fecha_inicio': '2019-11-03', 'fecha_fin': '2020-10-03',
                'sid': 905, 'asistencias': 21, 'inasistencias_just': 0, 'inasistencias_no_just': 2},
            {'lid': 490, 'fecha_inicio': '2019-11-03', 'fecha_fin': '2020-10-03',
                'sid': 985, 'asistencias': 16, 'inasistencias_just': 4, 'inasistencias_no_just': 3},
            {'lid': 490, 'fecha_inicio': '2019-11-03', 'fecha_fin': '2020-10-03',
                'sid': 1221, 'asistencias': 20, 'inasistencias_just': 3, 'inasistencias_no_just': 0},
            {'lid': 490, 'fecha_inicio': '2019-11-03', 'fecha_fin': '2020-10-03',
                'sid': 1110, 'asistencias': 22, 'inasistencias_just': 0, 'inasistencias_no_just': 1},
            {'lid': 490, 'fecha_inicio': '2019-11-03', 'fecha_fin': '2020-10-03',
                'sid': 907, 'asistencias': 23, 'inasistencias_just': 0, 'inasistencias_no_just': 0},
            {'lid': 490, 'fecha_inicio': '2019-11-03', 'fecha_fin': '2020-10-03',
                'sid': 1218, 'asistencias': 23, 'inasistencias_just': 0, 'inasistencias_no_just': 0},
            {'lid': 490, 'fecha_inicio': '2019-11-03', 'fecha_fin': '2020-10-03',
                'sid': 986, 'asistencias': 23, 'inasistencias_just': 0, 'inasistencias_no_just': 0},
        ]

        self.maxDiff = None
        self.assertListEqual(expected_value, comisiones)
