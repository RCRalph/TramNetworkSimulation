import os
from sqlite3 import Cursor
from abc import ABC, abstractmethod


class DatabasePreparer(ABC):
    def __init__(self, cursor: Cursor):
        self.cursor = cursor

    @abstractmethod
    def _drop_tables(self):
        pass

    @abstractmethod
    def _create_tables(self):
        pass

    def prepare_database(self):
        if os.environ.get("REFRESH_DATABASE").lower() == "yes":
            self._drop_tables()

        self._create_tables()
