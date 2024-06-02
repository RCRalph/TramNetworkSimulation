import os
import sqlite3
from contextlib import closing

from dotenv import load_dotenv

from classes import TimetableScraper
from database import TimetableDatabaseSetup

if __name__ == "__main__":
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

        scraper = TimetableScraper(cursor)
        scraper.scrape_timetables(included_lines, excluded_lines)
