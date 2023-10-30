from typing import List, Dict, Any, Callable, Tuple
from abc import abstractmethod, ABC
from datetime import datetime
import paho.mqtt.client as paho
import json
import os
import random
import pprint

from smartpark.car import Car
from smartpark.mqtt_device import MqttDevice
from smartpark.sensor import parse_sensor_message
from smartpark.loggers import log_data


class ManagementCenter(ABC):
    def __init__(self, num_parking_bays):
        if num_parking_bays < 1:
            raise ValueError("Max Parking Lot Capacity Cannot be Zero or Negative!")

        self.num_parking_bays = num_parking_bays
        self.parking_bays: Dict[int, Car | None] = {i: None for i in range(1, num_parking_bays+1)}
        self.cars: List[Car] = []  # List of all the Cars in the Car Park (Both Parked & Not Parked)

        self._entry_exit_time: datetime | None = None

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
    def available_parking_bays(self) -> List[int]:
        return [bay_num for bay_num, car in self.parking_bays.items() if car is None]

    @property
    def unavailable_parking_bays(self) -> List[int]:
        return [bay_num for bay_num, car in self.parking_bays.items() if car is not None]

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
        return {bay_num: "Occupied" if isinstance(car, Car) else "Available" for bay_num, car in
                self.parking_bays.items()}

    @property
    def cars_status(self):
        """Gets the Parking Status of each Car in the Car Park: 'Parked' or 'Unparked'"""
        return {car.license_plate: "Parked" if car.is_parked else "Unparked" for car in self.cars}

    def get_carpark_details(self):
        parking_bays_and_parked_cars = {k: v.license_plate if isinstance(v, Car) else "" for k, v in
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

        return json.dumps(carpark_details, indent=4, sort_keys=False, default=str)

    def add_capacity(self, num_lots):
        # TODO: Check about available bays
        assert isinstance(num_lots, int) and num_lots > 0
        self.num_parking_bays += num_lots

    def remove_capacity(self, num_lots):
        # TODO: Check about available bays
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
        """Car Entering the Car Park"""
        assert car.license_plate not in [c.license_plate for c in
                                         self.cars], f"Car with license place {car.license_plate} " \
                                                     f"is already in the parking lot"
        self.cars.append(car)

        self.entry_exit_time = car.entry_time  # Pass the entry_time of the car to entry_exit_time

        # TODO: Need Logging and Store Data for Entering Car
        print(f"Car '{car}' Entering")

        # Select Random Un-parked Car to Park to Random Available Bay, if applicable
        selected_bay = self._select_random_available_bay()
        selected_car = self._select_random_car_to_park()

        # TODO: Need Logging and Store Data for Car Park when a Car Entered

        if selected_bay is not None and selected_car is not None:
            self.parking_bays[selected_bay] = selected_car
            self.parking_bays[selected_bay].is_parked = True

        log_data(selected_car.to_json_format(), "cars.txt")

        try:
            # print("\n")
            # pprint.pprint(selected_car.to_json_format())
            print(selected_car.to_json_format())
            # print("\n")
        except Exception as e:
            print(e)

    def exit_car(self, temperature):
        # Select Random Car to Un-park and Exit, if applicable
        if len(self.cars) == 0:
            return

        selected_car: Car = random.choice(self.cars)

        print(f"Car '{selected_car}' is Exiting")
        print(f"Car '{selected_car}' parking status: {selected_car.is_parked}")

        if selected_car.is_parked:  # Case 1: Parked
            parked_cars_dict = {k: v for k, v in self.parking_bays.items() if v is not None}  # Parked Cars
            occupied_bays = [k for k, v in parked_cars_dict.items() if v.license_plate == selected_car.license_plate]

            assert len(occupied_bays) == 1, f"There are more than one bays for {selected_car.license_plate}!"

            the_bay = occupied_bays[0]
            self.remove_car(self.parking_bays[the_bay])
            self.parking_bays[the_bay] = None
        else:  # Case 2: Un-parked
            self.remove_car(selected_car)

        selected_car.car_exit(temperature)

        # pprint.pprint(selected_car.to_json_format())
        print(selected_car.to_json_format())

        self.entry_exit_time = selected_car.exit_time  # Pass the exit_time of the car to entry_exit_time

        # TODO: Need Logging and Store Data for Exiting Car
        # TODO: Need Logging and Store Data for Car Park when a Car Exited

        log_data(selected_car.to_json_format(), "cars.txt")

        del selected_car  # Delete the instance

    def _select_random_available_bay(self) -> int | None:
        # This will be for cars to be parked.
        return random.choice(self.available_parking_bays) if len(self.available_parking_bays) != 0 else None

    def _select_random_unavailable_bay(self) -> int | None:
        return random.choice(self.unavailable_parking_bays) if len(self.unavailable_parking_bays) != 0 else None

    def _select_random_car_to_park(self) -> Car | None:
        return random.choice(self.unparked_cars) if len(self.unparked_cars) != 0 else None

    def _select_random_car_to_unpark(self) -> Car | None:
        return random.choice(self.parked_cars) if len(self.parked_cars) != 0 else None


class CarPark(ABC):
    def __init__(self, config, management_center_type, num_parking_bays, *args, **kwargs):
        self.sensor_topics: List[str] = []
        self.carpark_name: str = config["name"]
        self.pubsub: MqttDevice = MqttDevice(config)

        self._temperature: int | float | None = None

        self.management_center: ManagementCenter = management_center_type(num_parking_bays, *args, **kwargs)
        self.pubsub.client.on_message = self.on_message  # Bind the on_message callback

    def add_sensor_topic(self, sensor_topic: str):
        """Display Topic: <topic-root>/<location>/<name>/display"""
        self.sensor_topics.append(sensor_topic)
        self.pubsub.client.subscribe(sensor_topic)
        # self.add_topic_and_callback(sensor_topic, self.on_message)

    def add_sensor_topics(self, sensor_topics: List[Tuple[str, int]]):
        for topic, _ in sensor_topics:
            self.sensor_topics.append(topic)
        print(self.sensor_topics)
        self.pubsub.client.subscribe(sensor_topics)

    def remove_sensor_topic(self, sensor_topic: str):
        self.sensor_topics.remove(sensor_topic)
        self.pubsub.client.unsubscribe(sensor_topic)

    def add_topic_and_callback(self, topic: str, on_message: Callable):
        self.pubsub.client.message_callback_add(topic, on_message)

    def publish_to_display(self, message: str):
        self.pubsub.client.publish(self.display_topic, message)

    @property
    def display_topic(self):
        return self.pubsub.create_topic_qualifier("display")

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

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
        # Implement Callback when Received Message from Sensors or Publishers
        pass


class SimulatedCarPark(CarPark):
    def __init__(self, config, num_parking_bays, *args, **kwargs):
        super().__init__(config, SimulatedManagementCenter, num_parking_bays, *args, **kwargs)

    def start_serving(self):
        """Start listening to sensors"""
        self.pubsub.client.loop_forever()

    def publish_event(self):
        # "<spaces>;<temperature>;<time>"
        msg_str = f"{len(self.management_center.available_parking_bays)};" \
                  f"{self.temperature};" \
                  f"{self.management_center.entry_exit_time.strftime('%Y-%m-%d %H:%M:%S')}"

        print(f"Publishing to {self.display_topic} : {msg_str}")
        self.publish_to_display(msg_str)
        print("\n")
        # pprint.pprint(self.management_center.get_carpark_details())
        print(self.management_center.get_carpark_details())
        print("\n")
        print("=" * 100)

    def on_car_entry(self):
        self.management_center.enter_car(Car.generate_random_car(self.temperature))
        self.publish_event()

    def on_car_exit(self):
        self.management_center.exit_car(self.temperature)
        self.publish_event()

    def on_message(self, client: paho.Client, userdata: Any, message: paho.MQTTMessage):
        payload = message.payload.decode()  # "<Entry|Exit>,<temperature>"
        entry_or_exit, self.temperature = parse_sensor_message(payload)  # ("<Entry|Exit>",<temperature>)

        print(f"Topic: {message.topic}")
        print(fr"Message Received: {payload}")
        print(fr"Message Topic: {message.topic}")
        print("\n")

        if entry_or_exit == "Entry":
            self.on_car_entry()
        elif entry_or_exit == "Exit":
            self.on_car_exit()
