from unittest import main, TestCase
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from test_helpers import html_proyectos, html_no_proyectos, html_proyecto, html_autores, MockResponse
from scraper.proyectos import fetch_new_proyectos, fetch_resumen, fetch_autores, requests


class FetchNewPeriodos(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=tramitacion&ac=avanzada_resultado&cadena=0~S~1~0~{}~{}~~~0~0~~~~'

    def setUp(self):
        requests.get = MagicMock(return_value=MockResponse(html_proyectos))

    def test_should_call_right_url(self):
        fetch_new_proyectos()
        requests.get.assert_called_once()
        requests.get.assert_called_with(self.url.format(
            (datetime.now() - timedelta(days=1)).date().strftime('%d/%m/%Y'),
            datetime.now().date().strftime('%d/%m/%Y'),
        ))

    def test_should_return_projects(self):
        periodos = fetch_new_proyectos()
        expected_value = [
            {
                'fecha': datetime.strptime('07/05/2003', '%d/%m/%Y'),
                'boletin': '3235-13',
                'estado': 'aprobado'
            },
            {
                'fecha': datetime.strptime('06/05/2003', '%d/%m/%Y'),
                'boletin': '3232-07',
                'estado': 'tramitacion'
            }
        ]
        self.assertListEqual(expected_value, periodos)

    def test_should_not_return_if_none(self):
        requests.get = MagicMock(return_value=MockResponse(html_no_proyectos))
        periodos = fetch_new_proyectos()
        self.assertListEqual([], periodos)


class FetchResumenAndId(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=tramitacion&ac=datos_proy&nboletin={}'

    def setUp(self):
        requests.get = MagicMock(return_value=MockResponse(html_proyecto))
        self.proyecto = {'boletin': '10002-07'}

    def test_should_call_right_url(self):
        fetch_resumen(self.proyecto)
        requests.get.assert_called_once()
        requests.get.assert_called_with(
            self.url.format(self.proyecto['boletin']))

    def test_should_return_data(self):
        expected_id = 10426
        expected_url = 'http://www.senado.cl/appsenado/templates/tramitacion/index.php?boletin_ini=10002-07'
        expected_resumen = 'Modifica la ley N° 19.733, sobre Libertades de Opinión e Información y Ejercicio del Periodismo, para proteger el derecho a la imagen, a la vida privada y a la honra de los niños, niñas y adolescentes'
        fetch_resumen(self.proyecto)
        self.assertEqual(self.proyecto['id'], expected_id)
        self.assertEqual(self.proyecto['resumen'], expected_resumen)
        self.assertEqual(self.proyecto['url'], expected_url)


class FetchAutores(TestCase):
    url = 'http://www.senado.cl/appsenado/index.php?mo=tramitacion&ac=autores&proyid={}'
    pid = 13177

    def setUp(self):
        requests.get = MagicMock(return_value=MockResponse(html_autores))

    def test_should_call_right_url(self):
        fetch_autores(self.pid)
        requests.get.assert_called_once()
        requests.get.assert_called_with(self.url.format(self.pid))

    def test_should_return_data(self):
        expected_result = [
            {'pid': self.pid, 'sid': 905},
            {'pid': self.pid, 'sid': 1115}
        ]
        response = fetch_autores(self.pid)
        self.assertEqual(response, expected_result)


if __name__ == "__main__":
    main()
