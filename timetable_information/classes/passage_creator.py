from collections import defaultdict
from sqlite3 import Cursor

from .day_type import DayType
from .departure import Departure
from .tram_passage import TramPassage
from .tram_stop import TramStop


class PassageCreator:
    tram_stops: dict[int, TramStop]
    tram_line_variants: dict[int, list[int]]

    def __init__(self, cursor: Cursor):
        self.cursor = cursor

        self._set_tram_stops()
        self._set_tram_line_variants()

    def _set_tram_stops(self):
        self.cursor.execute("SELECT id, name, latitude, longitude FROM tram_stops")
        self.tram_stops = {item[0]: TramStop(*item) for item in self.cursor.fetchall()}

    def _set_tram_line_variants(self):
        self.cursor.execute("SELECT id, tram_line_id FROM tram_line_variants")

        self.tram_line_variants = defaultdict(list)
        for variant_id, tram_line_id in self.cursor.fetchall():
            self.tram_line_variants[tram_line_id].append(variant_id)

    def _get_departures(self, tram_line_variant: int, day: DayType):
        self.cursor.execute("""
            SELECT
                tram_stops.id,
                tram_departures.stop_index,
                tram_departures.hour,
                tram_departures.minute
            FROM tram_departures
                JOIN tram_line_variants ON tram_departures.tram_line_variant_id = tram_line_variants.id
                JOIN tram_stops ON tram_departures.tram_stop_id = tram_stops.id
            WHERE tram_line_variants.id = ? AND tram_departures.day = ?
            ORDER BY
                tram_departures.stop_index DESC,
                tram_departures.hour DESC,
                tram_departures.minute DESC
        """, (tram_line_variant, day.value))

        return [
            Departure(item[0], tram_line_variant, item[1], day, item[2], item[3])
            for item in self.cursor.fetchall()
        ]

    def _get_new_first_departure(self, end_departure: Departure):
        self.cursor.execute(
            """
                SELECT DISTINCT tram_stops.id
                FROM tram_departures
                    JOIN tram_line_variants ON tram_departures.tram_line_variant_id = tram_line_variants.id
                    JOIN tram_stops ON tram_departures.tram_stop_id = tram_stops.id
                WHERE tram_departures.day = ? AND tram_line_variants.id = ? AND tram_departures.stop_index = ?
            """,
            (
                end_departure.day_type.value,
                end_departure.variant_id,
                end_departure.stop_index + 1,
            )
        )

        new_stop_id = self.cursor.fetchone()[0]

        # We assume one minute time between stops for unknown travel time
        return Departure(
            new_stop_id,
            end_departure.variant_id,
            end_departure.stop_index + 1,
            end_departure.day_type,
            (end_departure.hour + (end_departure.minute + 1) // 60) % 24,
            (end_departure.minute + 1) % 60
        )

    def _store_passages(self, passages: list[TramPassage]):
        for passage in passages:
            self.cursor.execute("""
                INSERT INTO tram_passages (tram_line_id, day)
                VALUES (?, ?)
                RETURNING id
            """, (passage.line_id, passage.day.value))

            passage_id = self.cursor.fetchone()[0]
            self.cursor.executemany(
                """
                    INSERT INTO tram_passage_stops (tram_stop_id, tram_passage_id, stop_index, hour, minute)
                    VALUES (?, ?, ?, ?, ?)
                """,
                (
                    (item.stop_id, passage_id, stop_index + 1, item.hour, item.minute)
                    for stop_index, item in enumerate(reversed(passage.reverse_stop_sequence))
                )
            )

    def _get_variant_passages(self, tram_line_id: int, variant_id: int, day: DayType):
        def add_departure(departure: Departure):
            tram_passage.add_stop(departure)
            departure_passage[departure] = tram_passage

        departures = self._get_departures(variant_id, day)
        passages: list[TramPassage] = []
        departure_passage: dict[Departure, TramPassage] = {}

        highest_stop_index = max(map(lambda x: x.stop_index, departures))
        for end_departure in filter(lambda x: x not in departure_passage, departures):
            tram_passage = TramPassage(tram_line_id, day)
            passages.append(tram_passage)

            if end_departure.stop_index < highest_stop_index:
                new_first_departure = self._get_new_first_departure(end_departure)
                departures.append(new_first_departure)
                add_departure(new_first_departure)

            previous_stop = end_departure
            for item in filter(lambda x: x is end_departure or x.is_previous(previous_stop), departures):
                if item in departure_passage:
                    later_passage = departure_passage[item]
                    for _ in range(later_passage.get_departure_index(item), len(later_passage)):
                        del departure_passage[later_passage.reverse_stop_sequence.pop()]

                add_departure(item)
                previous_stop = item

        return passages

    def create_passages(self):
        for tram_line_id, tram_line_variants in self.tram_line_variants.items():
            for variant_id in tram_line_variants:
                for day in DayType:
                    print(tram_line_id, variant_id, day)
                    self._store_passages(self._get_variant_passages(tram_line_id, variant_id, day))
