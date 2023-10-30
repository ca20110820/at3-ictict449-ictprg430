import unittest

import toml  # you can use toml, json,yaml, or ryo for your config file

from smartpark.config_parser import CONFIG_PATH, parse_config


class TestConfigParsing(unittest.TestCase):
    def test_parse_config(self):
        configs = parse_config(CONFIG_PATH)
        self.assertEqual(configs['sensor']['broker'], 'localhost')
        self.assertEqual(configs['sensor']['port'], 1883)
        self.assertEqual(configs['sensor']['topic-root'], 'lot')
        self.assertEqual(configs['sensor']['name'], 'sensor')
        self.assertEqual(configs['sensor']['location'], 'moondaloop')
        self.assertEqual(configs['sensor']['topic-qualifier'], 'na')

        self.assertEqual(configs['carpark']['broker'], 'localhost')
        self.assertEqual(configs['carpark']['port'], 1883)
        self.assertEqual(configs['carpark']['topic-root'], 'lot')
        self.assertEqual(configs['carpark']['name'], 'raf-park')
        self.assertEqual(configs['carpark']['location'], 'L306')
        self.assertEqual(configs['carpark']['topic-qualifier'], 'car-park')
        self.assertEqual(configs['carpark']['total-spaces'], 10)
        self.assertEqual(configs['carpark']['total-cars'], 5)

        self.assertEqual(configs['display']['broker'], 'localhost')
        self.assertEqual(configs['display']['port'], 1883)
        self.assertEqual(configs['display']['topic-root'], 'lot')
        self.assertEqual(configs['display']['name'], 'display')
        self.assertEqual(configs['display']['location'], 'L306')
        self.assertEqual(configs['display']['topic-qualifier'], 'na')
