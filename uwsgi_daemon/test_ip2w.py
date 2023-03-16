import unittest
import functools
from ip2w import *


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                	f(*new_args)
                except Exception as e:
                    print(str(new_args[1]) + '\n')
                    print('ERROR TEST: '+str(e))
        return wrapper
    return decorator

class TestClasses(unittest.TestCase):

	@cases([
        {"url": "http://localhost:9090/ip2w/176.14.221.123"},
        {"url": "http://localhost/ip2w/176.14.221.123"},
        {"url": "localhost/ip2w/176.14.221.123"},
        {"url": "localhost/ip2w/176.14.221.123/"}
    ])
	def test_parse_url_ok(self, test_case):
		code, ip = parse_url(test_case['url'])
		self.assertEqual(code, 200)

	@cases([
        {"url": "http://localhost:9090/ip2w/176.14.221"},
        {"url": "http://localhost/ip2w/176.14.221.abc"},
        {"url": "localhost/ip2w/176.14.221.444"}
    ])
	def test_parse_url_bad(self, test_case):
		code, ip = parse_url(test_case['url'])
		self.assertEqual(code, 400)

	@cases([
        {"ip": "176.14.221.123"},
        {"ip": "205.14.56.74"}
    ])
	def test_get_city_ok(self, test_case):
		code, city = get_city(test_case['ip'])
		self.assertEqual(code, 200)

	@cases([
        {"ip": "255.255.255.255"},
        {"ip": "192.168.1.1"},
    ])
	def test_get_city_bad(self, test_case):
		code, city = get_city(test_case['ip'])
		print(city)
		self.assertEqual(code, 400)

	@cases([
        {"city": "Moscow"},
        {"city": "Campbell"}
    ])
	def test_get_weather_data_ok(self, test_case):
		code, weather = get_weather_data(test_case['city'])
		self.assertEqual(code, 200)

	@cases([
        {"city": "not-a-city"}
    ])
	def test_get_weather_data_bad(self, test_case):
		code, weather = get_weather_data(test_case['city'])
		self.assertEqual(code, 400)


if __name__ == "__main__":
    unittest.main()