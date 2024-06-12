import sqlite3
from collections import defaultdict
from contextlib import closing

from flask import Flask, send_file, abort

from information.classes import DayType

app = Flask(
    __name__,
    static_folder="client/dist",
    static_url_path=""
)


@app.route("/")
def index():
    return send_file("client/dist/index.html")


@app.route("/api/global-settings")
def global_settings():
    result = {
        "day_types": DayType.names()
    }

    with closing(sqlite3.connect("db.sqlite")) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("""
            SELECT id, name, latitude, longitude
            FROM tram_stops
        """)

        result["stop_locations"] = [
            {"id": item[0], "name": item[1], "latitude": item[2], "longitude": item[3]}
            for item in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT start_stop_id, end_stop_id, latitude, longitude, distance
            FROM tram_route_nodes
            ORDER BY node_index
        """)

        result["tram_routes"] = defaultdict(lambda: defaultdict(list))
        for start_id, end_id, latitude, longitude, distance in cursor.fetchall():
            result["tram_routes"][start_id][end_id].append({
                "latitude": latitude,
                "longitude": longitude,
                "distance": distance
            })

    return result


@app.route("/api/tram-passages/<day_type>")
def tram_passages(day_type):
    if day_type not in DayType.names():
        abort(404)

    with closing(sqlite3.connect("db.sqlite")) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("""
            SELECT
                tram_passage_stops.tram_stop_id,
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
            WHERE tram_passages.day = ?
            ORDER BY tram_passage_stops.stop_index, tram_passage_stops.hour, tram_passage_stops.minute
        """, [DayType[day_type].value])

        result = {}
        for row in cursor.fetchall():
            if row[1] not in result:
                result[row[1]] = {
                    "passage_id": row[1],
                    "tram_line": row[2],
                    "stops": []
                }

            result[row[1]]["stops"].append({
                "node_id": row[0],
                "name": row[3],
                "latitude": row[4],
                "longitude": row[5],
                "hour": row[6],
                "minute": row[7]
            })

        return list(result.values())


if __name__ == "__main__":
    app.run()
