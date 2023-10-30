"""
All Detectors must publish the message with the following string template:
                    "<Entry|Exit>,<temperature>"
where
    <Entry|Exit> := Detected event, Car Entry or Exit
    <temperature> := Temperature generated randomly, from a file, or from external source with API
"""
import paho.mqtt.client as paho
from abc import ABC, abstractmethod
from typing import Any
import time
import random
import tkinter as tk

from smartpark.mqtt_device import MqttDevice


def parse_sensor_message(message: str):
    out_list = message.split(',')  # ["<Entry|Exit>", "<temperature>"]
    float_val = float(out_list[1])  # Temperature as Float
    temperature = float("{:.2f}".format(float_val))
    return out_list[0], temperature


class Sensor(MqttDevice):
    def on_detection(self, message: str, **kwargs):
        self.client.publish(self.topic_address, payload=message, **kwargs)


# ======================================================================================================================


class IEntrySensor(ABC):
    @abstractmethod
    def on_car_entry(self):
        pass


class IExitSensor(ABC):
    @abstractmethod
    def on_car_exit(self):
        pass


class IEntryExitSensor(ABC):
    @abstractmethod
    def on_car_entry(self):
        pass

    @abstractmethod
    def on_car_exit(self):
        pass


class BaseSensor(MqttDevice):
    IS_OCCUPIED = False

    @abstractmethod
    def temperature(self):
        """Implement Getter for Temperature, this can be random or pulled from API"""
        raise NotImplementedError()

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Must be implemented with infinite loop"""
        pass


class CLISensor(BaseSensor, IEntryExitSensor):

    IS_OCCUPIED = False

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
            elif detection == "x":
                if self.IS_OCCUPIED:
                    print("Car Exited")
                    self.on_car_exit()
            else:
                continue

    def on_car_entry(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/entry
        # Message: "Entry,'<license_plate>','<car_model>',<temperature>"
        self.client.publish(self.create_topic_qualifier("entry"), f"Entry,<license_plate>,<car_model>,{self.temperature}")
        self.IS_OCCUPIED = True

    def on_car_exit(self):
        # Topic: <topic-root>/<location>/<bay_id_or_name>/exit
        # Message: "Entry,<temperature>"
        self.client.publish(self.create_topic_qualifier("exit"), f"Exit,{self.temperature}")
        self.IS_OCCUPIED = False
# ======================================================================================================================


class Detector(ABC):
    @abstractmethod
    def temperature(self):
        pass

    @abstractmethod
    def start_sensing(self, *args, **kwargs):
        """Must be implemented with infinite loop"""
        pass

    def on_car_entry(self):
        """Define on_car_entry event-handler"""
        pass

    def on_car_exit(self):
        """Define on_car_exit event-handler"""
        pass


class EntryOnlyDetector(Detector):
    def __init__(self, config, *args, **kwargs):
        self.entry_sensor = Sensor(config, *args, **kwargs)

    @property
    def temperature(self):
        raise NotImplementedError()

    def start_sensing(self, *args, **kwargs):
        """Must be implemented with infinite loop"""
        raise NotImplementedError()

    def on_car_entry(self):
        self.entry_sensor.on_detection(f"Entry,{self.temperature}")


class ExitOnlyDetector(Detector):
    def __init__(self, config, *args, **kwargs):
        self.exit_sensor = Sensor(config, *args, **kwargs)

    @property
    def temperature(self):
        raise NotImplementedError()

    def start_sensing(self, *args, **kwargs):
        """Must be implemented with infinite loop"""
        raise NotImplementedError()

    def on_car_exit(self):
        self.exit_sensor.on_detection(f"Exit,{self.temperature}")


class EntryExitDetector(Detector):
    def __init__(self, entry_config, exit_config):
        self.entry_sensor = Sensor(entry_config)
        self.exit_sensor = Sensor(exit_config)

    @property
    def temperature(self):
        raise NotImplementedError()

    def start_sensing(self, *args, **kwargs):
        """Must be implemented with infinite loop"""
        raise NotImplementedError()

    def on_car_entry(self):
        self.entry_sensor.on_detection(f"Entry,{self.temperature}")

    def on_car_exit(self):
        self.exit_sensor.on_detection(f"Exit,{self.temperature}")


class GUICarDetector(EntryExitDetector):
    def __init__(self, entry_sensor_config, exit_sensor_config):
        super().__init__(entry_sensor_config, exit_sensor_config)
        self.root = tk.Tk()
        self.root.title("Car Detector ULTRA")

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


class CLIDetector(EntryExitDetector):
    def __init__(self, entry_sensor_config, exit_sensor_config):
        super().__init__(entry_sensor_config, exit_sensor_config)

    @property
    def temperature(self):
        # TODO: Import a callable from temperature.py to get the temperature
        return random.randint(10, 30)

    def start_sensing(self):
        """ A blocking event loop that waits for detection events, in this
                case Enter presses"""
        print("Press E when Car entered!")
        print("Press X when Car exited!\n")
        while True:
            detection = input("e or x> ")
            if detection == "e":
                self.on_car_entry()
            elif detection == "x":
                self.on_car_exit()
            else:
                continue


class RandomDetector(EntryExitDetector):
    def __init__(self, entry_sensor_config, exit_sensor_config):
        super().__init__(entry_sensor_config, exit_sensor_config)

    @property
    def temperature(self):
        # TODO: Import a callable from temperature.py to get the temperature
        # TODO: Fix - Too fast that value of temperature is None. If None use temperature API to get it independently.
        return random.randint(10, 30)

    def start_sensing(self):
        while True:
            time_interval = 1  # random.randint(1, 2)  # Random Number between 0 & 1
            time.sleep(time_interval)
            rnd = random.choice(["Entry", "Exit"])
            if rnd == "Entry":
                print("Car Entered")
                self.on_car_entry()
            elif rnd == "Exit":
                print("Car Exited")
                self.on_car_exit()
            else:
                continue


class FileDataDetector(EntryExitDetector):
    """
    The format of the data in the file must follow the following structure:
    <Entry|Exit>,<temperature>

    Example:
    Entry,23
    Entry,22
    Exit,25
    Exit,26

    Comma Separated
    """
    def __init__(self, entry_sensor_config: dict, exit_sensor_config: dict, file_path: str):
        super().__init__(entry_sensor_config, exit_sensor_config)
        self.file_path = file_path

        self._temperature: int | float | None = None

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    def start_sensing(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.rstrip()
                print(line)
                entry_or_exit, self.temperature = parse_sensor_message(line)

                if entry_or_exit in ["Entry"]:
                    self.on_car_entry()
                elif entry_or_exit in ["Exit"]:
                    self.on_car_exit()
                else:
                    # Send quit signal/event
                    continue


if __name__ == "__main__":
    sensor_config = {"name": "bay1",
                     "location": "L306",
                     "host": "localhost",
                     "port": 1883,
                     "topic-root": "Moondaloop Park",
                     "topic-qualifier": "na"
                     }
    CLISensor(sensor_config).start_sensing()
