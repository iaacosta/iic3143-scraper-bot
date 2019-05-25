from unittest import main, TestCase
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from test_helpers import html_proyectos, html_no_proyectos, MockResponse
from scraper import fetch_new_proyectos, requests

url = 'http://www.senado.cl/appsenado/index.php?mo=tramitacion&ac=avanzada_resultado&cadena=0~S~1~0~{}~{}~~~0~0~~~~'


class FetchNewPeriodos(TestCase):

    def setUp(self):
        requests.get = MagicMock(return_value=MockResponse(html_proyectos))

    def test_should_call_right_url(self):
        fetch_new_proyectos()
        requests.get.assert_called_once()
        requests.get.assert_called_with(url.format(
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


if __name__ == "__main__":
    main()
