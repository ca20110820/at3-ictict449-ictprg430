from smartpark.sensor import CLIBaySensorSensor

config = {"name": "bay_1",
          "location": "L306",
          "host": "localhost",
          "port": 1883,
          "topic-root": "Moondaloop Park",
          "topic-qualifier": "na"
          }

# "Moondaloop Park/L306/bay_1/na"

carpark_sub_topic = "Moondaloop Park/Moondaloop/CarPark/parked"

CLIBaySensorSensor(config, carpark_sub_topic).start_sensing()
