from django.urls import include, re_path, path

from . import views


# Набор URL, отвечающих за перенаправление запросов на необходимые функции
# в app questions
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('get_all_questions/', views.QuestionsView.as_view(), name='all_questions'),
    path('get_popular_questions/', views.QuestionsPopularView.as_view(), name='popular_questions'),
    path('ask_question/', views.QuestionsSave.as_view(), name='ask_questions'),
    path('get_user_session_data/', views.UserSession.as_view(), name='user_session'),
    path('plus_vote/', views.PlusVote.as_view(), name='plus_vote'),
    path('minus_vote/', views.MinusVote.as_view(), name='minus_vote'),
]
