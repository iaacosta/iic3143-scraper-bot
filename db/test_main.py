from os import environ
from helpers import MockConector, MockCursor
from unittest import TestCase, main
from unittest.mock import MagicMock
from os import environ
from db import insert, connect, fetch_senadores, psycopg2

psycopg2.connect = MagicMock()

test_env = 'postgres://testurl@blabla'
environ['DATABASE_URL'] = test_env


class TestConnect(TestCase):
    def test_should_call_connect_with_env_var(self):
        connect()
        psycopg2.connect.assert_called_once()
        psycopg2.connect.assert_called_with(test_env)


class TestFetchSenadores(TestCase):
    def test_should_call_cursor_and_methods(self):
        connection = MockConector(test_env)
        fetch_senadores(connection, ['test_selector_1'])
        connection.cursor.assert_called_once()

    def test_with_one_attr(self):
        connection = MockConector(test_env)

        return_val = fetch_senadores(connection,
                                     ['test_selector_1'])
        self.assertEqual(return_val, ['M'])

        cursor = connection.cursor.return_value
        cursor.execute.assert_called_with(
            'SELECT test_selector_1 FROM "Senadors";')
        cursor.execute.assert_called_once()
        cursor.fetchall.assert_called_once()
        cursor.close.assert_called_once()

    def test_with_multiple_attr(self):
        connection = MockConector(test_env)

        return_val = fetch_senadores(connection,
                                     ['test_selector_1', 'test_selector_2'])

        self.assertEqual(return_val, ['MockCursorReturn'])

        cursor = connection.cursor.return_value
        cursor.execute.assert_called_with(
            'SELECT test_selector_1, test_selector_2 FROM "Senadors";')
        cursor.execute.assert_called_once()
        cursor.fetchall.assert_called_once()
        cursor.close.assert_called_once()


class TestInsert(TestCase):
    pass


if __name__ == "__main__":
    main()
