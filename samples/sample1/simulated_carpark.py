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

SimulatedCarPark(config, management_center)
