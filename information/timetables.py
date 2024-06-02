import os
import sqlite3
import re

from contextlib import closing
from dotenv import load_dotenv
from time import sleep
from random import uniform
from mechanicalsoup import StatefulBrowser

from classes import DayType, Departure
from database import TimetableDatabaseSetup


class TimetableScraper:
    def __init__(self, connection_cursor: sqlite3.Cursor):
        self.cursor = connection_cursor

        self.browser = StatefulBrowser()
        self.departures: list[Departure] = []

    def _scrape_departures(self, variant_id: int, stop_index: int, stop_name: str, stop_url: str):
        self.cursor.execute("SELECT id FROM tram_stops WHERE name LIKE ?", [stop_name])
        rows, stop_id = self.cursor.fetchall(), None

        if len(rows):
            stop_id = rows[0][0]
        else:
            print(f"Stop '{stop_name}' not found")

        # For stops where line terminates, the timetable doesn't exist.
        # To combat this problem, we assume a 1-minute travel time between the second-last and last stop.
        # In order to achieve this, the departures list holds information about previous departures.
        if stop_url is not None:
            self.browser.open(os.environ.get("TIMETABLE_URL") + stop_url)

            self.departures = []
            for item in self.browser.page.findAll("table")[13].findAll("tr")[1:-2]:
                cells = item.findAll("td")
                hour = int(cells[0].text)

                for i, day in enumerate(DayType):
                    if i + 1 >= len(cells):
                        continue

                    for minute in cells[i + 1].text.strip().split():
                        self.departures.append(Departure(
                            stop_id, variant_id, stop_index, day, hour,
                            int(re.sub("[^0-9]", "", minute))
                        ))
        else:
            self.departures = [
                Departure(
                    stop_id, variant_id,
                    stop_index, item.day_type,
                    (item.hour + (item.minute + 1) // 60) % 24,
                    (item.minute + 1) % 60
                ) for item in self.departures
            ]

        self.cursor.executemany(
            """
                INSERT INTO tram_departures (tram_stop_id, tram_line_variant_id, stop_index, day, hour, minute)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                (item.stop_id, item.variant_id, item.stop_index, item.day_type.value, item.hour, item.minute)
                for item in self.departures
            )
        )

        sleep(uniform(1, 5))

    def _scrape_variant_stops(self, tram_line_id: int, variant_name: str, variant_url: str):
        print("Wariant", variant_name)

        self.cursor.execute(
            "INSERT INTO tram_line_variants (tram_line_id, name) VALUES (?, ?) RETURNING id",
            (tram_line_id, variant_name)
        )
        variant_id = self.cursor.fetchone()[0]

        self.browser.open(os.environ.get("TIMETABLE_URL") + variant_url)
        stop_urls = {
            item.text.strip(): item.find("a") and item.find("a").get("href")[1:]
            for item in self.browser.page.findAll("table")[10].findAll("td")
            if item.text.strip() and item.text.strip() != "NŻ"
        }

        for stop_index, (stop_name, stop_url) in enumerate(stop_urls.items()):
            self._scrape_departures(variant_id, stop_index + 1, stop_name, stop_url)

    def _scrape_line_variants(self, line_number: str, line_url: str):
        print("Linia", line_number)

        self.cursor.execute(
            "INSERT INTO tram_lines (number) VALUES (?) RETURNING id",
            tuple([line_number])
        )
        line_id = self.cursor.fetchone()[0]

        self.browser.open(os.environ.get("TIMETABLE_URL") + line_url)
        variant_urls = {
            item.text.strip(): item.get("href")[1:]
            for item in self.browser.page.findAll("table")[7].findAll("a")
        }

        # For the sake of simplicity, we assume the first two variants of
        # any line show the full information about all running trams,
        # which as of 05.05.2024 is true for all tram lines in Kraków.
        for variant_name, variant_url in list(variant_urls.items())[:2]:
            self._scrape_variant_stops(line_id, variant_name, variant_url)

    def scrape_timetables(self, included_lines: set[str], excluded_lines: set[str]):
        self.browser.open(os.environ.get('TIMETABLE_URL'))

        tram_lines = {
            item.text.strip(): item.get("href")[1:]
            for item in self.browser.page.findAll("a", class_=lambda x: x and x.startswith("linia"))
            if len(item.text.strip()) <= 2
        }

        for line_number, line_url in filter(
            lambda x: x[0] in included_lines if included_lines else x[0] not in excluded_lines,
            tram_lines.items()
        ):
            self._scrape_line_variants(line_number, line_url)


def main():
    load_dotenv()

    with (
        closing(sqlite3.connect(os.environ.get('DATABASE_NAME'), isolation_level=None)) as connection,
        closing(connection.cursor()) as cursor
    ):
        TimetableDatabaseSetup(cursor).prepare_database()

        included_lines = set(os.environ.get("INCLUDED_LINES").split(","))
        if len(included_lines) == 1 and "" in included_lines:
            included_lines.clear()

        excluded_lines = set(os.environ.get("EXCLUDED_LINES").split(","))
        if len(excluded_lines) == 1 and "" in excluded_lines:
            excluded_lines.clear()

        TimetableScraper(cursor).scrape_timetables(included_lines, excluded_lines)


if __name__ == "__main__":
    main()
