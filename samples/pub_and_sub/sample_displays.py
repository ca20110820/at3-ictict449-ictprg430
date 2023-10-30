import concurrent.futures
from smartpark.display import TkGUIDisplay, ConsoleDisplay

pub_display_config = {"name": "CarPark",
                      "location": "Moondaloop Park",
                      "host": "localhost",
                      "port": 1883,
                      "topic-root": "Moondaloop Park",
                      "topic-qualifier": "display"
                      }

# Display Topic from CarPark: "Moondaloop Park/Moondaloop Park/CarPark/display"

# TkGUIDisplay(pub_display_config, "Moondaloop Park/Moondaloop Park/CarPark/display")
# ConsoleDisplay(pub_display_config, "Moondaloop Park/Moondaloop Park/CarPark/display")


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(TkGUIDisplay, pub_display_config, "Moondaloop Park/Moondaloop Park/CarPark/display")
        executor.submit(ConsoleDisplay, pub_display_config, "Moondaloop Park/Moondaloop Park/CarPark/display")
