from unittest import main, TestCase
from unittest.mock import MagicMock
from test_helpers import html_senadores_index, MockResponse
from scraper.periodos import fetch_periodos, requests, BeautifulSoup


class FetchPeriodos(TestCase):
    def test_one_senator(self):
        requests.get = MagicMock(
            return_value=MockResponse(html_senadores_index))
        periodos = fetch_periodos([905])
        expected_value = [
            {'sid': 905, 'cargo': 'senador', 'inicio': 2014, 'final': 2022}]
        self.assertListEqual(expected_value, periodos)

    def test_multiple_senators(self):
        requests.get = MagicMock(
            return_value=MockResponse(html_senadores_index))
        periodos = fetch_periodos([905, 985, 1221])
        expected_values = [
            {'sid': 905, 'cargo': 'senador', 'inicio': 2014, 'final': 2022},
            {'sid': 985, 'cargo': 'senador', 'inicio': 2018, 'final': 2026},
            {'sid': 1221, 'cargo': 'diputado', 'inicio': 2010, 'final': 2018},
            {'sid': 1221, 'cargo': 'senador', 'inicio': 2018, 'final': 2026}
        ]
        for value in expected_values:
            self.assertIn(value, periodos)


if __name__ == "__main__":
    main()
