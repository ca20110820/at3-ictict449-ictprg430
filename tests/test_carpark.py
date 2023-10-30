import unittest

from smartpark.carpark import CarPark


class TestCarPark(unittest.TestCase):
    def test_no_negative_spaces(self):
        car_park = CarPark({"broker": "localhost",
                            "port": 1883,
                            "topic-root": "lot",
                            "name": "raf-park",
                            "location": "L306",
                            "topic-qualifier": "car-park",
                            "total-spaces": 0,
                            "total-cars": 3
                            },
                           test_mode=True
                           )

        car_park.on_car_entry()
        car_park.on_car_entry()
        car_park.on_car_entry()
        car_park.on_car_entry()
        self.assertEqual(car_park.available_spaces, 0)

    def test_full_parking_lots(self):
        car_park = CarPark({"broker": "localhost",
                            "port": 1883,
                            "topic-root": "lot",
                            "name": "raf-park",
                            "location": "L306",
                            "topic-qualifier": "car-park",
                            "total-spaces": 5,
                            "total-cars": 5
                            },
                           test_mode=True
                           )

        car_park.on_car_entry()
        car_park.on_car_entry()
        car_park.on_car_entry()
        self.assertEqual(car_park.total_cars, 5)
        self.assertEqual(car_park.available_spaces, 0)

        car_park.on_car_exit()
        car_park.on_car_exit()
        car_park.on_car_exit()
        self.assertEqual(car_park.total_cars, 2)
        self.assertEqual(car_park.available_spaces, 3)

        car_park.on_car_exit()
        car_park.on_car_exit()
        car_park.on_car_exit()
        self.assertEqual(car_park.total_cars, 0)
        self.assertEqual(car_park.available_spaces, 5)
