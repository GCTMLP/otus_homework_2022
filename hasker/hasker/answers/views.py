from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction
from django.core import serializers
from django.core.mail import send_mail

from datetime import datetime
import json

from hasker.answers.models import Answers, VotesAnswers
from hasker.questions.models import Question
from hasker.settings.models import Profile

class AnswersView(TemplateView):
	"""
	Показываем основной шаблон ответов (шаблон изначально пустой,
	все данные подгружаются в него через vue.js ajax запросом)
	"""
	template_name = "answers.html"

class AnswersViewData(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию о конкретном 
	вопросе и обо всех ответах на него
	"""
	def post(self, request):
		# Необходимые данные из запроса (сессию и тело запроса)
		session_user = request.user.id
		request = json.loads(request.body)
		# Получаем номер страницы, кол-во элементов на странице и номер вопроса
		page = int(request['page'])
		limit = int(request['limit'])
		question = int(request['q_num'])
		# Проверям, была ли введена информация в строку поиска
		# И получаем все данные ответов
		if request['search']:
			qa = Answers.objects.filter(Q(question_id=int(question)) & 
										Q(answer_text__contains=request['search']))\
										.select_related('user')\
										.select_related('question')[(page-1)*limit:page*limit]
		else:
			qa = Answers.objects.filter(question_id=int(question))\
								.select_related('user')\
								.select_related('question')[(page-1)*limit:page*limit]
		count = Answers.objects.filter(question_id=int(question)).count()
		# Получаем данные о том, за какие ответы голосовал пользователь, 
		# от чьего имени данная сессия
		if session_user:
			qs_vote = VotesAnswers.objects.filter(user_id=int(session_user))
		all_data = {}
		data = []
		# Рендерим данные ответов и собираем их в "удобный" для шаблона вид 
		for q in qa:
			one_a = {}
			one_a['text'] = q.answer_text
			one_a['pub_date'] = q.pub_date.strftime("%m/%d/%Y %H:%m")
			one_a['user_name'] = q.user.username
			one_a['is_correct'] = q.is_correct
			one_a['id'] = q.id
			# Создаем путь до фотографии пользователя, написавшего вопрос
			one_a['foto'] = settings.AVATARS_URL+'/'+\
							Profile.objects.get(user_id=q.user.id).foto
			# Проверяем, голосовал ли пользователь за данный ответ
			if session_user:
				one_a['is_voted'] = VotesAnswers.objects\
									.filter(answer=q.id,\
									user_id=int(session_user)).count()
			# Если не голосовал, то даем ему возможность проголосовать
			else:
				one_a['is_voted'] = 1
			# Подсчитываем общее число голосов за данный ответ
			one_a['count_votes'] = VotesAnswers.objects.filter(answer=q.id).count()
			data.append(one_a)

		# Получаем данные о вопросе, на который были даны ответы 
		question_data = Question.objects\
						.filter(id=question).select_related('user')
		one_q = {}
		one_q['question_header'] = question_data[0].question_header
		one_q['question_text'] = question_data[0].question_text
		one_q['pub_date'] = question_data[0].pub_date\
							.strftime("%m/%d/%Y %H:%m")
		one_q['tags'] = question_data[0].tags.split()
		one_q['user_name'] = question_data[0].user.username
		one_q['id'] = question_data[0].id
		# Создаем путь до фотографии пользователя, написавшего ответ
		one_q['foto'] = settings.AVATARS_URL+'/'+\
						Profile.objects.get(user_id=question_data[0].user.id).foto
		all_data['question'] =  [one_q]
		all_data['data'] = data
		all_data['count'] = count
		# Проверям, данная сессия от создателя вопроса или нет 
		# (это делается для того, чтобы дать возможность создателю)
		# вопроса отметить ответ как "правильный"
		if question_data[0].user.id == session_user:
			all_data['make_true_answer'] = True
		else:
			all_data['make_true_answer'] = False
		return_data = json.dumps(all_data)
		return JsonResponse(return_data, safe=False)


class PlusVoteAnswer(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию 
	о том, за какой ответ какой пользователь проголосовал 
	и записываем в бд данную информацию
	"""

	def post(self, request):
		try:
			session_user = request.user.id
			request_data = json.loads(request.body)
			with transaction.atomic():
				VotesAnswers.objects.create(answer_id=request_data['id'], 
									user_id=session_user)
			return JsonResponse('true', safe=False)
		except:
			return JsonResponse('false', safe=False)

class MinusVoteAnswer(View):
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
				del_qs = VotesAnswers.objects.get(answer_id=request_data['id'], 
									user_id=session_user)
				del_qs.delete()	
			return JsonResponse('true', safe=False)
		except:
			return JsonResponse('false', safe=False)

class AnswersSave(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию 
	о новом ответе на вопрос и уведомляем создателя вопроса по почте
	о том, что на его вопрос появился ответ 
	"""

	def post(self, request):
		try:
			# Получаем ссылку на вопрос
			link = request.META['HTTP_REFERER']
			# Получаем данные нового ответа
			session_user = request.user.id
			request = json.loads(request.body)
			# Создаем запись в бд с параметрами нового ответа
			Answers.objects.create(answer_text=request['text'], 
									pub_date=datetime.now(),
									question_id=request['q_id'],
									user_id=session_user)
			# получаем данные о вопросе, на который пришел ответ для того,
			# чтобы понимать, кому и какой email отправлять
			question_data = Question.objects.filter(id=request['q_id'])\
							.select_related('user')[0]
			# Вызываем встроенную функцию отправки email
			send_mail('Hasker', f'You have new answer on question, \
					"{question_data.question_header}". \n link: {link}',\
					 settings.EMAIL_HOST,[question_data.user.email],\
					 fail_silently=False)
			return JsonResponse('true', safe=False)
		except:
			return JsonResponse('false', safe=False)


class CorrectUncorrectAnswer(View):
	"""
	Класс обработки ajax запроса. Полученаем инфорацию 
	о том, какой ответ создатель вопроса отметил как правильный
	"""

	def post(self, request):
		request = json.loads(request.body)
		# Проверяем, какой запрос к нам пришел:
		# пометить ответ как правильный или же отменить данный выбор
		if request['func'] == 'uncorrect':
			# Отменяем "правильность" ответа
			change_answer = Answers.objects.get(id=request['id_a'])
			change_answer.is_correct = 0
			change_answer.save()
			return JsonResponse('true', safe=False)
		elif request['func'] == 'correct':
			# Конструкция try срабатывает если какой то ответ был отмечен 
			# как правильный, пользователь в качестве правильного выбрал другой
			# и данный ответ (который в прошлом был правильный) необходимо отенить
			# его "правильность"
			try:
				change_answer_f = Answers.objects.select_related('question')\
									.get(question_id=request['id_q'], is_correct=1)
				change_answer_f.is_correct = 0
				change_answer_f.save()
			# Срабатывает, если никакой ответ не был помечен как правильный
			except:
				pass
			# помечаем выбранный ответ как правильный
			change_answer_t = Answers.objects.get(id=request['id_a'])
			change_answer_t.is_correct = 1
			change_answer_t.save()
			return JsonResponse('true', safe=False)
		# Если пришел некорректый запрос
		else:
			return JsonResponse('false', safe=False)
