from zone1tube.data.stations import Stations


def main():
    with open("./data.json", "r") as f:
        stations = Stations.validate_json(f.read())
        print(len(stations))


if __name__ == "__main__":
    main()
