import datetime


def logger(message):
    date = datetime.datetime.now()
    print('[{}] {}'.format(date.strftime('%d-%M-%Y %H:%m'), message))
    return date
