from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.db import transaction

from datetime import datetime
import json

from hasker.questions.models import Question, VotesQuestion
from hasker.answers.models import Answers
from hasker.settings.models import Profile


class IndexView(TemplateView):
	"""
	Показываем основной шаблон вопросов (шаблон изначально пустой,
	все данные подгружаются в него через vue.js ajax запросом)
	"""
	template_name = "question.html"
	

class QuestionsView(View):
	"""
	Класс обработки ajax запроса. Полученаем обо всех вопросах
	"""

	def post(self, request):
		try:
			# Необходимые данные из запроса (сессию и тело запроса)
			session_user = request.user.id
			request = json.loads(request.body)
			# Получаем номер страницы, кол-во элементов на странице и номер вопроса
			page = int(request['page'])
			limit = int(request['limit'])
			# Получаем общее число вопросов
			count = Question.objects.count()
			# Проверям, была ли введена информация в строку поиска
			# И получаем все данные ответов (вначале запрашиваем популярные)
			if request['search'] and request['search'][0] != '#':
				qs = Question.objects.filter(Q(question_header__contains=request['search']) 
					| Q(question_text__contains=request['search']))\
					.select_related('user')[(page-1)*limit:page*limit]
			# Срабатывает, если поиск осуществляется по тэгам
			elif request['search'] and request['search'][0] == '#':
				qs = Question.objects.filter(tags__contains=request['search'][1:])\
									.select_related('user')[(page-1)*limit:page*limit]
			else:
				qs = Question.objects.select_related('user')\
						.annotate(count=Count('votesquestion__id'))\
						.order_by('-count', '-pub_date')[(page-1)*limit:page*limit]
			# Рендерим данные вопросов и собираем их в "удобный" для шаблона вид 
			all_data = {}
			data = []
			for q in qs:
				one_q = {}
				one_q['question_header'] = q.question_header
				one_q['question_text'] = q.question_text
				one_q['pub_date'] = q.pub_date.strftime("%d/%m/%Y %H:%m")
				one_q['tags'] = q.tags.split()
				one_q['user_name'] = q.user.username
				one_q['id'] = q.id
				# Проверяем, голосовал ли пользователь за данный ответ
				if session_user:
					one_q['is_voted'] = VotesQuestion.objects.filter(user_id=int(session_user), question_id=int(q.id)).count()
				# Если не голосовал, то даем ему возможность проголосовать
				else:
					one_q['is_voted'] = False
				# Подсчет количества ответов на вопрос и голосов за данный вопрос
				one_q['count_votes'] = VotesQuestion.objects.filter(question_id=q.id).count()
				one_q['count_answers'] = Answers.objects.filter(question_id=q.id).count()
				# Создаем путь до фотографии пользователя, написавшего вопрос
				one_q['foto'] = settings.AVATARS_URL+'/'+Profile.objects.get(user_id=q.user.id).foto
				data.append(one_q)
			all_data['data'] = data
			all_data['count'] = count
			qs = json.dumps(all_data)
			
			return JsonResponse(qs, safe=False)
		except:
			return JsonResponse('false', safe=False)


class QuestionsPopularView(View):
	"""
	Класс обработки ajax запроса. Получаем информацию о наиболее
	популярных вопросах (по голосованию), 
	"""

	def post(self, request):
		try:
			return_top = []
			qs = Question.objects.select_related('user')\
						.annotate(count=Count('votesquestion__id'))\
						.order_by('-count', '-pub_date')[:20]
			# Получаем необходимую информацию о вопросе
			for question in qs:
				one_q = {}
				one_q['question_header'] = question.question_header
				one_q['id'] = question.id
				one_q['count_votes'] = int(VotesQuestion.objects\
									.filter(question_id=question.id).count())
				return_top.append(one_q)
			all_data = json.dumps(return_top)
			return JsonResponse(all_data, safe=False)
		except:
			return JsonResponse('false', safe=False)


class UserSession(View):
	"""
	Класс обработки ajax запроса. Получаем информацию о пользователе
	от имени которого создалась сессия (для отображения инфорамции 
	о пользователе в шапке)
	"""

	def post(self, request):
		try:
			all_data = {}
			if request.user.is_authenticated:
				session_user = request.user.username
				qs = User.objects.get(username=session_user)
				all_data['username'] = session_user
				all_data['email'] = qs.email
			else:
				session_user = False
			return JsonResponse(json.dumps(all_data), safe=False)
		except:
			return JsonResponse('false', safe=False)

class QuestionsSave(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию 
	о новом вопросе и записываем ее в бд (проверка тегов 
	происходит на стороне vue.js)
	"""

	def post(self, request):
		try:
			session_user = request.user.id
			request = json.loads(request.body)
			ins = Question(question_header=request['title'], 
									question_text=request['text'], 
									pub_date=datetime.now(), 
									tags=request['tags'],
									user_id=session_user)
			ins.save()
			id=ins.id
			return JsonResponse(id, safe=False)
		except:
			return JsonResponse('false', safe=False)

class PlusVote(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию 
	о том, за какой вопрос какой пользователь проголосовал 
	и записываем в бд данную информацию
	"""

	def post(self, request):
		try:
			session_user = request.user.id
			request_data = json.loads(request.body)	
			with transaction.atomic():
				VotesQuestion.objects.create(question_id=request_data['id'], 
									user_id=session_user)
			return JsonResponse('true', safe=False)
		except:
			return JsonResponse('false', safe=False)

class MinusVote(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию 
	о том, у которого ответа какой пользователь отменил свой голос 
	и записываем в бд данную информацию
	"""

	def post(self, request):
		try:
			session_user = request.user.id
			request_data = json.loads(request.body)
			with transaction.atomic():
				del_qs = VotesQuestion.objects.get(question_id=request_data['id'], 
									user_id=session_user)
				del_qs.delete()	
			return JsonResponse('true', safe=False)
		except:
			return JsonResponse('false', safe=False)
