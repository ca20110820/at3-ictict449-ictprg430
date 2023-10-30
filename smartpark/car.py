from datetime import datetime
import time
import random
import string
import json


class Car(object):
    """
    Car Data to be recorded:
    - license_plate
    - car_model
    - entry_time
    - entry_temperature
    - exit_time
    - exit_temperature
    """
    def __init__(self, license_plate: str, car_model: str, entry_temperature: int | float):
        assert isinstance(entry_temperature, (int, float)), "Entry Temperature must be a valid numeric!"

        self.license_plate = license_plate
        self.car_model = car_model
        self.entry_time = datetime.now()  # .strftime("%Y-%m-%d %H:%M:%S")
        self.entry_temperature = entry_temperature

        self.is_parked: bool = False  # When car is instantiated (i.e. Entered) it not parked by default

        self.exit_time: datetime | None = None
        self.exit_temperature: float | int | None = None

    @property
    def duration_in_carpark(self):  # Deprecate: Can be derived and calculated in DBMS
        try:
            return (self.exit_time - self.entry_time).total_seconds()
        except TypeError:
            return None

    def __str__(self):
        return f"{self.license_plate} - {self.car_model}"

    def car_exit(self, exit_temperature):
        assert isinstance(exit_temperature, (int, float)), "Entry Temperature must be a valid numeric!"
        self.exit_time = datetime.now()  # .strftime("%Y-%m-%d %H:%M:%S")
        self.is_parked = False
        self.exit_temperature = exit_temperature

    def to_csv_format(self):
        # TODO: Run Unit Tests
        item_list = [self.license_plate,
                     self.car_model,
                     self.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                     self.exit_time.strftime("%Y-%m-%d %H:%M:%S") if self.exit_time is not None else "null",
                     self.duration_in_carpark if self.duration_in_carpark is not None else "null",
                     self.entry_temperature,
                     self.exit_temperature if self.exit_temperature is not None else "null"
                     ]

        item_list = [str(item) for item in item_list]

        return ",".join(item_list)

    def to_json_format(self):
        # TODO: Fix to_json_format()

        out_json = {"license_plate": self.license_plate,
                    "car_model": self.car_model,
                    "entry_time": self.entry_time,
                    "exit_time": self.exit_time,
                    "parking_duration": self.duration_in_carpark,
                    "entry_temperature": self.entry_temperature,
                    "exit_temperature": self.exit_temperature
                    }

        return json.dumps(out_json, sort_keys=False, default=str)

    def append_to_csv(self, file_path):
        # TODO: Test - Implement append_to_csv()
        with open(file_path, 'a') as file:
            file.write(self.to_csv_format() + "\n")
            pass

    @staticmethod
    def clean_datetime(in_datetime: datetime):
        # TODO: Implement clean_datetime()
        # Utility function for cleaning and parsing the datetime
        pass

    @classmethod
    def generate_random_car(cls, temperature):
        rnd_license_plate = cls.generate_random_license_plate()
        rnd_car_model = cls.generate_random_car_model(["ModelA", "ModelB", "ModelC", "ModelD", "ModelE"])
        return cls(rnd_license_plate, rnd_car_model, temperature)

    @staticmethod
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

    @staticmethod
    def generate_random_car_model(model_list):
        return random.choice(model_list)


if __name__ == "__main__":
    car = Car.generate_random_car(random.randint(10, 30))
    print(car.to_json_format())
    time.sleep(0.5)
    car.car_exit(random.randint(10, 30))
    print(car.to_csv_format())
    # print(car.to_json_format())
    print(json.loads(car.to_json_format()))
    print("=" * 100)

    car = Car.generate_random_car(random.randint(10, 30))
    time.sleep(0.5)
    car.car_exit(random.randint(10, 30))
    print(car.to_csv_format())
    print("=" * 100)

    car = Car.generate_random_car(random.randint(10, 30))
    time.sleep(0.5)
    car.car_exit(random.randint(10, 30))
    print(car.to_csv_format())
    print("=" * 100)

    car = Car.generate_random_car(random.randint(10, 30))
    time.sleep(0.5)
    car.car_exit(random.randint(10, 30))
    print(car.to_csv_format())
    print("=" * 100)

    x = json.dumps({"A": ["s", 1, True, None]})
    print(x)
    print(json.loads(x))

    # for _ in range(5):
    #     car = Car.generate_random_car()
    #     print(car)
    #
    #     print("Entry Time:", car.entry_time)
    #     print(car.duration_in_carpark)  # Error
    #     time.sleep(0.2)
    #     car.is_parked = True
    #     time.sleep(0.4)
    #     car.car_exit()
    #     print("Exit Time:", car.exit_time)
    #     print(car.duration_in_carpark)
    #     print("CSV Format:", car.to_csv_format())
    #     print("JSON Format:", car.to_json_format())
    #     print("=" * 50)
