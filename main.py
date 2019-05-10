from db.main import connect, fetch_senadors

if __name__ == '__main__':
    connection = connect()
    print(fetch_senadors(connection))
