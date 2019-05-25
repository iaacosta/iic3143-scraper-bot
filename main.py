import db
import scraper.senadores as senadores
import scraper.periodos as periodos
from helpers import logger
from datetime import datetime


class Bot:
    def __init__(self):
        self.connection = db.connect()

    def run(self):
        self.actualizar_senadores()
        self.commit_actualizacion()
        self.connection.close()

    def actualizar_senadores(self):
        logger('Verificando cambios en los senadores')

        web_ids = set(self.scrap_ids_senadores())
        db_ids = set(db.fetch_senadores(self.connection, ['id']))

        diff = web_ids - db_ids
        if len(diff) == 0:
            logger('No hay cambios')
            return

        logger('Cambios detectados, scrapeando nueva información')
        nuevos = self.scrap_new_senadores(diff)
        logger('Agregando {} senador{} a la base de datos'.format(
            len(nuevos), 'es' if len(nuevos) > 1 else ''))
        db.insert(self.connection, 'Senadors', nuevos)
        logger('Senadores agregados a la base de datos')
        self.agregar_periodos(map(lambda senador: senador['id'], nuevos))

    def agregar_periodos(self, ids):
        logger('Recolectando información de los periodos')
        periodos_db = periodos.fetch_periodos(ids)
        logger('Agregando periodos a la base de datos')
        db.insert(self.connection, 'Periodos', periodos_db)
        logger('Periodos agregados a la base de datos')

    def commit_actualizacion(self):
        db.insert(self.connection, 'Updates', [
            {'"createdAt"': datetime.now()}])

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
