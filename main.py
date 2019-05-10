import scraper.senadores as senadores
import db.main as db
from helpers.main import logger


class Bot:
    def __init__(self):
        self.connection = db.connect()

    def run(self):
        self.actualizar_senadores()
        self.connection.close()

    def actualizar_senadores(self):
        logger('Verificando cambios en los senadores')

        web_ids = set(self.scrap_ids_senadores())
        db_ids = set(db.fetch_senadores(self.connection, ['id']))

        diff = web_ids - db_ids
        diff = diff.union(set([905]))
        if len(diff) == 0:
            logger('No hay cambios')
            return

        logger('Cambios detectados, scrapeando nueva información')
        nuevos = self.scrap_new_senadores(diff)
        logger('Agregando {} senadores a la base de datos'.format(len(nuevos)))
        db.insert_senadores(self.connection, nuevos)

    @staticmethod
    def scrap_ids_senadores():
        tabla = senadores.fetch_table_actuales()
        return senadores.fetch_ids(tabla)

    @staticmethod
    def scrap_new_senadores(ids):
        nuevos = list()
        for _id in ids:
            logger('\tsid={}'.format(_id))
            nuevos.append(senadores.fetch_detail(_id))
        return nuevos


if __name__ == '__main__':
    bot = Bot()
    bot.run()
