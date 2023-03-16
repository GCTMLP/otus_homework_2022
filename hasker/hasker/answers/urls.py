from django.urls import include, re_path, path

from . import views


# Набор URL, отвечающих за перенаправление запросов на необходимые функции
# в app answers
urlpatterns = [
    path('', views.AnswersView.as_view(), name='answers'),
    path('get_all_answers/', views.AnswersViewData.as_view(), name='all_answers'),
    path('answer_question/', views.AnswersSave.as_view(), name='answer_questions'),
    path('plus_vote/', views.PlusVoteAnswer.as_view(), name='plus_vote_answer'),
    path('minus_vote/', views.MinusVoteAnswer.as_view(), name='minus_vote_answer'),
    path('correct_uncorrect/', views.CorrectUncorrectAnswer.as_view(), name='cor_uncor_answer'),
]