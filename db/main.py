from os import environ
import psycopg2

DB_URL = environ['DATABASE_URL']


def connect():
    return psycopg2.connect(DB_URL)


def fetch_senadors(connection, selectors):
    cursor = connection.cursor()
    cursor.execute('SELECT {} FROM "Senadors";'.format(','.join(selectors)))

    senadores = list(map(lambda row: row[0], cursor.fetchall().copy()))

    cursor.close()
    return senadores
