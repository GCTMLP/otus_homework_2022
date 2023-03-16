from django.db import models

from hasker.questions.models import Question


class Answers(models.Model):
	"""
	Модель ответов (связана PK с пользователями, написавшими ответ 
	и с вопросами, на которые дан был ответ)
	"""
	question = models.ForeignKey('questions.Question', on_delete = models.CASCADE)
	answer_text = models.CharField(max_length=5000)
	pub_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('auth.User', on_delete = models.CASCADE)
	is_correct = models.BooleanField(default=False)

	# Происходит сортировка по дате при запросе данных из базы
	class Meta:
		ordering = ('-pub_date',)


class VotesAnswers(models.Model):
	"""
	Модель подсчета готлосов у ответа (Связана PK с пользователем,
	проголосовавшим за ответ и с ответом, которому отдали голос)
	"""
	answer = models.ForeignKey('Answers', on_delete = models.CASCADE)
	user = models.ForeignKey('auth.User', on_delete = models.CASCADE)