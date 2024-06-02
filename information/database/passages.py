from classes.day_type import DayType
from .database_preparer import DatabasePreparer


class PassageDatabaseSetup(DatabasePreparer):
    def _drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS tram_passage_stops")
        self.cursor.execute("DROP TABLE IF EXISTS tram_passages")

    def _create_tram_passages_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS tram_passages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tram_line_id INTEGER NOT NULL,
                day TEXT NOT NULL CHECK (day IN {tuple(DayType.values())}),

                FOREIGN KEY (tram_line_id) REFERENCES tram_lines (id) ON DELETE CASCADE
            )
        """)

    def _create_tram_passage_stops_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS tram_passage_stops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tram_stop_id INTEGER NOT NULL,
                tram_passage_id INTEGER NOT NULL,
                stop_index INTEGER NOT NULL CHECK (stop_index > 0),
                hour INTEGER NOT NULL,
                minute INTEGER NOT NULL,

                FOREIGN KEY (tram_stop_id) REFERENCES tram_stops (id) ON DELETE CASCADE,
                FOREIGN KEY (tram_passage_id) REFERENCES tram_passages (id) ON DELETE CASCADE,
                UNIQUE (tram_passage_id, stop_index) ON CONFLICT ABORT
            )
        """)

    def create_tables(self):
        self._create_tram_passages_table()
        self._create_tram_passage_stops_table()
