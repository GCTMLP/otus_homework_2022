from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.core import serializers
from django.http import JsonResponse
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import json
import re

from hasker.settings.models import Profile

class SettingsView(TemplateView):
	"""
	Показываем основной шаблон страницы настройки (шаблон изначально пустой,
	все данные подгружаются в него через vue.js ajax запросом)
	"""
	template_name = "settings.html"

class SettingsViewData(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию о пользователе
	и рендерим ее для отправки обратно в js
	"""

	def post(self, request):
		try:
			session_user = request.user.id
			qs = Profile.objects.select_related('user').get(user_id=int(session_user))
			data = {}
			data['email'] = qs.user.email
			data['foto'] = settings.AVATARS_URL+qs.foto
			data['login'] = qs.user.username
			return JsonResponse(json.dumps(data), safe=False)
		except:
			return JsonResponse('false', safe=False)


class SettingsChangeData(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию которую необходимо 
	изменить у пользователя (login, email, avatar)
	"""

	def post(self, request):
		# Получаем данные о сессии 
		session_user = request.user.id
		session_user_name = request.user.username
		# Данные приходят в виде FormData, их них мы получаем картинку,
		# если она была изменена. Затем мы ее сохраняем в папку с аватарками
		try:
			try:
				name = session_user_name+'_'+re.findall(r'filename="([\s\S]*?)"', str(request.body))[0]
				data = (request.body.split(b"\r\n\r\n")[1])
				f = open(settings.STATIC_URL_IMG[0]+'/avatars/'+name, 'wb')
				f.write(data)
				profile = Profile.objects.get(user_id=session_user)
				profile.foto = name
				profile.save()
			# Если картинка не была изменена
			except:
				pass
			# Получаем login и email из формы и записываем их в базу
			login = re.findall(r'login"\\r\\n\\r\\n([\s\S]*?)\\r', str(request.body))[0]
			email = re.findall(r'email"\\r\\n\\r\\n([\s\S]*?)\\r', str(request.body))[0]
			user = User.objects.get(id=session_user)
			user.username = login
			user.email = email
			user.save()
			return JsonResponse('true', safe=False)
		except:
			return JsonResponse('false', safe=False)
