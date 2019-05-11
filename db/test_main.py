from unittest import TestCase, main
from unittest.mock import MagicMock
from os import environ

from db.main import *
from helpers.test import MockConector, MockCursor

psycopg2.connect = MagicMock()


class TestDBModule(TestCase):

    def test_connect(self):
        connect()
        psycopg2.connect.assert_called_with(DB_URL)

    def test_fetch_senadores_should_call_cursor_and_methods(self):
        connection = MockConector(DB_URL)
        return_val = fetch_senadores(connection,
                                     ['test_selector_1'])
        connection.cursor.assert_called_once()

    def test_fetch_senadores_one_attr(self):
        connection = MockConector(DB_URL)

        return_val = fetch_senadores(connection,
                                     ['test_selector_1'])
        self.assertEqual(return_val, ['M'])

        cursor = connection.cursor.return_value
        cursor.execute.assert_called_with(
            'SELECT test_selector_1 FROM "Senadors";')
        cursor.fetchall.assert_called_once()
        cursor.close.assert_called_once()

    def test_fetch_senadores_multiple_attr(self):
        connection = MockConector(DB_URL)

        return_val = fetch_senadores(connection,
                                     ['test_selector_1', 'test_selector_2'])

        self.assertEqual(return_val, ['MockCursorReturn'])

        cursor = connection.cursor.return_value
        cursor.execute.assert_called_with(
            'SELECT test_selector_1, test_selector_2 FROM "Senadors";')
        cursor.fetchall.assert_called_once()
        cursor.close.assert_called_once()


if __name__ == "__main__":
    main()
