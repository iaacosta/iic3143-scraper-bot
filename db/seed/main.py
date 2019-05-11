import csv
import os
import re
import psycopg2
from main import connect

DATA_FILES = ['senadors', 'proyectos', 'periodos', 'senador_proyectos']

""" 
    Still can't make it work
"""


def camel_caser(snake_str):
    components = snake_str.split('_')
    return components[0].capitalize() + ''.join(x.title() for x in components[1:])


def clean_database(connection):
    cursor = connection.cursor()
    for table in map(camel_caser, DATA_FILES):
        cursor.execute('DELETE FROM "{}";'.format(table))
    connection.commit()
    cursor.close()


def seed():
    data = dict()

    connection = connect()
    cursor = connection.cursor()

    clean_database(connection)

    for file_name in DATA_FILES:
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'data', '{}.csv'.format(file_name))
        table_name = camel_caser(file_name)

        with open(path, 'r') as file:
            header = next(file).strip().split(',')

            cursor.copy_expert(
                '\copy "{}"({}) FROM "{}" DELIMITER \',\' CSV HEADER;'.format(table_name, header, file.read()))
            # cursor.copy_from(file, table='"{}"'.format(
            #     table_name), sep=',', columns=header)

    connection.commit()
    cursor.close()
    connection.close()


seed()
