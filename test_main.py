from datetime import datetime
from unittest import main, TestCase
from unittest.mock import MagicMock, ANY
from main import Bot, db, periodos, senadores, proyectos, comisiones, sleep

sleep = MagicMock(return_value='nada')


class TestBot(TestCase):

    def setUp(self):
        self.bot = Bot()
        self.bot.connection.close = MagicMock()
        db.insert = MagicMock()
        db.select = MagicMock(return_value=[905])
        senadores.fetch_ids = MagicMock(return_value=[905])
        senadores.fetch_detail = MagicMock(return_value='senador')

        periodos.fetch_periodos = MagicMock(return_value='periodos')

        proyectos.fetch_resumen = MagicMock()
        proyectos.fetch_autores = MagicMock(return_value=[[905, 1], [905, 2]])
        proyectos.fetch_new_proyectos = MagicMock(return_value=[{
            'fecha': datetime.now().date(),
            'boletin': 905,
            'estado': 'test'
        }])

        comisiones.fetch_detail = MagicMock()
        comisiones.fetch_integrantes = MagicMock(return_value=[
            {'cid': 805, 'pid': 2}
        ])
        comisiones.fetch_proyectos_in_comision = MagicMock(
            return_value=set(['0-0', '1-0']))
        comisiones.fetch_new_comisiones = MagicMock(return_value=[{
            'id': 905,
            'nombre': 'test',
            'tipo': 'test'
        }])

    def test_run(self):
        self.bot.actualizar_senadores = MagicMock()
        self.bot.actualizar_proyectos = MagicMock()
        self.bot.actualizar_comisiones = MagicMock()
        self.bot.actualizar_proyectos_por_comision = MagicMock()
        self.bot.actualizar_asistencias = MagicMock()
        self.bot.commit_actualizacion = MagicMock()

        self.bot.run()

        self.bot.connection.close.assert_called_once()
        self.bot.actualizar_proyectos.assert_called_once()
        self.bot.actualizar_comisiones.assert_called_once()
        self.bot.actualizar_senadores.assert_called_once()
        self.bot.actualizar_proyectos_por_comision.assert_not_called()
        self.bot.commit_actualizacion.assert_called_once()

    def test_run_if_added_leyes(self):
        self.bot.actualizar_senadores = MagicMock()
        self.bot.actualizar_proyectos = MagicMock()
        self.bot.actualizar_comisiones = MagicMock()
        self.bot.actualizar_proyectos_por_comision = MagicMock()
        self.bot.actualizar_asistencias = MagicMock()
        self.bot.commit_actualizacion = MagicMock()
        self.bot.new_leyes = set([0, 1])

        self.bot.run()

        self.bot.connection.close.assert_called_once()
        self.bot.actualizar_proyectos.assert_called_once()
        self.bot.actualizar_comisiones.assert_called_once()
        self.bot.actualizar_senadores.assert_called_once()
        self.bot.actualizar_proyectos_por_comision.assert_called_once()
        self.bot.commit_actualizacion.assert_called_once()

    def test_should_not_scrap_senadores_if_not_needed(self):
        self.bot.scrap_new_senadores = MagicMock()
        self.bot.actualizar_senadores()
        self.bot.scrap_new_senadores.assert_not_called()

    def test_should_scrap_senadores_if_needed(self):
        self.bot.scrap_ids_senadores = MagicMock(return_value=[905, 805])
        self.bot.scrap_new_senadores = MagicMock(return_value='senadores')
        self.bot.agregar_periodos = MagicMock()

        self.bot.actualizar_senadores()

        self.bot.scrap_new_senadores.assert_called_once()
        self.bot.scrap_new_senadores.assert_called_with(set([805]))
        self.bot.agregar_periodos.assert_called_once()
        db.insert.assert_called_once()
        db.insert.assert_called_with(
            self.bot.connection, 'Senadors', 'senadores')

    def test_should_not_scrap_proyectos_if_not_needed(self):
        self.bot.scrap_new_proyectos = MagicMock()
        self.bot.actualizar_proyectos()
        self.bot.scrap_new_proyectos.assert_not_called()

    def test_should_scrap_proyectos_if_needed(self):
        sample_proyectos = [
            {'fecha': datetime.now().date(), 'boletin': 905, 'estado': 'test'},
            {'fecha': datetime.now().date(), 'boletin': 805, 'estado': 'test'},
        ]
        proyectos.fetch_new_proyectos = MagicMock(
            return_value=sample_proyectos)

        self.bot.scrap_new_proyectos = MagicMock(return_value='proyectos')
        self.bot.agregar_senadores_autores = MagicMock()

        self.bot.actualizar_proyectos()

        self.bot.scrap_new_proyectos.assert_called_once()
        self.bot.agregar_senadores_autores.assert_called_once()

        boletin_called = self.bot.scrap_new_proyectos.call_args_list[0][0][0][0]['boletin']
        self.assertEqual(boletin_called, 805)
        self.assertGreater(len(self.bot.new_leyes), 0)

        db.insert.assert_called_once()
        db.insert.assert_called_with(
            self.bot.connection, 'Proyectos', 'proyectos')

    def test_should_not_scrap_comisiones_if_not_needed(self):
        self.bot.scrap_new_comisiones = MagicMock()
        self.bot.actualizar_comisiones()
        self.bot.scrap_new_comisiones.assert_not_called()

    def test_should_scrap_comisiones_if_needed(self):
        sample_comisiones = [
            {'id': 905, 'nombre': 'test 0'},
            {'id': 805, 'nombre': 'test 1'},
        ]

        comisiones.fetch_new_comisiones = MagicMock(
            return_value=sample_comisiones)

        self.bot.scrap_new_comisiones = MagicMock(return_value='comisiones')
        self.bot.agregar_integrantes = MagicMock()

        self.bot.actualizar_comisiones()

        self.bot.scrap_new_comisiones.assert_called_once()
        self.bot.agregar_integrantes.assert_called_once()

        id_called = self.bot.scrap_new_comisiones.call_args_list[0][0][0][0]['id']
        self.assertEqual(id_called, 805)

        db.insert.assert_called_once()
        db.insert.assert_called_with(
            self.bot.connection, 'Comitions', 'comisiones')

    def test_should_scrap_new_proyectos_in_comisiones_base(self):
        expected_values = [{'cid': 905, 'pid': 0}, {'cid': 905, 'pid': 1}]
        self.bot.get_pids_from_boletines = MagicMock(
            return_value=expected_values)

        self.bot.new_leyes = set(['0-0', '1-0'])
        self.bot.actualizar_proyectos_por_comision()

        db.select.assert_called_with(self.bot.connection, ['id'], 'Comitions')
        db.insert.assert_called_with(
            self.bot.connection, 'ProjectComitions', expected_values)
        self.bot.get_pids_from_boletines.assert_called_once()
        self.bot.get_pids_from_boletines.assert_called_with([
            {'cid': 905, 'boletin': '0-0'},
            {'cid': 905, 'boletin': '1-0'},
        ])

    def test_should_assign_comition_0_to_non_existant_project(self):
        self.bot.get_pids_from_boletines = MagicMock()

        self.bot.new_leyes = set(['0-0', '2-0'])
        self.bot.actualizar_proyectos_por_comision()

        self.bot.get_pids_from_boletines.assert_called_once()
        self.bot.get_pids_from_boletines.assert_called_with([
            {'cid': 905, 'boletin': '0-0'},
            {'cid': 0, 'boletin': '2-0'},
        ])

    def test_should_add_autores(self):
        self.bot.agregar_senadores_autores([805])

        proyectos.fetch_autores.assert_called_once()
        proyectos.fetch_autores.assert_called_with(805)

        db.insert.assert_called_once()
        db.insert.assert_called_with(
            self.bot.connection, 'SenadorProyectos', [[905, 1], [905, 2]])

    def test_should_add_periodos(self):
        self.bot.agregar_periodos([905])

        periodos.fetch_periodos.assert_called_once()
        periodos.fetch_periodos.assert_called_with([905])
        db.insert.assert_called_once()
        db.insert.assert_called_with(
            self.bot.connection, 'Periodos', 'periodos')

    def test_should_add_integrantes(self):
        self.bot.agregar_integrantes([905])

        comisiones.fetch_integrantes.assert_called_once()
        comisiones.fetch_integrantes.assert_called_with(905)
        db.insert.assert_called_once()
        db.insert.assert_called_with(
            self.bot.connection, 'SenatorComitions', [{'cid': 805, 'pid': 2}])

    def test_should_commit_actualizacion(self):
        self.bot.commit_actualizacion()

        db.insert.assert_called_once()
        db.insert.assert_called_with(self.bot.connection, 'Updates', ANY)

    def test_should_scrap_ids_senadores(self):
        return_value = self.bot.scrap_ids_senadores()
        senadores.fetch_ids.assert_called_once()
        self.assertEqual(return_value, [905])

    def test_should_scrap_new_senadores(self):
        return_value = self.bot.scrap_new_senadores([905, 885])
        self.assertEqual(senadores.fetch_detail.call_count, 2)
        self.assertEqual(['senador', 'senador'], return_value)

    def test_should_mutate_new_proyectos(self):
        self.bot.scrap_new_proyectos([{'boletin': 905}, {'boletin': 885}])
        self.assertEqual(proyectos.fetch_resumen.call_count, 2)

    def test_should_mutate_new_comisiones(self):
        self.bot.scrap_new_comisiones([{'id': 905}, {'id': 885}])
        self.assertEqual(comisiones.fetch_detail.call_count, 2)
