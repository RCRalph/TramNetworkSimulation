import sqlite3
from contextlib import closing

from flask import Flask, send_file

app = Flask(
    __name__,
    static_folder="client/dist",
    static_url_path=""
)


@app.route("/")
def index():
    return send_file("client/dist/index.html")


@app.route("/api/stop-locations")
def stop_locations():
    with closing(sqlite3.connect("../db.sqlite")) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("""
            SELECT id, name, latitude, longitude
            FROM tram_stops
        """)

        return [
            {"id": item[0], "name": item[1], "latitude": item[2], "longitude": item[3]}
            for item in cursor.fetchall()
        ]


@app.route("/api/tram-passage")
def tram_passage():
    with closing(sqlite3.connect("../db.sqlite")) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("""
            SELECT latitude, longitude
            FROM tram_passage_stops
                JOIN tram_stops ON tram_passage_stops.tram_stop_id = tram_stops.id
            WHERE tram_passage_stops.tram_passage_id = 1
            ORDER BY tram_passage_stops.stop_index
        """)

        return [{"latitude": item[0], "longitude": item[1]} for item in cursor.fetchall()]


if __name__ == "__main__":
    app.run()
