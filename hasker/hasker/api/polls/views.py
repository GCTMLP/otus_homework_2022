from rest_framework import viewsets

from .serializers import QuestionSerializer, AnswersSerializer, OneQuestionSerializer
from hasker.questions.models import Question, VotesQuestion
from hasker.answers.models import Answers, VotesAnswers
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import authentication, viewsets, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .serializers import QuestionSerializer
from hasker.api.polls.serializers import AuthTokenSerializer
from django.db.models import Q, Count
from django.core import serializers 
from rest_framework import viewsets
 
class StandardResultsSetPagination(PageNumberPagination):
    """
    Класс, который задает пагинацию на странице
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class QuestionApi(viewsets.ModelViewSet):
	"""
	Класс для получения данных index (все вопросы)
	"""
	serializer_class=QuestionSerializer
	pagination_class = StandardResultsSetPagination
	permission_classes=[IsAuthenticated]

	queryset = Question.objects\
						.annotate(votes_count=Count('votesquestion__id', distinct=True))\
						.annotate(answer_count=Count('answers__id', distinct=True))\
						.order_by('-votes_count', '-pub_date')


class AnswersApi(generics.ListAPIView):
	"""
	Класс для получения данных ответов на конкретный вопрос
	"""
	serializer_class = AnswersSerializer
	pagination_class = StandardResultsSetPagination

	def get_queryset(self):
		question_id = self.kwargs['id']
		return Answers.objects.filter(question_id=question_id)\
		.annotate(votes_count=Count('votesanswers__id', distinct=True))\
		.order_by('-votes_count', '-pub_date')


class SearchQuestionApi(generics.ListCreateAPIView):
	"""
	Класс для получения данных о вопросых по поисковой строке
	"""
	serializer_class=QuestionSerializer
	pagination_class = StandardResultsSetPagination

	def post(self, request):
		
		search = request.data.get('search')
		questions_search =  Question.objects\
						.annotate(votes_count=Count('votesquestion__id', distinct=True))\
						.annotate(answer_count=Count('answers__id', distinct=True))\
						.order_by('-votes_count', '-pub_date')\
						.filter(Q(question_header__contains=search) 
						| Q(question_text__contains=search))
		return JsonResponse(serializers.serialize('json', list(questions_search)), safe=False)
