import io

import folium
from PySide6.QtSql import QSqlQuery
from PySide6.QtWebEngineWidgets import QWebEngineView


class FoliumMapWidget(QWebEngineView):
    folium_map: folium.Map

    def __init__(self):
        super().__init__()

        self.folium_map = folium.Map(
            location=self.get_map_center(),
            zoom_start=13
        )

        self.add_stops_to_map()

        data = io.BytesIO()
        self.folium_map.save(data, close_file=False)

        self.setHtml(data.getvalue().decode())
        self.show()

    @staticmethod
    def get_map_center():
        query = QSqlQuery()
        query.exec("""
            SELECT
                (MAX(latitude) - MIN(latitude)) / 2 + MIN(latitude),
                (MAX(longitude) - MIN(longitude)) / 2 + MIN(longitude)
            FROM tram_stops
        """)

        query.next()

        return query.value(0), query.value(1)

    def add_stops_to_map(self):
        query = QSqlQuery()
        query.exec("""
            SELECT name, latitude, longitude
            FROM tram_stops
        """)

        stop_markers = []
        while query.next():
            stop_markers.append(folium.CircleMarker(
                location=(query.value(1), query.value(2)),
                radius=5,
                tooltip=query.value(0),
                fill=True
            ))

        for marker in stop_markers:
            marker.add_to(self.folium_map)
