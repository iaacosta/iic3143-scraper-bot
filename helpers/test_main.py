from unittest import TestCase, main
from helpers import process_phone_number, query_parser, parse_name, sql_value_parser


class TestProcessPhoneNumer(TestCase):
    def test_normal_phone_number(self):
        number = '(56-32) 1234567'
        self.assertEqual('+56321234567', process_phone_number(number))

    def test_short_phone_number(self):
        number = '1234'
        self.assertIsNone(process_phone_number(number))

    def test_short_phone_number_with_code(self):
        number = '(56-32) 123456'
        self.assertIsNone(process_phone_number(number))

    def test_no_string_number(self):
        number = 1234
        self.assertIsNone(process_phone_number(number))

    def test_already_formatted_number(self):
        number = '+56321234567'
        self.assertEqual(number, process_phone_number(number))


class TestQueryParser(TestCase):
    def test_normal_query(self):
        query = {'query1': 'value1',
                 'query2': 'value2'}
        self.assertEqual('?query1=value1&query2=value2', query_parser(query))


class TestParseName(TestCase):
    def test_well_formatted_name(self):
        name = 'Smith Doe, John'
        expected_result = {'nombre': 'John',
                           'apellido_paterno': 'Smith',
                           'apellido_materno': 'Doe'}
        self.assertEqual(expected_result, parse_name(name))


if __name__ == "__main__":
    main()
