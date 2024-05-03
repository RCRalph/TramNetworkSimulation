#!/bin/python3

import os
import sqlite3
from collections import defaultdict
from contextlib import closing
from random import uniform
from sqlite3 import Cursor
from time import sleep

from dotenv import load_dotenv
from mechanicalsoup import StatefulBrowser


class TimetableScraper:
    day_types = ("P", "S", "N")

    def __init__(self, connection_cursor: Cursor):
        self.cursor = connection_cursor
        self.browser = StatefulBrowser()
        self.day_departures: defaultdict[str, list[tuple[int, int]]] = defaultdict(list)

    def _drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS tram_departures")
        self.cursor.execute("DROP TABLE IF EXISTS tram_line_variants")
        self.cursor.execute("DROP TABLE IF EXISTS tram_lines")

    def _create_tram_lines_table(self):
        self.cursor.execute("""
            CREATE TABLE tram_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE ON CONFLICT REPLACE
            )
        """)

    def _create_tram_line_variants_table(self):
        self.cursor.execute("""
            CREATE TABLE tram_line_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tram_line_id INTEGER,
                name TEXT NOT NULL,

                FOREIGN KEY (tram_line_id) REFERENCES tram_lines (id),
                UNIQUE (tram_line_id, name) ON CONFLICT REPLACE
            )
        """)

    def _create_tram_departures_table(self):
        self.cursor.execute(f"""
            CREATE TABLE tram_departures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tram_stop_id INTEGER DEFAULT NULL,
                tram_line_variant_id INTEGER NOT NULL,
                stop_index INTEGER NOT NULL,
                day TEXT NOT NULL CHECK (day IN {scraper.day_types}),
                hour INTEGER NOT NULL,
                minute INTEGER NOT NULL,

                FOREIGN KEY (tram_stop_id) REFERENCES tram_stops (id),
                FOREIGN KEY (tram_line_variant_id) REFERENCES tram_line_variants (id)
            )
        """)

    def prepare_database(self):
        if os.environ.get("REFRESH_DATABASE").lower() == "yes":
            self._drop_tables()

        self._create_tram_lines_table()
        self._create_tram_line_variants_table()
        self._create_tram_departures_table()

    def _scrape_stops(self, variant_id: int, stop_index: int, stop_name: str, stop_url: str):
        cursor.execute("SELECT id FROM tram_stops WHERE name LIKE ?", list([stop_name]))
        rows, stop_id = cursor.fetchall(), None

        if not len(rows):
            print(f"Stop '{stop_name}' not found")
        else:
            stop_id = rows[0][0]

        # For stops where line terminates, we assume a 1-minute travel time between the second-last and last stop
        if stop_url is not None:
            self.browser.open(os.environ.get("TIMETABLE_URL") + stop_url)
            self.day_departures.clear()

            for item in self.browser.page.findAll("table")[13].findAll("tr")[1:-2]:
                cells = item.findAll("td")
                hour = int(cells[0].text)

                for i, day in enumerate(self.day_types):
                    for minute in cells[i + 1].text.strip().split():
                        self.day_departures[day].append((hour, int(minute)))

        for day, departures in self.day_departures.items():
            cursor.executemany(
                """
                    INSERT INTO tram_departures (tram_stop_id, tram_line_variant_id, stop_index, day, hour, minute)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                [(
                    stop_id,
                    variant_id,
                    stop_index,
                    day,
                    hour if stop_url is not None else (hour + (minute // 60)) % 24,
                    minute if stop_url is not None else (minute + 1) % 60
                ) for (hour, minute) in departures]
            )

        sleep(uniform(1, 5))

    def _scrape_variant_stops(self, tram_line_id: int, variant_name: str, variant_url: str):
        print("Wariant", variant_name)

        cursor.execute(
            "INSERT INTO tram_line_variants (tram_line_id, name) VALUES (?, ?) RETURNING id",
            (tram_line_id, variant_name)
        )
        variant_id = cursor.fetchone()[0]

        self.browser.open(os.environ.get("TIMETABLE_URL") + variant_url)
        stop_urls = {
            item.text.strip(): item.find("a") and item.find("a").get("href")[1:]
            for item in self.browser.page.findAll("table")[10].findAll("td")
            if item.text.strip()
        }

        for stop_index, (stop_name, stop_url) in enumerate(stop_urls.items()):
            self._scrape_stops(variant_id, stop_index + 1, stop_name, stop_url)

    def _scrape_line_variants(self, line_number: str, line_url: str):
        print("Linia", line_number)

        cursor.execute(
            "INSERT INTO tram_lines (number) VALUES (?) RETURNING id",
            tuple([line_number])
        )
        tram_line_id = cursor.fetchone()[0]

        self.browser.open(os.environ.get("TIMETABLE_URL") + line_url)
        variant_urls = {
            item.text.strip(): item.get("href")[1:]
            for item in self.browser.page.findAll("table")[7].findAll("a")
        }

        for variant_name, variant_url in variant_urls.items():
            self._scrape_variant_stops(tram_line_id, variant_name, variant_url)

    def scrape_timetables(self):
        self.browser.open(os.environ.get('TIMETABLE_URL'))

        tram_lines = {
            item.text.strip(): item.get("href")[1:]
            for item in self.browser.page.findAll("a", class_=lambda x: x and x.startswith("linia"))
            if len(item.text.strip()) <= 2
        }

        for line_number, line_url in tram_lines.items():
            self._scrape_line_variants(line_number, line_url)


if __name__ == "__main__":
    load_dotenv()

    with (closing(sqlite3.connect(os.environ.get('DATABASE_NAME'), isolation_level=None)) as connection,
          closing(connection.cursor()) as cursor):
        scraper = TimetableScraper(cursor)

        scraper.prepare_database()
        scraper.scrape_timetables()
