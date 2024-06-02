from .database_preparer import DatabasePreparer


class StopsDatabaseSetup(DatabasePreparer):
    def _drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS tram_stops")

    def _create_tram_stops_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tram_stops (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE ON CONFLICT REPLACE,
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL
            );
        """)

    def _create_tables(self):
        self._create_tram_stops_table()
