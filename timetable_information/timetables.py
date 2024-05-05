import os
import sqlite3
from contextlib import closing

from dotenv import load_dotenv

from classes import TimetableDatabaseSetup, TimetableScraper

if __name__ == "__main__":
    load_dotenv()

    with (
        closing(sqlite3.connect(os.environ.get('DATABASE_NAME'), isolation_level=None)) as connection,
        closing(connection.cursor()) as cursor
    ):
        TimetableDatabaseSetup(cursor).prepare_database()

        scraper = TimetableScraper(cursor)
        scraper.scrape_timetables(
            set(os.environ.get("INCLUDED_LINES").split(",")),
            set(os.environ.get("EXCLUDED_LINES").split(","))
        )
