from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict

import json

from paho.mqtt.client import MQTTMessage

from smartpark import mqtt_device
from smartpark.car import Car


class ManagementCenter(ABC):
    def __init__(self, num_parking_bays):
        if num_parking_bays < 1:
            raise ValueError("Max Parking Lot Capacity Cannot be Zero or Negative!")

        self.num_parking_bays = num_parking_bays
        self.parking_bays: Dict[str, Car | None] = {i: None for i in range(1, num_parking_bays+1)}
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
    def available_parking_bays(self) -> List[str]:
        return [bay for bay, car in self.parking_bays.items() if car is None]

    @property
    def unavailable_parking_bays(self) -> List[str]:
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


# class CarPark(mqtt_device.MqttDevice):
#     """Creates a carpark object to store the state of cars in the lot"""
#
#     def __init__(self, config, test_mode=False):
#         super().__init__(config)
#         self.total_spaces = config['total-spaces']
#         self.total_cars = config['total-cars']
#         self.client.on_message = self.on_message
#         self.client.subscribe('sensor')
#         if not test_mode:
#             self.client.loop_forever()
#         self._temperature = None
#
#     @property
#     def available_spaces(self):
#         available = self.total_spaces - self.total_cars
#         return max(available, 0)
#
#     @property
#     def temperature(self):
#         return self._temperature
#
#     @temperature.setter
#     def temperature(self, value):
#         self._temperature = value
#
#     def _publish_event(self):
#         readable_time = datetime.now().strftime('%H:%M:%S')
#         print(
#             (
#                 f"TIME: {readable_time}, "
#                 + f"SPACES: {self.available_spaces}, "
#                 + f"TEMPC: {self.temperature}"
#             )
#         )
#
#         if self.available_spaces == 0:
#             msg_str = f"Full;{self.temperature};{readable_time}"  # "<spaces>;<temperature>;<time>"
#         else:
#             msg_str = f"{self.available_spaces};{self.temperature};{readable_time}"  # "<spaces>;<temperature>;<time>"
#
#         self.client.publish('display', msg_str)
#
#     def on_car_entry(self):
#         self.total_cars += 1
#
#         if self.total_cars >= self.total_spaces:
#             self.total_cars = self.total_spaces
#
#         self._publish_event()
#
#     def on_car_exit(self):
#         self.total_cars -= 1
#
#         if self.total_cars < 0:
#             self.total_cars = 0
#
#         self._publish_event()
#
#     def on_message(self, client, userdata, msg: MQTTMessage):
#         payload = msg.payload.decode()
#         # TODO: Extract temperature from payload
#         # self.temperature = ... # Extracted value
#         entry_or_exit = payload.split(",")[0]
#         self.temperature = payload.split(",")[1]
#         if entry_or_exit == "Entry":
#             self.on_car_entry()
#         elif entry_or_exit == "Exit":
#             self.on_car_exit()
#         else:
#             exit()  # To close carpark.py as a background process (daemon thread)


if __name__ == '__main__':
    pass
