from datetime import datetime
import time
import random
import string
import json


class Car(object):
    """
    Car Data:
    - license_plate
    - car_model
    - entry_time
    - entry_temperature
    - exit_time
    - exit_temperature
    """
    def __init__(self, license_plate: str, car_model: str):
        self.license_plate = license_plate
        self.car_model = car_model
        self.entry_time: datetime | None = None  # .strftime("%Y-%m-%d %H:%M:%S")
        self.entry_temperature: float | int | None = None

        self.is_parked: bool = False  # When car is instantiated (i.e. Entered) it not parked by default

        self.exit_time: datetime | None = None
        self.exit_temperature: float | int | None = None

    def __str__(self):
        return f"{self.license_plate} - {self.car_model}"

    def car_parked(self):
        self.is_parked = True

    def car_entered(self):
        pass

    def car_exited(self, exit_temperature):
        assert isinstance(exit_temperature, (int, float)), "Entry Temperature must be a valid numeric!"
        self.exit_time = datetime.now()  # .strftime("%Y-%m-%d %H:%M:%S")
        self.is_parked = False
        self.exit_temperature = exit_temperature

    def to_csv_format(self):
        # TODO: Create Parser for to_csv_format()
        item_list = [self.license_plate,
                     self.car_model,
                     self.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                     self.exit_time.strftime("%Y-%m-%d %H:%M:%S") if self.exit_time is not None else "null",
                     self.entry_temperature,
                     self.exit_temperature if self.exit_temperature is not None else "null"
                     ]

        item_list = [str(item) for item in item_list]

        return ",".join(item_list)

    def to_json_format(self):
        # TODO: Create Parser for to_json_format()
        out_json = {"license_plate": self.license_plate,
                    "car_model": self.car_model,
                    "entry_time": self.entry_time,
                    "exit_time": self.exit_time,
                    "entry_temperature": self.entry_temperature,
                    "exit_temperature": self.exit_temperature
                    }

        return json.dumps(out_json, sort_keys=False, default=str)


def generate_random_license_plate():
    format_string = random.choice(["LLL-NNN", "NLL-NNN", "NLLL-NNN", "LL-NNNN", "TAXI-NNNN", "LLL-NNNN"])

    letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(format_string.count("L")))
    numbers = ''.join(random.choice(string.digits) for _ in range(format_string.count("N")))

    license_plate = format_string
    for char in format_string:
        if char == "L":
            license_plate = license_plate.replace(char, letters[0], 1)
            letters = letters[1:]
        elif char == "N":
            license_plate = license_plate.replace(char, numbers[0], 1)
            numbers = numbers[1:]

    return license_plate


def generate_random_car_model(model_list):
    return random.choice(model_list)


def generate_random_car(car_model_list):
    rnd_license_plate = generate_random_license_plate()
    rnd_car_model = generate_random_car_model(car_model_list)
    return Car(rnd_license_plate, rnd_car_model)


if __name__ == "__main__":
    pass
