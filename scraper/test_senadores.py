from unittest import main, TestCase
from unittest.mock import create_autospec
from test_helpers import html_senadores_actuales, html_senador_perfil, html_senadores_index, MockResponse
from scraper import fetch_ids, fetch_detail, requests, BeautifulSoup


def mock_response(url):
    if 'ac=periodos' in url:
        return MockResponse(html_senadores_index)
    return MockResponse(html_senador_perfil)


class TestFetchIds(TestCase):
    def test_default(self):
        periodos = fetch_ids(BeautifulSoup(
            html_senadores_actuales, 'html.parser'))
        expected_value = [905, 985, 1221]
        self.assertListEqual(expected_value, periodos)


class TestFetchDetail(TestCase):
    def test_default(self):
        requests.get = mock_response
        detalle = fetch_detail(905)
        expected_response = {
            'id': 905,
            'partido_politico': 'R.N.',
            'email': 'allamand@senado.cl',
            'telefono': '+56322504701',
            'url_curriculum': 'http://www.senado.cl/curriculum-senador-andres-allamand-zavala/senado/2014-03-10/171943.html',
            'url_foto': 'http://www.senado.cl/appsenado/index.php?mo=senadores&ac=getFoto&id=905&tipo=1',
            'nombre': 'Andrés',
            'apellido_paterno': 'Allamand',
            'apellido_materno': 'Zavala'
        }
        self.assertEqual(expected_response, detalle)


if __name__ == "__main__":
    main()
