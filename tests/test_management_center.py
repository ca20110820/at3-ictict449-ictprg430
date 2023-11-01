import unittest

from smartpark.carpark import SimulatedManagementCenter
from smartpark.car import Car


class TestSimulatedManagementCenter(unittest.TestCase):
    def setUp(self) -> None:
        self.management_center = SimulatedManagementCenter()
        self.management_center.add_parking_bays(1, 2)

    def test_entry_exit_cycle(self):
        self.assertEqual(self.management_center.num_available_parking_bays, 2)
        self.assertEqual(self.management_center.num_parking_bays, 2)
        self.assertEqual(self.management_center.num_cars_in_park, 0)

        car = Car.generate_random_car(["AAA", "BBB", "CCC"])
        car.car_entered(21)

        self.management_center.enter_car(car)

        self.assertFalse(car.is_parked)
        self.assertEqual(self.management_center.num_available_parking_bays, 2)
        self.assertEqual(self.management_center.num_parking_bays, 2)
        self.assertEqual(self.management_center.num_cars_in_park, 1)

        tup = self.management_center.car_parked()
        self.assertIsInstance(tup, tuple)
        bay = tup[0]
        c_parked = tup[1]
        self.assertTrue(c_parked.is_parked)
        self.assertEqual(self.management_center.num_available_parking_bays, 1)
        self.assertEqual(self.management_center.num_cars_in_park, 1)
        self.assertEqual(len(self.management_center.unparked_cars), 0)
        self.assertEqual(c_parked.entry_temperature, 21)
        self.assertIsNone(c_parked.exit_temperature)

        c_unparked = self.management_center.car_unparked(bay, c_parked)
        self.assertFalse(c_unparked.is_parked)
        self.assertEqual(self.management_center.num_available_parking_bays, 2)
        self.assertEqual(self.management_center.num_cars_in_park, 1)
        self.assertEqual(len(self.management_center.unparked_cars), 1)
        self.assertEqual(c_parked.entry_temperature, 21)
        self.assertIsNone(c_parked.exit_temperature)

        c_exited = self.management_center.exit_car(22)
        self.assertTrue(self.management_center.parking_bays[bay] is None)
        self.assertNotIn(c_exited, self.management_center.cars)
        self.assertEqual(c_exited.entry_temperature, 21)
        self.assertEqual(c_exited.exit_temperature, 22)

        self.assertEqual(self.management_center.num_available_parking_bays, 2)
        self.assertEqual(self.management_center.num_cars_in_park, 0)
        self.assertEqual(len(self.management_center.unparked_cars), 0)


if __name__ == "__main__":
    unittest.main()
