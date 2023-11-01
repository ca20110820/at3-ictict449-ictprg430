from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Hashable

import json

from paho.mqtt.client import MQTTMessage

from smartpark.mqtt_device import MqttDevice
from smartpark.car import Car


class IParkable(ABC):

    BAY: Hashable | None = None

    @abstractmethod
    def car_parked(self):
        pass

    @abstractmethod
    def car_unparked(self):
        pass


class ManagementCenter:
    def __init__(self):

        self.num_parking_bays = 0
        self.parking_bays: Dict[Hashable, Car | None] = {}
        self.cars: List[Car] = []  # List of all the Cars in the Car Park (Both Parked & Not Parked)

        self._entry_exit_time: datetime | None = None

    @classmethod
    def from_int_bays_and_num_parking_pays(cls, num_parking_bays):
        instance = cls()
        instance.num_parking_bays = num_parking_bays
        instance.parking_bays = {i: None for i in range(1, num_parking_bays+1)}

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


class SimulatedManagementCenter(ManagementCenter, IParkable):
    def enter_car(self, car: Car):
        pass

    def exit_car(self, temperature):
        pass

    def car_parked(self):
        pass

    def car_unparked(self):
        pass


class CarPark(MqttDevice):
    def __init__(self, config, management_center_type: Type[ManagementCenter], num_parking_bays, *args, **kwargs):
        super().__init__(config, *args, **kwargs)


if __name__ == '__main__':
    pass
