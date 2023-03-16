from rest_framework import viewsets

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
 
 
class CustomAuthToken(ObtainAuthToken):
    """
    Класс получения токена для аутентификации при вводе логина и пароля
    """
    authentication_classes = [authentication.BasicAuthentication]
    @swagger_auto_schema(responses={
        "201": openapi.Response(
            description = ("User has got Token"),
            schema=AuthTokenSerializer,
        )
    })
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        response201 = AuthTokenSerializer\
        				(data={"token": token.key, "user_id": user.pk})
        response201.is_valid(raise_exception=True)
        return JsonResponse(response201.data)

