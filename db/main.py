from os import environ
import psycopg2

DB_URL = environ['DATABASE_URL']


def connect():
    return psycopg2.connect(DB_URL)


def fetch_senadores(connection, selectors):
    cursor = connection.cursor()
    cursor.execute('SELECT {} FROM "Senadors";'.format(','.join(selectors)))

    senadores = list(map(lambda row: row[0], cursor.fetchall().copy()))

    cursor.close()
    return senadores


def insert_senadores(connection, senadores):
    cursor = connection.cursor()
    columns = senadores[0].keys()

    for senador in senadores:
        data = map(lambda val: str(val) if type(val)
                   == int else '"{}"'.format(val), senador.values())
        cursor.execute('INSERT INTO "Senadors"({}) VALUES({})'.format(
            ', '.join(columns), ', '.join(data)))

    connection.commit()
    cursor.close()
