from .database_preparer import DatabasePreparer


class RoutesDatabaseSetup(DatabasePreparer):
    def _drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS tram_route_nodes")

    def _create_tram_route_nodes_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tram_route_nodes (
                start_stop_id INTEGER,
                end_stop_id INTEGER,
                node_index INTEGER CHECK (node_index > 0),
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL,
                distance DOUBLE NOT NULL CHECK (distance >= 0),

                FOREIGN KEY (start_stop_id) REFERENCES tram_stops (id) ON DELETE CASCADE,
                FOREIGN KEY (end_stop_id) REFERENCES tram_stops (id) ON DELETE CASCADE,
                PRIMARY KEY (start_stop_id, end_stop_id, node_index)
            ) WITHOUT ROWID;
        """)

    def _create_tables(self):
        self._create_tram_route_nodes_table()
