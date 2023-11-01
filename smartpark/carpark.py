import random
import time
import threading
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Hashable, Callable, Optional, Any, Tuple

import json

import paho.mqtt.client as paho
from paho.mqtt.client import MQTTMessage

from smartpark.mqtt_device import MqttDevice
from smartpark.car import Car


class ManagementCenter:
    def __init__(self):

        self.num_parking_bays = 0
        self.parking_bays: Dict[Hashable, Car | None] = {}
        self.cars: List[Car] = []  # List of all the Cars in the Car Park (Both Parked & Not Parked)

        self._entry_exit_time: datetime | None = None

    @classmethod
    def from_int_bays_and_num_parking_pays(cls, num_parking_bays, enter_car: Callable,
                                           exit_car: Callable):
        instance = cls()
        instance.num_parking_bays = num_parking_bays
        instance.parking_bays = {i: None for i in range(1, num_parking_bays + 1)}

        instance.enter_car = enter_car
        instance.exit_car = exit_car

        return instance

    def add_parking_bay(self, bay_name: Hashable):
        self.parking_bays[bay_name] = None
        self.num_parking_bays += 1

    def add_parking_bays(self, *bays):
        for bay in bays:
            self.add_parking_bay(bay)

    @property
    def entry_exit_time(self):
        return self._entry_exit_time

    @entry_exit_time.setter
    def entry_exit_time(self, value):
        self._entry_exit_time = value

    @property
    def num_cars_in_park(self):
        return len(self.cars)

    @property
    def num_available_parking_bays(self):
        return len(self.available_parking_bays)

    @property
    def available_parking_bays(self) -> List[Hashable]:
        return [bay for bay, car in self.parking_bays.items() if car is None]

    @property
    def unavailable_parking_bays(self) -> List[Hashable]:
        return [bay for bay, car in self.parking_bays.items() if car is not None]

    @property
    def parked_cars(self) -> List[Car]:
        # Alternative: [car for car in self.cars if car.is_parked == True]
        # return [car for bay_num, car in self.parking_bays.items() if car is not None]
        return [car for car in self.cars if car.is_parked]

    @property
    def unparked_cars(self) -> List[Car]:
        # Alternative: [car for car in self.cars if car.is_parked == False]
        # return [car for car in self.cars if car not in self.parking_bays.items()]
        return [car for car in self.cars if not car.is_parked]

    @property
    def parking_bays_status(self):
        """Gets the Occupancy Status of each Parking Bay: 'Available' or 'Occupied'"""
        return {bay: "Occupied" if isinstance(car, Car) else "Available" for bay, car in
                self.parking_bays.items()}

    @property
    def cars_status(self):
        """Gets the Parking Status of each Car in the Car Park: 'Parked' or 'Unparked'"""
        return {car.license_plate: "Parked" if car.is_parked else "Unparked" for car in self.cars}

    def get_carpark_details(self):
        parking_bays_and_parked_cars = {bay: car.license_plate if isinstance(car, Car) else "" for bay, car in
                                        self.parking_bays.items()}

        carpark_details = \
            {
                "entry_exit_time": self.entry_exit_time,
                "num_available_parking_bays": self.num_available_parking_bays,
                "num_cars_in_park": self.num_cars_in_park,
                "num_parked_cars": len(self.parked_cars),
                "num_unparked_cars": len(self.unparked_cars),
                "parking_bays_status": self.parking_bays_status,
                "cars_status": self.cars_status,
                "parking_bays_and_parked_cars": parking_bays_and_parked_cars
            }

        # TODO: Build Parser for processing get_carpark_details()
        return json.dumps(carpark_details, indent=4, sort_keys=False, default=str)

    def add_capacity(self, num_lots):
        # TODO: Feature - Check about available bays
        assert isinstance(num_lots, int) and num_lots > 0
        self.num_parking_bays += num_lots

    def remove_capacity(self, num_lots):
        # TODO: Feature - Check about available bays
        if self.num_parking_bays - num_lots < 0:
            self.num_parking_bays = 0
        else:
            self.num_parking_bays -= self.num_parking_bays

    @abstractmethod
    def enter_car(self, car: Car):
        """
        User must:
        ----------
        - Update self.cars
        - Update self.parking_bays
        - Update self.entry_exit_time = <entering_car>.entry_time
        - Set <entering_car>.is_parking = True

        :param car: Car
            Entering Car. This must be instantiated outside of ManagementCenter instance.
        """
        pass

    @abstractmethod
    def exit_car(self, temperature):
        """
        User must:
        ----------
        - Update self.cars
        - Update self.parking_bays
        - Call car.car_exit(temperature) to modify the states of the exiting car instance with the temperature argument
        - Pass the car's exit_time to the self.entry_exit_time for updating and, optionally, logging purpose
            - self.entry_exit_time = <exiting_car>.exit_time

        :param temperature: int | float
            Temperature received from the Detectors, which is to be passed onto <exiting_car> for recording purpose.
        """
        pass

    def remove_car(self, car: Car):
        self.cars = [c for c in self.cars if car.license_plate != c.license_plate]

    def remove_car_by_license(self, license_plate: str):
        self.cars = [car for car in self.cars if car.license_plate != license_plate]


class SimulatedManagementCenter(ManagementCenter):
    def enter_car(self, car: Car):
        assert not car.is_parked, f"Car {car} is already parked!"
        self.cars.append(car)
        self.entry_exit_time = car.entry_time
        # TODO: Logging, Data Collection, Publishing to Displays

    def exit_car(self, temperature) -> Car | None:
        # Select Random Unparked Car to exit (parked cars must unparked before exiting them)
        car: Car | None = random.choice(self.unparked_cars) if len(self.unparked_cars) != 0 else None
        if car is None:
            return None

        assert not car.is_parked, f"The selected car {car} to exit is currently parked!"
        # assert len([bay for bay, c in self.parking_bays.items() if c.license_plate == car.license_plate]) == 0

        self.remove_car_by_license(car.license_plate)

        car.car_exited(temperature)
        self.entry_exit_time = car.exit_time

        # TODO: Logging, Data Collection, Publishing to Displays

        return car

    def car_parked(self) -> Tuple[Hashable, Car] | None:
        # Select Random Unparked Car to Park., if applicable
        # Selected Random Available Bay for the Car to be Parked, if applicable.

        car: Car | None = random.choice(self.unparked_cars) if len(self.unparked_cars) != 0 else None
        bay: Hashable | None = random.choice(self.available_parking_bays) if len(
            self.available_parking_bays) != 0 else None

        if car is not None and bay is not None:  # Matched
            car.car_parked()
            self.parking_bays[bay] = car
            return bay, car

        return None

    def car_unparked(self, bay: Hashable, car: Car) -> Car | None:
        # UI from BaySensor would decide which parked car to unpark
        if bay not in self.parking_bays.keys():
            print(f"Bay {bay} does not exist!")
            return None
        if car.license_plate not in [c.license_plate for b, c in self.parking_bays.items() if isinstance(c, Car)]:
            print(f"Car {car} does not exist in the parking bays!")
            return None
        if self.parking_bays[bay] is None:
            print(f"There are no Car to parked in Bay {bay}")
            return None
        if self.parking_bays[bay].license_plate != car.license_plate:
            print(f"The Parked Car {self.parking_bays[bay]} does not match {car}!")
            return None

        # self.parking_bays[bay] = None
        # car.car_unparked()
        car_unparked = self.parking_bays.pop(bay)
        car_unparked.car_unparked()
        return car_unparked


class CarPark(MqttDevice):
    def __init__(self, config, management_center: ManagementCenter, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.management_center = management_center
        self._temperature: int | float | None = None

        self.sensor_topics: List[str] = []  # For Bay Sensors
        self.carpark_sensors: List[
            str] = []  # For Car Park Sensors. We may have at least 1 entrance (or exit for the whole car park)
        self.display_topic = self.create_topic_qualifier("display")  # Default publication topic to Displays

        self.client.on_message = self.on_message

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    def publish_to_display(self, message: str):
        self.client.publish(self.display_topic, message)

    def add_topic_and_callback(self, topic: str, callback: Callable):
        self.client.message_callback_add(topic, callback)

    def add_sensor_topic(self, sensor_topic: str):
        self.sensor_topics.append(sensor_topic)
        self.client.subscribe(sensor_topic)

    def add_sensor_topics(self, sensor_topics: List[Tuple[str, int]]):
        for topic, _ in sensor_topics:
            self.sensor_topics.append(topic)
        self.client.subscribe(sensor_topics)

    def add_carpark_sensor(self, carpark_sensor_topic: str):
        self.carpark_sensors.append(carpark_sensor_topic)
        self.client.subscribe(carpark_sensor_topic)

    def add_carpark_sensors(self, carpark_sensor_topics: List[Tuple[str, int]]):
        for topic, _ in carpark_sensor_topics:
            self.carpark_sensors.append(topic)
        self.client.subscribe(carpark_sensor_topics)

    @abstractmethod
    def start_serving(self):
        """Start listening to Sensors"""
        # self.pubsub.client.loop_forever()  # Start a Blocking Thread
        # self.pubsub.client.loop_start()  # Daemon thread, need to be closed with .loop_stop()
        # self.pubsub.client.loop()  # Need to be called regularly with custom loop
        pass

    @abstractmethod
    def publish_event(self):
        """Publishing to Subscribed Displays.

        Data to Collect:
        ----------------
        - Datetime
        - Available Bays
        - Temperature
        - Number of Parked Cars
        - Number of Un-parked Cars
        - Total Number of Cars in the Car Park (both Parked and Un-parked)
        - List of Available Bays
        - List of Unavailable Bays
        - Car Details who entered or exited
        """
        # self.display_publisher.publish(<message>)
        pass

    @abstractmethod
    def on_car_entry(self):
        """Update the Properties/Fields of ManagementCenter and Generating a Car instance for the
        ManagementCenter"""
        # self.management_center.enter_car(<Car>)
        pass

    @abstractmethod
    def on_car_exit(self):
        """Update the Properties/Fields of ManagementCenter"""
        # self.management_center.exit_car(<temperature>)
        pass

    @abstractmethod
    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        pass


class SimulatedCarPark(CarPark):
    QUIT_FLAG: bool = False

    CAR_ENTERED: str | None = None

    def select_random_bay_topic(self) -> str:
        """Could be useful if publishing to BaySensors (i.e. BaySensors can be a Subscriber)"""
        return random.choice(self.sensor_topics)

    def start_serving(self):
        thread = threading.Thread(name=self.name, target=self.client.loop_forever)
        thread.daemon = True
        thread.start()

        while not self.QUIT_FLAG:
            try:
                # Simulate Driver Finding a Parking Bay to Park
                rnd_time_interval = random.randint(1, 3)
                time.sleep(rnd_time_interval)
                print("Trying to park a car ...")
                self.car_parked()
            except KeyboardInterrupt:
                self.QUIT_FLAG = True
                exit()

    def publish_event(self):
        # "<spaces>;<temperature>;<time>"
        print("=" * 100)
        msg_str = f"{len(self.management_center.available_parking_bays)};" \
                  f"{self.temperature};" \
                  f"{self.management_center.entry_exit_time.strftime('%Y-%m-%d %H:%M:%S')}"

        self.publish_to_display(msg_str)
        print(self.management_center.get_carpark_details())
        print("=" * 100)
        print("\n")

    def on_car_entry(self):
        assert isinstance(self.CAR_ENTERED, str), "Forgotten to update CAR_ENTERED!"
        car_entered = Car.from_json(self.CAR_ENTERED)
        car_entered.car_entered(self.temperature)
        self.management_center.enter_car(car_entered)
        self.publish_event()

    def on_car_exit(self):
        car_exited: Car | None = self.management_center.exit_car(self.temperature)
        if isinstance(car_exited, Car):
            self.publish_event()
        else:
            print(f"The Result was None when Exited!")

    def car_parked(self):
        # Idea: Simulate by generating random interval and then invoke this method
        # result: Tuple[<bay>, <car>] | None = self.management_center.car_parked()
        # Publish the result to BaySensor
        # Topic: <root>/<location>/<carpark_name>/parked
        # Message: "<bay>;<car_json_str>"

        result: Tuple[Hashable, Car] | None = self.management_center.car_parked()

        if result is None:
            return

        bay = result[0]
        car_parked = result[1]
        topic = self.create_topic_qualifier("parked")
        message = f"{bay};{car_parked.to_json_format()}"
        self.client.publish(topic, message)

    def car_unparked(self, bay: Hashable, car: Car):
        # Listening to BaySensor
        # result: Car | None = self.management_center.car_unparked(bay, car)

        result: Car | None = self.management_center.car_unparked(bay, car)

        if result is None:
            print(f"The Result of Unparking Car {car} in Bay {bay} is None!")

    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        # We are listening and subscribed to: CarParkSensor Entry/Exit and BaySensor Unparked Topics
        payload = message.payload.decode()

        print(f"Received Topic: {message.topic}")
        event_type = payload.split(",")[0].strip()
        print(event_type)

        if event_type == "Enter":
            # Extract the Car
            # Get Temperature
            self.temperature = float(payload.split(";")[0].split(",")[1])
            # car = Car.from_json(payload.split(";")[1])
            self.CAR_ENTERED = payload.split(";")[1]
            self.on_car_entry()
        elif event_type == "Exit":
            # Get Temperature
            self.temperature = float(payload.split(",")[1])
            self.on_car_exit()
        elif event_type == "Unparked":
            # Get Bay and Car
            car = Car.from_json(payload.split(";")[1])
            bay = payload.split(";")[0].split(",")[1]
            self.car_unparked(bay, car)
        else:
            # print(f"Received Unknown Message\nTopic: {message.topic}\nMessage: {payload}\n")
            print(f"Received Unknown Message\nTopic: {message.topic}\nMessage: {payload}\n")


if __name__ == '__main__':
    pass
