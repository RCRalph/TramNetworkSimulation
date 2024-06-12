from .database_preparer import DatabasePreparer
from ..classes import DayType


class TimetableDatabaseSetup(DatabasePreparer):
    def _drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS tram_departures")
        self.cursor.execute("DROP TABLE IF EXISTS tram_line_variants")
        self.cursor.execute("DROP TABLE IF EXISTS tram_lines")

    def _create_tram_lines_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tram_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE ON CONFLICT REPLACE
            )
        """)

    def _create_tram_line_variants_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tram_line_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tram_line_id INTEGER,
                name TEXT NOT NULL,

                FOREIGN KEY (tram_line_id) REFERENCES tram_lines (id) ON DELETE CASCADE,
                UNIQUE (tram_line_id, name) ON CONFLICT REPLACE
            )
        """)

    def _create_tram_departures_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS tram_departures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tram_stop_id INTEGER DEFAULT NULL,
                tram_line_variant_id INTEGER NOT NULL,
                stop_index INTEGER NOT NULL,
                day TEXT NOT NULL CHECK (day IN {tuple(DayType.values())}),
                hour INTEGER NOT NULL,
                minute INTEGER NOT NULL,

                FOREIGN KEY (tram_stop_id) REFERENCES tram_stops (id) ON DELETE CASCADE,
                FOREIGN KEY (tram_line_variant_id) REFERENCES tram_line_variants (id) ON DELETE CASCADE
            )
        """)

    def _create_tables(self):
        self._create_tram_lines_table()
        self._create_tram_line_variants_table()
        self._create_tram_departures_table()
