import os
import sqlite3
from contextlib import closing
from dotenv import load_dotenv

from database import RoutesDatabaseSetup


def main():
    load_dotenv()

    with (
        closing(sqlite3.connect(os.environ.get('DATABASE_NAME'), isolation_level=None)) as connection,
        closing(connection.cursor()) as cursor
    ):
        RoutesDatabaseSetup(cursor).prepare_database()


if __name__ == "__main__":
    main()
