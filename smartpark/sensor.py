""""Demonstrates a simple implementation of an 'event' listener that triggers
a publication via mqtt"""
import datetime
import threading

import paho.mqtt.client as paho
from abc import ABC, abstractmethod
import time
import random
import tkinter as tk

from smartpark.mqtt_device import MqttDevice
from smartpark.car import Car


class Sensor(MqttDevice):
    # Users are must implement the logic for car entry and/or exit event-handlers. No need for
    # strict enforcement.

    @abstractmethod
    def temperature(self):
        """Implement Getter for Temperature, this can be random number or pulled from API"""
        pass

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Implement with Event loop"""
        pass

    @staticmethod
    def get_time_now(*args, **kwargs) -> datetime:
        """Utility Function to Get Datetime Now"""
        return datetime.datetime.now(*args, **kwargs)

    @staticmethod
    def get_time_now_as_str(*args, **kwargs) -> str:
        """Utility Function to Get Datetime Now"""
        return datetime.datetime.now(*args, **kwargs).strftime('%Y-%m-%d %H:%M:%S')


class CarParkSensor(Sensor):
    # This class represent a sensor for the entrance (or exit) of the whole parking lot, not individual parking bays.
    # May be useful for keeping track of the number of cars (Parked/Un-parked) in the whole car park.
    # Not that there can be many entrance/exit points in a car park.
    # A Car instance may be constructed in this class and can be sent and reconstructed over a network from subscribers.

    @property
    def temperature(self):
        """Implement Getter for Temperature, this can be random number or pulled from API"""
        # TODO: Implement temperature
        raise NotImplementedError()

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Implement with Event loop"""
        pass

    def on_car_entered(self):
        topic = self.create_topic_qualifier("na")
        message = f"Enter,{self.temperature},{self.get_time_now_as_str()}"
        self.client.publish(topic, message)

    def on_car_exited(self):
        topic = self.create_topic_qualifier("na")
        message = f"Exit,{self.temperature},{self.get_time_now_as_str()}"
        self.client.publish(topic, message)


class BaySensor(Sensor):
    # This will add 2 types of events: Parked vs Un-parked
    # Equivalently, on_occupied() vs on_available() [OR on_car_parked() vs on_car_unparked()]
    # Users may have to implement BaySensor as a Subscriber for when a Car decided to park in an available bay.

    IS_OCCUPIED: bool = False  # Optional Flag if a Parking Bay is Occupied or Available
    CAR: Car | None = None

    @property
    def temperature(self):
        """Implement Getter for Temperature, this can be random number or pulled from API"""
        raise NotImplementedError()

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Implement with Event loop"""
        # self.on_car_parked(<license_plate>, <car_model>)
        pass

    def on_car_parked(self, car: Car | str):
        """Publish to subscribers"""
        # "Parked,<temperature>,<time>;<car_details_in_json_str>" Separated by ;

        car = car if isinstance(car, Car) else Car.from_json(car)

        if not self.IS_OCCUPIED and self.CAR is None:
            car.car_parked()  # Update parked status
            # my_topic = self.create_topic_qualifier("na")  # Default topic-qualifier is 'na'
            # my_message = f"Parked,{self.name},{self.temperature},{self.get_time_now_as_str()};{car.to_json_format()}"
            # self.client.user_data_set(self.CAR)
            # self.client.publish(my_topic, my_message)
            self.CAR = car
            self.IS_OCCUPIED = True
        else:
            # Failed to Park the Car
            self.client.publish(self.create_topic_qualifier("error"), f"{self.name};{car.to_json_format()}")
            print(f"Bay {self.name} is occupied!")

    def on_car_unparked(self):
        """Publish to subscribers"""
        if self.IS_OCCUPIED and isinstance(self.CAR, Car):
            self.CAR.car_unparked()
            my_topic = self.create_topic_qualifier("na")  # Default topic-qualifier is 'na'
            my_message = \
                f"Unparked,{self.name},{self.temperature},{self.get_time_now_as_str()};{self.CAR.to_json_format()}"
            self.client.user_data_set(self.CAR)
            self.client.publish(my_topic, my_message)
            print(self.CAR.to_json_format(indent=4))
            self.CAR = None
            self.IS_OCCUPIED = False
        else:
            self.client.publish(self.create_topic_qualifier("error"), f"IS_OCCUPIED={self.IS_OCCUPIED}")
            print(f"There are no car parked in Bay {self.name}!")


class CLICarParkSensor(CarParkSensor):

    QUIT_FLAG = False

    @property
    def temperature(self):
        return random.randint(20, 30)

    def start_sensing(self, *args, **kwargs):
        """Implement with Event loop"""
        while not self.QUIT_FLAG:
            enter_or_exit = input("E or X> ")
            if enter_or_exit in ["e", "E", "enter"]:
                self.on_car_entered()
            elif enter_or_exit in ["x", "X", "exit"]:
                self.on_car_exited()
            elif enter_or_exit in ["q", "Q", "quit"]:
                print("Good Bye!")
                self.client.publish(self.create_topic_qualifier("quit"))
                self.QUIT_FLAG = True
            else:
                print(f"Could not parse '{enter_or_exit}'! Please try again!\n")
                continue

    def on_car_entered(self):
        new_car: Car = Car.generate_random_car(["ModelA", "ModelB", "ModelC"])
        new_car.car_entered(self.temperature)
        my_topic = self.create_topic_qualifier("na")
        print(my_topic)
        my_message = f"Enter,{self.temperature},{self.get_time_now_as_str()};{new_car.to_json_format()}"
        self.client.publish(my_topic, my_message)

    def on_car_exited(self):
        my_topic = self.create_topic_qualifier("na")
        print(my_topic)
        my_message = f"Exit,{self.temperature},{self.get_time_now_as_str()}"
        self.client.publish(my_topic, my_message)


class CLIBaySensorSensor(BaySensor):

    QUIT_FLAG = False

    def __init__(self, config, carpark_sub_topic, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self.carpark_sub_topic = carpark_sub_topic
        self.client.subscribe(self.carpark_sub_topic)
        self.client.on_message = self.on_message

        thread = threading.Thread(name=self.name, target=self.client.loop_forever)
        thread.daemon = True

        thread.start()
        self.start_sensing()

    @property
    def temperature(self):
        """Implement Getter for Temperature, this can be random or pulled from API"""
        return random.randint(20, 30)

    def start_sensing(self, *args, **kwargs):
        """Listen to (User) Unparked Event"""
        while not self.QUIT_FLAG:
            print("=" * 100)
            user_input = input("Press U to Unpark> ")
            if user_input in ["U", "u", "unpark", "unparked"]:
                self.on_car_unparked()
            elif user_input in ["q", "Q", "quit"]:
                self.QUIT_FLAG = True
            else:
                print("\n")
                continue

    def on_message(self, client: paho.Client, userdata, message: paho.MQTTMessage):
        """Listening to Parked event"""
        print("=" * 100)
        payload = message.payload.decode()
        print(f"[{self.name}] Received Topic: \n{message.topic}")
        print(f"[{self.name}] Received Message: \n{payload}")
        print(f"[{self.name}] Received Data: \n{userdata}")

        # Topic: <root>/<location>/<carpark_name>/parked
        # Message: "<bay>;<car_json_str>"

        msg = payload.split(";")
        car_json_str = msg[1]

        if msg[0] == self.name:
            # self.on_car_parked(<car>|<car_json_str>)
            car = Car.from_json(car_json_str)
            self.on_car_parked(car)
        else:
            pass


if __name__ == '__main__':
    bay_sensor_config = {"name": "bay_1",
                         "location": "L306",
                         "host": "localhost",
                         "port": 1883,
                         "topic-root": "Moondaloop Park",
                         "topic-qualifier": "na"
                         }

    carpark_sensor_config = {"name": "MainEntrance",
                             "location": "L306",
                             "host": "localhost",
                             "port": 1883,
                             "topic-root": "Moondaloop Park",
                             "topic-qualifier": "na"
                             }
    # Topic: "Moondaloop Park/L306/bay_1/na"

    CLICarParkSensor(carpark_sensor_config).start_sensing()
    # CLISensor(sensor_config).start_sensing()
    # GUICarDetector(sensor_config).start_sensing()
    # SimulatedSensor(sensor_config).start_sensing()
