from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from hasker.settings.models import Profile


class RegistrationForm(UserCreationForm):
	"""
	Класс отрисовки формы регистрации
	"""
	email = forms.EmailField(required=True)
	photo = forms.ImageField()
	# Указываем модель и поля модели для отрисовки формы
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2", "photo")

	# Метод сохранения данных в бд
	def save(self, commit=True):
		user = super().save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class LoginForm(AuthenticationForm):
    """
    Класс отрисовки формы входа
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "password")