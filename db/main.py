from os import environ
from helpers import sql_value_parser
import psycopg2


def connect():
    return psycopg2.connect(environ['DATABASE_URL'])


def select(connection, selectors, table_name, condition=''):
    cursor = connection.cursor()
    cursor.execute('SELECT {} FROM "{}"{};'.format(
        ', '.join(selectors), table_name, condition))

    senadores = cursor.fetchall().copy()
    if len(selectors) == 1:
        senadores = list(map(lambda senador: senador[0], senadores))

    cursor.close()
    return senadores


def insert(connection, table_name, items):
    cursor = connection.cursor()
    columns = items[0].keys()

    query = 'INSERT INTO "{}"({}) VALUES'.format(
        table_name, ', '.join(columns))
    values = []

    for item in items:
        data = map(sql_value_parser, item.values())
        values.append('({})'.format(', '.join(data)))

    cursor.execute('{} {};'.format(query, ', '.join(values)))
    connection.commit()
    cursor.close()


def delete(connection, table_name, condition):
    cursor = connection.cursor()
    query = 'DELETE FROM "{}" WHERE {};'.format(table_name, condition)
    cursor.execute(query)
    connection.commit()
    cursor.close()
