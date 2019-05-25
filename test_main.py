from datetime import datetime
from unittest import main, TestCase
from unittest.mock import MagicMock, ANY
from main import Bot, db, periodos, senadores, proyectos


class TestBot(TestCase):

    def setUp(self):
        self.bot = Bot()
        self.bot.connection.close = MagicMock()
        db.insert = MagicMock()
        db.select = MagicMock(return_value=[905])
        senadores.fetch_ids = MagicMock(return_value=[905])
        senadores.fetch_detail = MagicMock(return_value='senador')
        periodos.fetch_periodos = MagicMock(return_value='periodos')
        proyectos.fetch_new_proyectos = MagicMock(return_value=[{
            'fecha': datetime.now().date(),
            'boletin': 905,
            'estado': 'test'
        }])
        proyectos.fetch_resumen = MagicMock(return_value='test resumen')
        proyectos.fetch_autores = MagicMock(return_value=[[905, 1], [905, 2]])

    def test_run(self):
        self.bot.actualizar_senadores = MagicMock()
        self.bot.actualizar_proyectos = MagicMock()
        self.bot.commit_actualizacion = MagicMock()

        self.bot.run()

        self.bot.connection.close.assert_called_once()
        self.bot.actualizar_proyectos.assert_called_once()
        self.bot.actualizar_senadores.assert_called_once()
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
        db.insert.assert_called_with(ANY, 'Senadors', 'senadores')

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

        db.insert.assert_called_once()
        db.insert.assert_called_with(ANY, 'Proyectos', 'proyectos')

    def test_should_add_autores(self):
        self.bot.agregar_senadores_autores([805])

        proyectos.fetch_autores.assert_called_once()
        proyectos.fetch_autores.assert_called_with(805)

        db.insert.assert_called_once()
        db.insert.assert_called_with(
            ANY, 'SenadorProyectos', [[905, 1], [905, 2]])

    def test_should_add_periodos(self):
        self.bot.agregar_periodos([905])

        periodos.fetch_periodos.assert_called_once()
        periodos.fetch_periodos.assert_called_with([905])
        db.insert.assert_called_once()
        db.insert.assert_called_with(ANY, 'Periodos', 'periodos')

    def test_should_commit_actualizacion(self):
        self.bot.commit_actualizacion()

        db.insert.assert_called_once()
        db.insert.assert_called_with(ANY, 'Updates', ANY)

    def test_should_scrap_ids_senadores(self):
        return_value = self.bot.scrap_ids_senadores()
        senadores.fetch_ids.assert_called_once()
        self.assertEqual(return_value, [905])

    def test_should_scrap_new_senadores(self):
        return_value = self.bot.scrap_new_senadores([905, 885])
        self.assertEqual(senadores.fetch_detail.call_count, 2)
        self.assertEqual(['senador', 'senador'], return_value)
