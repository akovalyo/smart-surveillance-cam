from smartCam import surveillance
import json


def main():
    config = None

    # Try to load configuration file, if the file doesn't exist ask user
    try:
        with open("configuration.json") as f:
            config = json.load(f)
    except:
        pass

    if config is None:
        while True:
            config_path = input(
                "Enter the path to the configuration file or 'q' to exit:\n")
            if config_path == "q":
                break
            try:
                with open(config_path) as f:
                    config = json.load(f)
                break
            except:
                print("File doesn't exist")

    if config:
        surveillance(config)


if __name__ == "__main__":
    main()
