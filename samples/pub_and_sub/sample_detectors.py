from smartpark.sensor import CLIDetector, RandomDetector, GUICarDetector, FileDataDetector

entry_config = {"name": "sensor1",
                "location": "L306",
                "host": "localhost",
                "port": 1883,
                "topic-root": "Moondaloop Park",
                "topic-qualifier": "entry"
                }

exit_config = {"name": "sensor2",
               "location": "L306",
               "host": "localhost",
               "port": 1883,
               "topic-root": "Moondaloop Park",
               "topic-qualifier": "exit"
               }

# Sensor Topics
# "Moondaloop Park/L306/sensor1/entry"
# "Moondaloop Park/L306/sensor2/exit"

# CLIDetector(entry_config, exit_config).start_sensing()
# RandomDetector(entry_config, exit_config).start_sensing()
GUICarDetector(entry_config, exit_config).start_sensing()
# FileDataDetector(entry_config, exit_config, './samples/pub_and_sub/mock_car_event_temperature.txt').start_sensing()
