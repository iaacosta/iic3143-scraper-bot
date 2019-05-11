from os import environ
import psycopg2

DB_URL = environ['DATABASE_URL']


def connect():
    return psycopg2.connect(DB_URL)


def fetch_senadores(connection, selectors):
    cursor = connection.cursor()
    cursor.execute('SELECT {} FROM "Senadors";'.format(', '.join(selectors)))

    senadores = cursor.fetchall().copy()
    if len(selectors) == 1:
        senadores = list(map(lambda senador: senador[0], senadores))

    cursor.close()
    return senadores


def insert(connection, table_name, items):
    cursor = connection.cursor()
    columns = items[0].keys()

    for item in items:
        data = map(lambda val: str(val) if type(val)
                   == int else "'{}'".format(val), item.values())
        query = 'INSERT INTO "{}"({}) VALUES({})'.format(
            table_name, ', '.join(columns), ', '.join(data))

        cursor.execute(query)

    connection.commit()
    cursor.close()
