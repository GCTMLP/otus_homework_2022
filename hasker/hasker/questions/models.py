from django.db import models

class Question(models.Model):
	"""
	Модель вопросов (связана PK с пользователями, написавшими вопрос 
	"""
	question_header = models.CharField(max_length=500)
	question_text = models.CharField(max_length=5000)
	pub_date = models.DateTimeField(auto_now_add=True)
	tags = models.CharField(max_length=100)
	user = models.ForeignKey('auth.User', on_delete = models.CASCADE)

	# Происходит сортировка по дате при запросе данных из базы
	class Meta:
		ordering = ('-pub_date',)

class VotesQuestion(models.Model):
	"""
	Модель подсчета готлосов у вопроса (Связана PK с пользователем,
	проголосовавшим за вопрос и с вопросом, которому отдали голос)
	"""
	question = models.ForeignKey('Question', on_delete = models.CASCADE)
	user = models.ForeignKey('auth.User', on_delete = models.CASCADE)