from smartpark.carpark import SimulatedCarPark


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

pubsub_config = {"name": "CarPark",
                 "location": "Moondaloop Park",
                 "host": "localhost",
                 "port": 1883,
                 "topic-root": "Moondaloop Park",
                 "topic-qualifier": "na"
                 }

# Sensor Topics
# "Moondaloop Park/L306/sensor1/entry"
# "Moondaloop Park/L306/sensor1/exit"

# Display Topic, see the CarPark.publish_to_display() method.
# Display objects must subscribe to this.
# "Moondaloop Park/Moondaloop Park/CarPark/display"

carpark = SimulatedCarPark(pubsub_config, 5)

# carpark.add_sensor_topic("Moondaloop Park/L306/sensor1/entry")
# carpark.add_sensor_topic("Moondaloop Park/L306/sensor2/exit")
topics = [("Moondaloop Park/L306/sensor1/entry", 0),
          ("Moondaloop Park/L306/sensor2/exit", 0)
          ]
carpark.add_sensor_topics(topics)

carpark.start_serving()
