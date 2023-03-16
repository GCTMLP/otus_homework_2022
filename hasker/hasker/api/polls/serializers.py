from rest_framework import serializers

from hasker.questions.models import Question
from hasker.answers.models import Answers


# Сериалайзер для получения index 
class QuestionSerializer(serializers.ModelSerializer):
	votes_count = serializers.IntegerField()
	answer_count = serializers.IntegerField()
	class Meta:
		model = Question
		fields = (	'id',
					'question_header', 
        			'question_text', 
        			'pub_date', 
        			'tags', 
        			'user',
        			'votes_count',
        			'answer_count')


# Сериалайзер для получения конкретного вопроса по id
class OneQuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Question
		fields = (	'id',
					'question_header', 
        			'question_text', 
        			'pub_date', 
        			'tags', 
        			'user')


# Сериалайзер для получения ответов к конкретному вопросу
class AnswersSerializer(serializers.ModelSerializer):
	votes_count = serializers.IntegerField()
	class Meta:
		model = Answers
		fields = (	'id',
        			'answer_text', 
        			'pub_date', 
        			'user',
        			'votes_count')


# Сериалайзер для получения токенов
class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, allow_blank=False)
    user_id = serializers.IntegerField(required=True)