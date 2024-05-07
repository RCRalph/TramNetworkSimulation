import os
import sqlite3
from contextlib import closing

import overpy
from dotenv import load_dotenv

from classes import TramStop

if __name__ == "__main__":
    load_dotenv()

    api = overpy.Overpass()

    tram_stops_query_result = api.query("""
        [out:json];
        area["name"="Kraków"]->.search_area;
        node["tram"="yes"]["railway"="tram_stop"](area.search_area);
        out;
    """)

    tram_stop_set = {
        TramStop(item.id, item.tags.get("name"), item.lat, item.lon)
        for item in tram_stops_query_result.nodes
    }

    with (
        closing(sqlite3.connect(os.environ.get('DATABASE_NAME'), isolation_level=None)) as connection,
        closing(connection.cursor()) as cursor
    ):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tram_stops (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE ON CONFLICT REPLACE,
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL
            );
        """)

        cursor.executemany(
            "INSERT INTO tram_stops VALUES (?, ?, ?, ?)",
            (item.to_sql_parameters() for item in tram_stop_set)
        )
