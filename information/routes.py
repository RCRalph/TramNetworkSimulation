import os
import sqlite3
from collections import defaultdict
from contextlib import closing
from queue import PriorityQueue

from dotenv import load_dotenv
from overpy import Overpass

from .classes import GraphNode
from .database import RoutesDatabaseSetup


class RouteMaker:
    def __init__(self, cursor: sqlite3.Cursor):
        self.cursor = cursor
        self.overpass = Overpass()

        self.graph: dict[int, GraphNode] = {}
        self.set_tram_railway_graph()

    def set_tram_railway_graph(self):
        tram_railways_query_result = self.overpass.query("""
            [out:json];
            area["name"="Kraków"]->.search_area;
            (
                way["railway"="tram"]["oneway"="yes"](area.search_area);
                >;
            );
            out geom;
        """)

        for item in tram_railways_query_result.ways:
            nodes = item.get_nodes()

            for node in filter(lambda x: x.id not in self.graph, nodes):
                self.graph[node.id] = GraphNode(node.id, node.lat, node.lon)

            for start, end in zip(nodes, nodes[1:]):
                self.graph[start.id].edges.append(self.graph[end.id])

    def get_list_of_neighboring_stops(self) -> list[tuple[int, int]]:
        self.cursor.execute("""
            SELECT DISTINCT
                tram_passage_stops.tram_stop_id AS start_stop_id,
                TPS.tram_stop_id AS end_stop_id
            FROM tram_passage_stops
                JOIN tram_passage_stops TPS ON tram_passage_stops.tram_passage_id = TPS.tram_passage_id
            WHERE tram_passage_stops.stop_index = TPS.stop_index - 1
        """)

        return self.cursor.fetchall()

    def route_between_nodes(self, start_node_id: int, end_node_id: int):
        """
            This method implements a modified version of Dijkstra's algorithm.
            In this implementation it is possible to not only find the shortest
            distance between two nodes, but also the shortest path between them.
            The implementation also does not search the entire graph, but stops
            when no further improvement is possible.
        """

        priority_queue: PriorityQueue[tuple[float, GraphNode]] = PriorityQueue()
        parents: dict[int, GraphNode | None] = {}
        distances: dict[int, float] = defaultdict(lambda: float("inf"))

        priority_queue.put((0, self.graph[start_node_id]))
        parents[start_node_id] = None
        distances[start_node_id] = 0

        while priority_queue.not_empty:
            current_distance, root = priority_queue.get()

            if current_distance > distances[end_node_id]:
                break

            for node in self.graph[root.id].edges:
                new_distance = distances[root.id] + root.distance_to(node)

                if distances[node.id] > new_distance:
                    distances[node.id] = new_distance
                    parents[node.id] = root
                    priority_queue.put((distances[node.id], node))

        result: list[tuple[GraphNode, float]] = []

        node = self.graph[end_node_id]
        while node is not None:
            result.append((node, distances[node.id]))
            node = parents[node.id]

        result.reverse()

        return result

    def make_routes(self):
        for start_id, end_id in self.get_list_of_neighboring_stops():
            self.cursor.executemany(
                """
                    INSERT INTO tram_route_nodes (start_stop_id, end_stop_id, node_index, latitude, longitude, distance)
                    VALUES (?, ?, ?, ?, ? ,?)
                """,
                (
                    (start_id, end_id, i + 1, float(node.latitude), float(node.longitude), distance)
                    for i, (node, distance) in enumerate(self.route_between_nodes(start_id, end_id))
                )
            )


def main():
    load_dotenv()

    with (
        closing(sqlite3.connect(os.environ.get('DATABASE_NAME'), isolation_level=None)) as connection,
        closing(connection.cursor()) as cursor
    ):
        RoutesDatabaseSetup(cursor).prepare_database()
        RouteMaker(cursor).make_routes()


if __name__ == "__main__":
    main()
