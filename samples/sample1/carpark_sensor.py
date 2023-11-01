from smartpark.sensor import CLICarParkSensor


config = {"name": "MainEntrance",
          "location": "L306",
          "host": "localhost",
          "port": 1883,
          "topic-root": "Moondaloop Park",
          "topic-qualifier": "na"
          }

CLICarParkSensor(config).start_sensing()
