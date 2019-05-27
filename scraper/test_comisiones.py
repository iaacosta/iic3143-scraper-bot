from unittest import main, TestCase
from unittest.mock import MagicMock
from test_helpers import html_comisiones, html_comision, html_leyes_comision, MockResponse
from scraper.comisiones import fetch_new_comisiones, fetch_detail, fetch_integrantes
from scraper.comisiones import fetch_proyectos_in_comision, requests


class FetchComisiones(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=tramitacion&ac=comisiones'

    def setUp(self):
        requests.get = MagicMock(return_value=MockResponse(html_comisiones))

    def test_should_call_right_url(self):
        fetch_new_comisiones()
        requests.get.assert_called_once()
        requests.get.assert_called_with(self.url)

    def test_should_return_comisiones(self):
        comisiones = fetch_new_comisiones()
        expected_value = [
            {
                'id': 192,
                'tipo': 'permanente',
                'nombre': 'Agricultura'
            },
            {
                'id': 283,
                'tipo': 'unidas',
                'nombre': 'Agricultura, de Medio Ambiente y Bienes Nacionales y de Salud, unidas'
            },
            {
                'id': 1034,
                'tipo': 'especial',
                'nombre': 'Bicameral del artículo 66A de la LOC Congreso Nacional'
            },
        ]

        self.assertListEqual(expected_value, comisiones)


class FetchDetail(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=comisiones&ac=ficha&id={}&tipo_comision=10'

    def setUp(self):
        html = html_comision.format('test@test.com')
        requests.get = MagicMock(return_value=MockResponse(html))
        self.comision = {'id': 0}

    def test_should_call_right_url(self):
        fetch_detail(self.comision)
        requests.get.assert_called_once()
        requests.get.assert_called_with(self.url.format(self.comision['id']))

    def test_should_mutate_data(self):
        fetch_detail(self.comision)
        expected_email = 'test@test.com'
        expected_phone = '+56322022791'
        self.assertEqual(self.comision['email'], expected_email)
        self.assertEqual(self.comision['telefono'], expected_phone)

    def test_should_return_none_email(self):
        html = html_comision.format('')
        requests.get = MagicMock(return_value=MockResponse(html))
        fetch_detail(self.comision)
        self.assertIsNone(self.comision['email'])


class FetchIntegrantes(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=comisiones&ac=ficha&id={}&tipo_comision=10'
    comision = 0

    def setUp(self):
        html = html_comision.format('test@test.com')
        requests.get = MagicMock(return_value=MockResponse(html))

    def test_should_call_right_url(self):
        fetch_integrantes(self.comision)
        requests.get.assert_called_once()
        requests.get.assert_called_with(self.url.format(self.comision))

    def test_should_return_integrantes(self):
        relations = fetch_integrantes(self.comision)
        expected_result = [
            {'cid': 0, 'sid': 1110},
            {'cid': 0, 'sid': 907},
            {'cid': 0, 'sid': 1212},
        ]

        self.assertListEqual(relations, expected_result)


class FetchProyectosInComision(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=tramitacion&ac=boletin_x_fecha&comiid={}'
    comision = 0

    def setUp(self):
        requests.get = MagicMock(
            return_value=MockResponse(html_leyes_comision))

    def test_should_call_right_url(self):
        fetch_proyectos_in_comision(self.comision)
        requests.get.assert_called_once()
        requests.get.assert_called_with(self.url.format(self.comision))

    def test_should_return_proyectos(self):
        proyectos = fetch_proyectos_in_comision(self.comision)
        expected_result = set(['12442-01', '11985-01', '12090-01'])
        self.assertSetEqual(proyectos, expected_result)
