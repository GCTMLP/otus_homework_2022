from django.urls import path, include
from . import views
from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers


router = routers.SimpleRouter()
router.register(r'questions', views.QuestionApi)
urlpatterns = router.urls



# Набор URL, отвечающих за перенаправление запросов на необходимые функции
# в app api
urlpatterns += [
    path('questions/search/', views.SearchQuestionApi.as_view()),
    re_path('^questions/answers/(?P<id>.+)/$', views.AnswersApi.as_view()),
 ]
