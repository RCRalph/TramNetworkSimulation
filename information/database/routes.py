from .database_preparer import DatabasePreparer


class RoutesDatabaseSetup(DatabasePreparer):
    def _drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS tram_routes")
        self.cursor.execute("DROP TABLE IF EXISTS tram_route_nodes")

    def _create_tram_routes_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tram_routes (
                id INTEGER PRIMARY KEY
                start_stop_id INTEGER NOT NULL,
                end_stop_id INTEGER NOT NULL,

                FOREIGN KEY (start_stop_id) REFERENCES tram_stops (id) ON DELETE CASCADE,
                FOREIGN KEY (end_stop_id) REFERENCES tram_stops (id) ON DELETE CASCADE,
                UNIQUE (start_stop_id, end_stop_id) ON CONFLICT ABORT
            );
        """)

    def _create_tram_route_nodes_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tram_route_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tram_route_id INTEGER NOT NULL,
                node_index INTEGER NOT NULL CHECK (node_index > 0),
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL,
                distance_at_end DECIMAL(10, 3) NOT NULL CHECK (distance_at_end > 0),

                FOREIGN KEY (tram_route_id) REFERENCES tram_routes (id) ON DELETE CASCADE
            )
        """)

    def _create_tables(self):
        self._create_tram_routes_table()
        self._create_tram_route_nodes_table()
