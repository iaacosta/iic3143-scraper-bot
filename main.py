import db
import scraper.senadores as senadores
import scraper.periodos as periodos
import scraper.proyectos as proyectos
import scraper.comisiones as comisiones
import scraper.asistencias as asistencias
from functools import reduce
from helpers import logger, trigger_mailer_senator
from time import sleep
from datetime import datetime
from sys import argv


class Bot:
    def __init__(self, custom_from_date=None):
        self.connection = db.connect()
        self.new_leyes = []
        self.custom_form_date = custom_from_date

    def run(self):
        self.actualizar_senadores()
        self.actualizar_proyectos()
        self.actualizar_comisiones()

        if len(self.new_leyes) != 0:
            self.actualizar_proyectos_por_comision()

        self.actualizar_asistencias()
        self.commit_actualizacion()
        self.connection.close()

    def actualizar_senadores(self):
        logger('Verificando cambios en los senadores')

        web_ids = set(self.scrap_ids_senadores())
        db_ids = set(db.select(self.connection, ['id'], 'Senadors'))

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

    def actualizar_proyectos(self):
        logger('Verificando cambios en proyectos de ley')

        web_data = proyectos.fetch_new_proyectos(self.custom_form_date)
        db_ids = set(db.select(self.connection, ['boletin'], 'Proyectos'))
        web_ids = set(map(lambda proy: proy['boletin'], web_data))

        diff = web_ids - db_ids
        if len(diff) == 0:
            logger('No hay cambios')
            return

        self.new_leyes = diff
        new_data = list(filter(lambda proy: proy['boletin'] in diff, web_data))
        logger('Cambios detectados, scrapeando nueva información')
        nuevos = self.scrap_new_proyectos(new_data)

        logger('Agregando {} proyecto{} a la base de datos'.format(
            len(nuevos), 's' if len(nuevos) > 1 else ''))
        db.insert(self.connection, 'Proyectos', nuevos)

        logger('Proyectos agregados a la base de datos')
        self.agregar_senadores_autores(map(lambda proy: proy['id'], nuevos))

    def actualizar_comisiones(self):
        logger('Verificando cambios en comisiones vigentes')

        web_data = comisiones.fetch_new_comisiones()
        db_ids = set(db.select(self.connection, ['id'], 'Comitions'))
        web_ids = set(map(lambda com: com['id'], web_data))

        diff = web_ids - db_ids
        if len(diff) == 0:
            logger('No hay cambios')
            return

        new_data = list(filter(lambda com: com['id'] in diff, web_data))
        logger('Cambios detectados, scrapeando nueva información')
        nuevas = self.scrap_new_comisiones(new_data)

        logger('Agregando {} comisi{} a la base de datos'.format(
            len(nuevas), 'iones' if len(nuevas) > 1 else 'ón'))
        db.insert(self.connection, 'Comitions', nuevas)

        logger('Comisiones agregadas a la base de datos')
        self.agregar_integrantes(map(lambda com: com['id'], nuevas))

    def actualizar_proyectos_por_comision(self):
        logger('Hay {0} nuevo{1} proyecto{1}, se requiere verificar de que comisiones son'.format(
            len(self.new_leyes),
            's' if len(self.new_leyes) > 1 else ''
        ))

        cids = db.select(self.connection, ['id'], 'Comitions')

        correspondencias = []
        for cid in cids:
            if len(self.new_leyes) == 0:
                logger('No hay mas proyectos por buscar')
                break

            logger('\tcid={}'.format(cid))
            proyectos_en_comision = comisiones.fetch_proyectos_in_comision(cid)
            inter = self.new_leyes.intersection(proyectos_en_comision)

            if len(inter) > 0:
                logger('\t\t{0} proyecto{1} encontrado{1}'.format(
                    len(inter), 's' if len(inter) > 1 else ''))

            for boletin in inter:
                correspondencias.append({'cid': cid, 'boletin': boletin})
                self.new_leyes.remove(boletin)

            sleep(0.7)

        if len(self.new_leyes) > 0:
            logger('Quedaron {} proyectos sin comisión válida. '.format(len(self.new_leyes))
                   + 'Se asume que son de la cámara de diputados')
            correspondencias += list(
                map(lambda bol: {'cid': 0, 'boletin': bol}, self.new_leyes))

        correspondencias.sort(key=lambda c: c['boletin'])
        correspondencias = self.get_pids_from_boletines(correspondencias)
        logger('Agregando {} relacion{} a la base de datos'.format(
            len(correspondencias), 'es' if len(correspondencias) > 1 else ''))

        db.insert(self.connection, 'ProjectComitions', correspondencias)
        logger('Proyectos agregados a la base de datos')

    def actualizar_asistencias(self):
        logger('Verificando cambios en asistencias')

        refreshed_data = asistencias.fetch_new_asistencias()
        db_ids = db.select(self.connection, ['lid'], 'Assistance')

        if refreshed_data[0]['lid'] in db_ids:
            logger('Legislación ya existe, borrando los datos anteriores')
            condition = map(lambda d: '(lid={} AND sid={})'.format(
                d['lid'], d['sid']), refreshed_data)
            db.delete(self.connection, 'Assistance', ' OR '.join(condition))

        db.insert(self.connection, 'Assistance', refreshed_data)
        logger('Asistencias agregadas a la base de datos')

    def agregar_periodos(self, ids):
        logger('Recolectando información de los periodos')
        periodos_db = periodos.fetch_periodos(ids)
        logger('Agregando periodos a la base de datos')
        db.insert(self.connection, 'Periodos', periodos_db)
        logger('Periodos agregados a la base de datos')

    def agregar_senadores_autores(self, pids):
        logger('Scrapeando autores de nuevos proyectos')
        autores = []
        for pid in pids:
            logger('\tpid={}'.format(pid))
            autores += proyectos.fetch_autores(pid)
            sleep(0.7)
        logger('Agregando {} autor{} a la base de datos'.format(
            len(autores), 'es' if len(autores) > 1 else ''))
        db.insert(self.connection, 'SenadorProyectos', autores)

        logger('Gatillando envío a los suscriptores')
        for sid in set(map(lambda rel: rel['sid'], autores)):
            logger('\tsid={}'.format(sid))
            trigger_mailer_senator(sid)

    def agregar_integrantes(self, cids):
        logger('Scrapeando integrantes de nuevas comisiones')
        integrantes = []
        for cid in cids:
            logger('\tpid={}'.format(cid))
            integrantes += comisiones.fetch_integrantes(cid)
            sleep(0.7)
        logger('Agregando {} integrante{} a la base de datos'.format(
            len(integrantes), 's' if len(integrantes) > 1 else ''))
        db.insert(self.connection, 'SenatorComitions', integrantes)

    def commit_actualizacion(self):
        db.insert(self.connection, 'Updates', [
            {'"createdAt"': datetime.now()}])

    def get_pids_from_boletines(self, correspondencias):
        boletines = map(lambda rel: rel['boletin'], correspondencias)
        condition = " WHERE boletin IN ('{}')".format("','".join(boletines))
        pid_dict = dict(db.select(self.connection, [
                        'boletin', 'id'], 'Proyectos', condition=condition))

        return list(map(lambda rel: {
            'cid': rel['cid'],
            'pid': pid_dict[rel['boletin']],
        }, correspondencias))

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
            sleep(0.7)
        return nuevos

    @staticmethod
    def scrap_new_proyectos(_proyectos):
        nuevos = []
        for proyecto in _proyectos:
            logger('\tboletin={}'.format(proyecto['boletin']))
            proyectos.fetch_resumen(proyecto)
            nuevos.append(proyecto)
            sleep(0.7)
        return nuevos

    @staticmethod
    def scrap_new_comisiones(_comisiones):
        nuevas = []
        for comision in _comisiones:
            logger('\tcid={}'.format(comision['id']))
            comisiones.fetch_detail(comision)
            nuevas.append(comision)
            sleep(0.7)
        return nuevas


if __name__ == '__main__':
    if len(argv) > 1:
        bot = Bot(argv[2])
    else:
        bot = Bot()

    bot.run()
