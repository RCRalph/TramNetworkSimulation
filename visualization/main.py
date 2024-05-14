import sys

from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QApplication

from layout import MainWindow


def main():
    app = QApplication(sys.argv)

    connection = QSqlDatabase.addDatabase("QSQLITE")
    connection.setDatabaseName("../db.sqlite")

    if not connection.open():
        raise IOError("Could not open database")

    window = MainWindow()
    window.show()

    app.exec()
    connection.close()


if __name__ == "__main__":
    main()
