import os
import re
import json
from configparser import ConfigParser
import requests
import logging


OK = 200
BAD_REQUEST = 400
INTERNAL_ERROR = 500
CONFIG = "/usr/local/etc/ip2w.ini"


def get_weather(env, max_try):
	"""
	Основная функция распределения задач для получения конечной информаци
	о погоде
	"""
	code, ip = parse_url(env)
	if code != OK:
		return code, ip
	code, city_country = get_city(ip, max_try)
	if code != OK:
		return code, ip
	code, weather = get_weather_data(city_country, max_try)
	return code, weather


def parse_url(env):
	"""
	Функция парсинга тела запроса для получения ip-адреса
	"""
	ip = env.strip('/').split('/')[-1]
	# проеряем ip регуляркой
	if re.fullmatch(r'\d{1,3}?\.\d{1,3}?\.\d{1,3}?\.\d{1,3}', ip):
		# проверяем ip адрес по октетам
		for octet in ip.split('.'):
			if int(octet) < 1 or int(octet) > 255:
				# если в запросе пришел неверный ip-адрес
				# возвращаем ответ с ошибкой
				err_msg = "Wrong ip: {}".format(ip)
				return BAD_REQUEST, err_msg
		return OK, ip
	else:
		# если в запросе пришел неверный ip-адрес
		# возвращаем ответ с ошибкой
		err_msg = "Wrong ip: {}".format(ip)
		return BAD_REQUEST, err_msg


def get_city(ip, max_try, trying=0):
	"""
	Функция получения города по принадлежности ip-адресов к регионам
	с использованием сервиса "ipinfo"
	"""
	try:
		res = requests.get('https://ipinfo.io/'+ip)
		data = res.json()
		# если в запросе не пришли данны о городе или стране - возвращаем ошибку
		if 'city' not in data.keys() and 'country' not in data.keys():
			msg = "Cannot find country or city by this ip {}".format(ip)
			return BAD_REQUEST, msg
		else:
			# Если все хорошо, то возвращаем данные о горожде со статусом 200
			return OK, data['city']
	except Exception as e:
		# Совершаем n попыток подключиться к сервису,
		# если не удается получить данные сразу
		if trying < max_try:
			trying+=1
			get_city(ip, max_try, trying)
		# если не удается подключиться возвращаем ошибку
		msg = "Error in connecting to ipinfo.io"
		return INTERNAL_ERROR, msg
	

def get_weather_data(city, max_try, trying=0):
	"""
	Функция получения погоды по названию города
	с использованием сервиса "openweathermap"
	"""
	
	try:
		# для использования сервиса необходим токен (получение при регистрации)
		app_key = os.environ.get("WEATHER_API_KEY")
		app_key = "e86882e61a7d2d99fedb3986a156824f"
		res = requests.get("https://api.openweathermap.org/data/2.5/weather"+
							"?q={}&units=metric&lang=ru&appid={}"\
							.format(city, app_key))
		data = res.json()
		# если в ответе от сервера пришли данные о погоде - рендерим данные
		# и возвращаем ответ
		if 'main' in data.keys() and 'weather' in data.keys():
			response = {'city':city,
						'temp':int(data['main']['temp']),
						'conditions':','.join([weather['description'] \
												for weather in data['weather']])}
			return OK, response
		# если в ответе от сервера не пришли данные о погоде - возвращаем ошибку
		else:
			msg = "Cannot find weather data in {} or api_key incorrect".format(city)
			return BAD_REQUEST, msg
	except Exception as e:
		if trying < max_try:
			trying+=1
			get_weather_data(city, max_try, trying)
		msg = "Error in connecting to api.openweathermap.org"
		return INTERNAL_ERROR, msg
		
	
def application(environ, start_response):
	"""
	Основная функция для запуска uwsgi приложения
	"""
	# считываем конфигурацию и настраиваем логгирование
	config = ConfigParser()
	config.read(CONFIG)
	config = dict(config["ip2w"])
	max_try = int(config["max_try"])

	logging.basicConfig(filename=config["log_file"], level=logging.INFO,
						format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
	code, response = get_weather(environ['REQUEST_URI'], max_try)
	# рендерим ответ и отправляем клиенту
	if not isinstance(response, str):
		response = json.dumps(response, ensure_ascii=False, indent="\t")
	response = response.encode(encoding="UTF-8")
	response_headers = [
		('Content-Type', 'text/plain'),
		('Content-Length', str(len(response)))
	]
	start_response(str(code), response_headers)
	return [response]