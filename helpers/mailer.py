import requests
from time import sleep

URL = 'https://ventana-ciudadana.herokuapp.com'
PATH = '/senadores'


def trigger_mailer_senator(sid):
    extra_paths = '/{}/update_followers'.format(sid)
    requests.post('{}{}{}'.format(URL, PATH, extra_paths))
    sleep(1)
