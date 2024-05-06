import os
import sqlite3
from contextlib import closing

from dotenv import load_dotenv

from timetable_information.classes import PassageDatabaseSetup, PassageCreator

if __name__ == "__main__":
    load_dotenv()

    with (
        closing(sqlite3.connect(os.environ.get('DATABASE_NAME'), isolation_level=None)) as connection,
        closing(connection.cursor()) as cursor
    ):
        PassageDatabaseSetup(cursor).prepare_database()

        passage_creator = PassageCreator(cursor)
        passage_creator.create_passages()
