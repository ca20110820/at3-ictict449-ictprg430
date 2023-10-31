""""Demonstrates a simple implementation of an 'event' listener that triggers
a publication via mqtt"""
import datetime
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
    def get_time_now(*args, **kwargs):
        """Utility Function to Get Datetime Now"""
        return datetime.datetime.now(*args, **kwargs)


class CarParkSensor(Sensor):
    # This class represent a sensor for the entrance (or exit) of the whole parking lot, not individual parking bays.
    # May be useful for keeping track of the number of cars (Parked/Un-parked) in the whole car park.
    # Not that there can be many entrance/exit points in a car park.
    @property
    def temperature(self):
        """Implement Getter for Temperature, this can be random number or pulled from API"""
        # TODO: Implement temperature
        return random.randint(20, 30)

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Implement with Event loop"""
        pass

    def on_car_entered(self):
        topic = self.create_topic_qualifier("entry")
        message = f"Enter,{self.get_time_now()},{self.temperature}"
        self.client.publish(topic, message)

    def on_car_exited(self):
        topic = self.create_topic_qualifier("exit")
        message = f"Exit,{self.get_time_now()},{self.temperature}"
        self.client.publish(topic, message)


class BaySensor(Sensor):
    # This will add 2 types of events: Parked vs Un-parked
    # Equivalently, on_occupied() vs on_available() [OR on_car_parked() vs on_car_unparked()]

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

    def on_car_parked(self, car: Car):
        """Publish to subscribers"""
        # "Parked,<temperature>,<time>;<car_details_in_json_str>" Separated by ;
        car.car_parked()  # Update parked status
        my_topic = self.create_topic_qualifier("na")  # Default topic-qualifier is 'na'
        my_message = f"Parked,{self.temperature},{self.get_time_now()};{car.to_json_format()}"
        if not self.IS_OCCUPIED:
            self.client.publish(my_topic, my_message)
            self.CAR = car
            self.IS_OCCUPIED = True
        else:
            print(f"Bay {self.name} is occupied!")

    def on_car_unparked(self):
        """Publish to subscribers"""
        self.CAR.is_parked = False
        my_topic = self.create_topic_qualifier("na")  # Default topic-qualifier is 'na'
        my_message = f"Unparked,{self.temperature},{self.get_time_now()};{self.CAR.to_json_format()}"
        if self.IS_OCCUPIED:
            self.client.publish(my_topic, my_message)
            self.CAR = None
            self.IS_OCCUPIED = False
        else:
            print(f"There are not car parked in Bay {self.name}!")


class CLISensor(BaySensor):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

    @property
    def temperature(self):
        """Implement Getter for Temperature, this can be random or pulled from API"""
        return random.randint(20, 30)

    def start_sensing(self, *args, **kwargs):
        """Must be implemented with infinite loop"""
        """ A blocking event loop that waits for detection events, in this
                        case Enter presses"""
        print("Press E when Car entered!")
        print("Press X when Car exited!\n")
        while True:
            detection = input("e or x> ")
            if detection == "e":
                self.on_car_parked()
            elif detection == "x":
                self.on_car_unparked()
            else:
                continue


class GUICarDetector(BaySensor):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.root = tk.Tk()
        self.root.title(f"Car Detector ULTRA | Bay: {self.name}")

        self.btn_incoming_car = tk.Button(
            self.root, text='🚘 Incoming Car', font=('Arial', 50), cursor='right_side', command=self.on_car_parked)
        self.btn_incoming_car.pack(padx=10, pady=5)
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car 🚘', font=('Arial', 50), cursor='bottom_left_corner',
            command=self.on_car_unparked)
        self.btn_outgoing_car.pack(padx=10, pady=5)

    @property
    def temperature(self):
        # TODO: Import a callable from temperature.py to get the temperature
        return random.randint(10, 30)

    def start_sensing(self):
        self.root.mainloop()

    def on_car_parked(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/entry
        # Message: "Entry,<license_plate>,<car_model>,<temperature>"  Need to be parsed in Subscribers
        if not self.IS_OCCUPIED:
            self.client.publish(self.create_topic_qualifier("entry"),
                                f"Entry,{datetime.datetime.now()},<license_plate>,<car_model>,{self.temperature}")
            self.IS_OCCUPIED = True
        else:
            print(f"There's already a car parked in {self.name}!")

    def on_car_unparked(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/exit
        # Message: "Entry,<temperature>"

        if self.IS_OCCUPIED:
            self.client.publish(self.create_topic_qualifier("exit"),
                                f"Exit,{self.temperature}")
            self.IS_OCCUPIED = False
        else:
            print(f"Cannot exit when there is no car in {self.name}!")


class SimulatedSensor(Sensor):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

    @property
    def temperature(self):
        """Implement Getter for Temperature, this can be random or pulled from API"""
        return random.randint(20, 30)

    def start_sensing(self, *args, **kwargs):
        while True:
            time_interval = 1  #
            time.sleep(time_interval)
            rnd = random.choice(["Entry", "Exit"])
            if rnd == "Entry":
                self.on_car_entry()
            elif rnd == "Exit":
                self.on_car_exit()
            else:
                continue

    def on_car_entry(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/entry
        # Message: "Entry,<license_plate>,<car_model>,<temperature>"  Need to be parsed in Subscribers
        if not self.IS_OCCUPIED:
            print("Car Entered")
            self.client.publish(self.create_topic_qualifier("entry"),
                                f"Entry,{datetime.datetime.now()},<license_plate>,<car_model>,{self.temperature}")
            self.IS_OCCUPIED = True
        else:
            print(f"There's already a car parked in {self.name}!")

    def on_car_exit(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/exit
        # Message: "Entry,<temperature>"
        if self.IS_OCCUPIED:
            print("Car Exited")
            self.client.publish(self.create_topic_qualifier("exit"),
                                f"Exit,{self.temperature}")
            self.IS_OCCUPIED = False
        else:
            print(f"Cannot exit when there is no car in {self.name}!")


if __name__ == '__main__':
    sensor_config = {"name": "bay_1",
                     "location": "L306",
                     "host": "localhost",
                     "port": 1883,
                     "topic-root": "Moondaloop Park",
                     "topic-qualifier": "na"
                     }
    # Topic: "Moondaloop Park/L306/bay_1/entry"

    # CLISensor(sensor_config).start_sensing()
    GUICarDetector(sensor_config).start_sensing()
    # SimulatedSensor(sensor_config).start_sensing()
