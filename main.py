from db.main import connect, fetch_senadors

if __name__ == '__main__':
    connection = connect()
    ids_senadores = fetch_senadors(connection, ['id'])
