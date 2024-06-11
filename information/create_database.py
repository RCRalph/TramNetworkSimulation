import information


def main():
    print("Inserting stops...")
    information.stops()

    print("Inserting timetables...")
    information.timetables()

    print("Inserting passages...")
    information.passages()

    print("Inserting routes...")
    information.routes()


if __name__ == '__main__':
    main()
