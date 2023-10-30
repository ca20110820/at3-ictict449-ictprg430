""""Demonstrates a simple implementation of an 'event' listener that triggers
a publication via mqtt"""
import datetime
import paho.mqtt.client as paho
from abc import ABC, abstractmethod
import time
import random
import tkinter as tk

from smartpark.mqtt_device import MqttDevice


class Sensor(MqttDevice):
    # Users are must implement the logic for car entry and/or exit event-handlers. No need for
    # strict enforcement.

    IS_OCCUPIED = False  # Optional Flag if a Parking Bay is Occupied or Available

    @abstractmethod
    def temperature(self):
        """Implement Getter for Temperature, this can be random number or pulled from API"""
        pass

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Implement with Event loop"""
        pass


class CLISensor(Sensor):
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
                if not self.IS_OCCUPIED:
                    print("Car Entered")
                    self.on_car_entry()
                else:
                    print(f"There's already a car parked in {self.name}!")
            elif detection == "x":
                if self.IS_OCCUPIED:
                    print("Car Exited")
                    self.on_car_exit()
                else:
                    print(f"Cannot exit when there is no car in {self.name}!")
            else:
                continue

    def on_car_entry(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/entry
        # Message: "Entry,<license_plate>,<car_model>,<temperature>"  Need to be parsed in Subscribers
        self.client.publish(self.create_topic_qualifier("entry"),
                            f"Entry,{datetime.datetime.now()},<license_plate>,<car_model>,{self.temperature}")
        self.IS_OCCUPIED = True

    def on_car_exit(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/exit
        # Message: "Entry,<temperature>"
        self.client.publish(self.create_topic_qualifier("exit"),
                            f"Exit,{self.temperature}")
        self.IS_OCCUPIED = False


class GUICarDetector(Sensor):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.root = tk.Tk()
        self.root.title(f"Car Detector ULTRA | Bay: {self.name}")

        self.btn_incoming_car = tk.Button(
            self.root, text='🚘 Incoming Car', font=('Arial', 50), cursor='right_side', command=self.on_car_entry)
        self.btn_incoming_car.pack(padx=10, pady=5)
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car 🚘', font=('Arial', 50), cursor='bottom_left_corner',
            command=self.on_car_exit)
        self.btn_outgoing_car.pack(padx=10, pady=5)

    @property
    def temperature(self):
        # TODO: Import a callable from temperature.py to get the temperature
        return random.randint(10, 30)

    def start_sensing(self):
        self.root.mainloop()

    def on_car_entry(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/entry
        # Message: "Entry,<license_plate>,<car_model>,<temperature>"  Need to be parsed in Subscribers
        if not self.IS_OCCUPIED:
            self.client.publish(self.create_topic_qualifier("entry"),
                                f"Entry,{datetime.datetime.now()},<license_plate>,<car_model>,{self.temperature}")
            self.IS_OCCUPIED = True
        else:
            print(f"There's already a car parked in {self.name}!")

    def on_car_exit(self):
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
