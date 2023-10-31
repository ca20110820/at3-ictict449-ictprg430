""""Demonstrates a simple implementation of an 'event' listener that triggers
a publication via mqtt"""
import datetime
import paho.mqtt.client as paho
from abc import ABC, abstractmethod
import time
import random
import tkinter as tk

from smartpark.mqtt_device import MqttDevice
from smartpark.car import Car, generate_random_license_plate, generate_random_car_model


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
        return random.randint(20, 30)

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

        if not self.IS_OCCUPIED and self.CAR is None:
            car = car if isinstance(car, Car) else Car.from_json(car)
            car.car_parked()  # Update parked status
            my_topic = self.create_topic_qualifier("na")  # Default topic-qualifier is 'na'
            my_message = f"Parked,{self.temperature},{self.get_time_now_as_str()};{car.to_json_format()}"
            self.client.user_data_set(self.CAR)
            self.client.publish(my_topic, my_message)
            self.CAR = car
            self.IS_OCCUPIED = True
        else:
            print(f"Bay {self.name} is occupied!")

    def on_car_unparked(self):
        """Publish to subscribers"""
        if self.IS_OCCUPIED and isinstance(self.CAR, Car):
            self.CAR.car_unparked()
            my_topic = self.create_topic_qualifier("na")  # Default topic-qualifier is 'na'
            my_message = f"Unparked,{self.temperature},{self.get_time_now_as_str()};{self.CAR.to_json_format()}"
            self.client.user_data_set(self.CAR)
            self.client.publish(my_topic, my_message)
            print(self.CAR.to_json_format(indent=4))
            self.CAR = None
            self.IS_OCCUPIED = False
        else:
            print(f"There are no car parked in Bay {self.name}!")


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
                license_plate = generate_random_license_plate()
                car_model = generate_random_car_model(["ModelA", "ModelB", "ModelC"])
                new_car = Car(license_plate, car_model)
                new_car.car_entered(self.temperature)
                self.on_car_parked(new_car)
                self.CAR.bay = self.name  # Attach the bay name/number/id to the Car as property
                print(self.CAR.to_json_format(indent=4))
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
    # Topic: "Moondaloop Park/L306/bay_1/na"

    CLISensor(sensor_config).start_sensing()
    # GUICarDetector(sensor_config).start_sensing()
    # SimulatedSensor(sensor_config).start_sensing()
