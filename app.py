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
    return send_file("visualization/client/dist/index.html")


@app.route("/api/stop-locations")
def stop_locations():
    with closing(sqlite3.connect("db.sqlite")) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("""
            SELECT id, name, latitude, longitude
            FROM tram_stops
        """)

        return [
            {"id": item[0], "name": item[1], "latitude": item[2], "longitude": item[3]}
            for item in cursor.fetchall()
        ]


@app.route("/api/tram-passages")
def tram_passages():
    with closing(sqlite3.connect("db.sqlite")) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("""
            SELECT
                tram_passage_stops.tram_passage_id,
                tram_lines.number,
                tram_stops.name,
                tram_stops.latitude,
                tram_stops.longitude,
                tram_passage_stops.hour,
                tram_passage_stops.minute
            FROM tram_passage_stops
                JOIN tram_stops ON tram_passage_stops.tram_stop_id = tram_stops.id
                JOIN tram_passages ON tram_passage_stops.tram_passage_id = tram_passages.id
                JOIN tram_lines ON tram_passages.tram_line_id = tram_lines.id
            WHERE tram_passages.day = 'H'
            ORDER BY tram_passage_stops.stop_index, tram_passage_stops.hour, tram_passage_stops.minute
        """)

        result = {}
        for row in cursor.fetchall():
            if row[0] not in result:
                result[row[0]] = {
                    "id": row[0],
                    "tram_line": row[1],
                    "stops": []
                }

            result[row[0]]["stops"].append({
                "name": row[2],
                "latitude": row[3],
                "longitude": row[4],
                "hour": row[5],
                "minute": row[6]
            })

        return list(result.values())


if __name__ == "__main__":
    app.run()
