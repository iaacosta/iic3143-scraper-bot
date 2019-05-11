from unittest.mock import MagicMock


class MockCursor:
    def __init__(self):
        self.execute = MagicMock()
        self.close = MagicMock()
        self.fetchall = MagicMock(return_value=['MockCursorReturn'])


class MockConector:
    def __init__(self, url):
        self.cursor = MagicMock(return_value=MockCursor())
        self.close = MagicMock()
        self.commit = MagicMock()
