import random
import unittest
from datetime import datetime

from smartpark.carpark import SimulatedManagementCenter
from smartpark.car import Car


class TestRandomEntryExitManagementCenter(unittest.TestCase):
    def test_management_center_invalid_arg(self):
        num_parking_bays = 0
        self.assertRaises(ValueError, SimulatedManagementCenter, num_parking_bays)

        num_parking_bays = -1
        self.assertRaises(ValueError, SimulatedManagementCenter, num_parking_bays)

    def test_one_parking_lot(self):
        num_parking_bays = 1
        management_center = SimulatedManagementCenter(num_parking_bays)
        self.assertEqual(management_center.num_cars_in_park, 0)
        self.assertEqual(management_center.num_available_parking_bays, num_parking_bays)
        self.assertEqual(len(management_center.parked_cars), 0)
        self.assertEqual(len(management_center.unparked_cars), 0)
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

        # Try to exit even if there are no cars in the Car Park
        management_center.exit_car(30)
        self.assertEqual(management_center.num_cars_in_park, 0)
        self.assertEqual(management_center.num_available_parking_bays, num_parking_bays)
        self.assertEqual(len(management_center.parked_cars), 0)
        self.assertEqual(len(management_center.unparked_cars), 0)
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

        car1 = Car("1111", "ModelA", 20)
        management_center.enter_car(car1)
        self.assertEqual(management_center.num_cars_in_park, 1)
        self.assertEqual(management_center.num_available_parking_bays, 0)
        self.assertEqual(car1.is_parked, True)
        self.assertEqual(len(management_center.parked_cars), 1)
        self.assertEqual(len(management_center.unparked_cars), 0)
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

        car2 = Car("2222", "ModelB", 24)
        management_center.enter_car(car2)
        self.assertEqual(management_center.num_cars_in_park, 2)
        self.assertEqual(management_center.num_available_parking_bays, 0)
        self.assertEqual(car2.is_parked, False)
        self.assertEqual(len(management_center.parked_cars), 1)
        self.assertEqual(len(management_center.unparked_cars), 1)
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

        management_center.exit_car(21)
        self.assertEqual(management_center.num_cars_in_park, 1)
        # Uncertain if Parked or Un-parked Car who left
        self.assertIn(management_center.num_available_parking_bays, [0, 1])
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

    def test_one_car(self):
        num_parking_bays = 10
        management_center = SimulatedManagementCenter(num_parking_bays)

        self.assertEqual(management_center.num_cars_in_park, 0)
        self.assertEqual(management_center.num_available_parking_bays, num_parking_bays)
        self.assertEqual(len(management_center.parked_cars), 0)
        self.assertEqual(len(management_center.unparked_cars), 0)
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

        car = Car("1111", "ModelA", 20)
        management_center.enter_car(car)
        self.assertEqual(management_center.num_cars_in_park, 1)
        self.assertEqual(management_center.num_available_parking_bays, num_parking_bays - 1)
        self.assertEqual(car.is_parked, True)
        self.assertEqual(len(management_center.parked_cars), 1)
        self.assertEqual(len(management_center.unparked_cars), 0)
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

        management_center.exit_car(21)
        self.assertEqual(management_center.num_cars_in_park, 0)
        self.assertEqual(management_center.num_available_parking_bays, num_parking_bays)
        self.assertEqual(len(management_center.parked_cars), 0)
        self.assertEqual(len(management_center.unparked_cars), 0)
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)

    def test_many_random_cars(self):
        num_parking_bays = 3
        management_center = SimulatedManagementCenter(num_parking_bays)

        # 5 Cars
        management_center.enter_car(Car.generate_random_car(random.randint(20, 30)))
        management_center.enter_car(Car.generate_random_car(random.randint(20, 30)))
        management_center.enter_car(Car.generate_random_car(random.randint(20, 30)))
        management_center.enter_car(Car.generate_random_car(random.randint(20, 30)))
        management_center.enter_car(Car.generate_random_car(random.randint(20, 30)))

        self.assertEqual(management_center.num_cars_in_park, 5)
        self.assertEqual(management_center.num_available_parking_bays, 0)
        self.assertEqual(len(management_center.parked_cars), 3)
        self.assertEqual(len(management_center.unparked_cars), 2)

        # Exiting
        management_center.exit_car(random.randint(20, 30))
        management_center.exit_car(random.randint(20, 30))

        self.assertEqual(management_center.num_cars_in_park, 3)
        print("num_available_parking_bays: ", management_center.num_available_parking_bays)
        print("num_parked_cars:", len(management_center.parked_cars))
        print("num_unparked_cars:", len(management_center.unparked_cars))
        self.assertEqual(len(management_center.parked_cars) + len(management_center.unparked_cars),
                         management_center.num_cars_in_park)


if __name__ == "__main__":
    unittest.main()
