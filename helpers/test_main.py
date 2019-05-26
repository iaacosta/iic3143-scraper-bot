from unittest import TestCase, main
from helpers import process_phone_number, query_parser, parse_name, sql_value_parser


class TestProcessPhoneNumer(TestCase):
    def test_normal_phone_number(self):
        test_number = '(56-32) 1234567'
        self.assertEqual('+56321234567', process_phone_number(test_number))

    def test_short_phone_number(self):
        test_number = '1234'
        self.assertIsNone(process_phone_number(test_number))

    def test_short_phone_number_with_code(self):
        test_number = '(56-32) 123456'
        self.assertIsNone(process_phone_number(test_number))

    def test_no_string_number(self):
        test_number = 1234
        self.assertIsNone(process_phone_number(test_number))

    def test_already_formatted_number(self):
        test_number = '+56321234567'
        self.assertEqual(test_number, process_phone_number(test_number))

    def test_dual_number(self):
        test_number = '322504225-322504658'
        self.assertEqual('+56322504225', process_phone_number(test_number))

    def test_spaced_number(self):
        test_number = '32 2504040'
        self.assertEqual('+56322504040', process_phone_number(test_number))

    def test_dashed_number(self):
        test_number = '32-2504227'
        self.assertEqual('+56322504227', process_phone_number(test_number))

    def test_dashed_spaced_number(self):
        test_number = '32-250 46 04'
        self.assertEqual('+56322504604', process_phone_number(test_number))

    def test_dashed_parenthesis_number(self):
        test_number = '(56) 32 2504156'
        self.assertEqual('+56322504156', process_phone_number(test_number))


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
