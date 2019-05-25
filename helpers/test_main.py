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
    def test_dict_query(self):
        dict_query = {'query1': 'value1',
                      'query2': 'value2'}
        self.assertEqual('?query1=value1&query2=value2',
                         query_parser(dict_query))

    def test_string_query(self):
        str_query = '?query1=value1&query2=value2'
        expected_value = {'query1': 'value1',
                          'query2': 'value2'}
        self.assertEqual(expected_value, query_parser(str_query))

    def test_no_string_or_dict_query(self):
        self.assertRaises(TypeError, query_parser, 0)


class TestParseName(TestCase):
    def test_well_formatted_name(self):
        name = 'Smith Doe, John'
        expected_result = {'nombre': 'John',
                           'apellido_paterno': 'Smith',
                           'apellido_materno': 'Doe'}
        self.assertEqual(expected_result, parse_name(name))


class TestSQLValueParser(TestCase):
    def test_string_value(self):
        value = 'John Doe'
        self.assertEqual("'John Doe'", sql_value_parser(value))

    def test_number_value(self):
        value = 0
        self.assertEqual('0', sql_value_parser(value))


if __name__ == "__main__":
    main()
