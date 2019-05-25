from os import environ
from test_helpers import MockConector, MockCursor
from unittest import TestCase, main
from unittest.mock import MagicMock
from os import environ
from db import insert, connect, select, psycopg2

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
        select(connection, ['test_selector_1'])
        connection.cursor.assert_called_once()

    def test_with_one_attr(self):
        connection = MockConector(test_env)

        return_val = select(connection,
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

        return_val = select(connection,
                            ['test_selector_1', 'test_selector_2'])

        self.assertEqual(return_val, ['MockCursorReturn'])

        cursor = connection.cursor.return_value
        cursor.execute.assert_called_with(
            'SELECT test_selector_1, test_selector_2 FROM "Senadors";')
        cursor.execute.assert_called_once()
        cursor.fetchall.assert_called_once()
        cursor.close.assert_called_once()


class TestInsert(TestCase):
    def test_with_one_value(self):
        connection = MockConector(test_env)
        insert(connection, 'TestTable', [{'id': 0, 'name': 'Test name 0'}])
        cursor = connection.cursor.return_value
        cursor.execute.assert_called_with(
            'INSERT INTO "TestTable"(id, name) VALUES (0, \'Test name 0\');')
        cursor.execute.assert_called_once()

    def test_with_multiple_values(self):
        connection = MockConector(test_env)
        insert(connection, 'TestTable', [
               {'id': 0, 'name': 'Test name 0'}, {'id': 1, 'name': 'Test name 1'}])
        cursor = connection.cursor.return_value
        cursor.execute.assert_called_with(
            'INSERT INTO "TestTable"(id, name) VALUES (0, \'Test name 0\'), (1, \'Test name 1\');')
        cursor.execute.assert_called_once()

    def test_should_commit_and_close(self):
        connection = MockConector(test_env)
        insert(connection, 'TestTable', [{'id': 0, 'name': 'Test name 0'}])
        cursor = connection.cursor.return_value
        connection.commit.assert_called_once()
        cursor.close.assert_called_once()


if __name__ == "__main__":
    main()
