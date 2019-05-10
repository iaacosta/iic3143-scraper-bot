from os import environ
import psycopg2

DB_URL = environ['DATABASE_URL']


def connect():
    return psycopg2.connect(DB_URL)


def fetch_senadors(connection):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM "Senadors";')

    senadores = cursor.fetchall().copy()

    cursor.close()
    return senadores
