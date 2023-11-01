from smartpark.carpark import SimulatedManagementCenter, SimulatedCarPark

config = {"name": "CarPark",
          "location": "Moondaloop",
          "host": "localhost",
          "port": 1883,
          "topic-root": "Moondaloop Park",
          "topic-qualifier": "na"
          }

management_center = SimulatedManagementCenter()
management_center.add_parking_bay("bay_1")

car_park = SimulatedCarPark(config, management_center)
car_park.add_sensor_topic("Moondaloop Park/L306/bay_1/na")
car_park.add_carpark_sensor("Moondaloop Park/L306/MainEntrance/na")
car_park.start_serving()
