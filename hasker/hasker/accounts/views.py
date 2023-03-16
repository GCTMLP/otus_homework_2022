from django.shortcuts import  render, redirect
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic import TemplateView, View, CreateView
from django.http import HttpResponse
from django.core import serializers
from django.http import JsonResponse
from django.db import models
from django.conf import settings
from django.contrib.auth.views import LoginView

import json
import re

from .forms import RegistrationForm, LoginForm
from hasker.settings.models import Profile


class Register(CreateView):
	"""
	Функция валидации формы регистрации
	"""
	form_class = forms.NewUserForm
	template_name = 'register.html'
	success_url = "/"
	
	def form_valid(self, form):
		res = super().form_valid(form)
		user = form.save()
		if user:
			file_name = form.cleaned_data['username'] +'_'+ self.request.FILES['foto'].name 
			# Проходим процедуру сохранения фотографии 
			# (в отдельной таблице хранится путь до фото у конкретного пользователя)
			last_user = User.objects.filter(username=form.cleaned_data['username'])
			Profile.objects.create(photo=file_name, 
								user_id=last_user.id)
			# Вызывае функцию сохранения файла
			handle_uploaded_file(self.request.FILES['foto'].file, file_name)
			# Залогиниваемся от вновь зарегистрированного пользователя 
			# и перенаправлеям его на страницу вопросов
			login(self.request, user)
		return res


class SignUp(LoginView):
	 """
    Функция валидации формы входа
    """
    form_class = forms.LoginForm
    template_name = 'login.html'
    success_url = "/"

    def form_valid(self, form):
        res = super().form_valid(form)
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(self.request, user)
        return res


def handle_uploaded_file(f, save_name):
	"""
	Функция сохранения аватарки при регистрации  
	"""
	f.seek(0)
	file = open(settings.AVATARS_URL+'/'+save_name, 'wb') 
	file.write(f.read())


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
