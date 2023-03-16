from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Модель Профиля, которая дополняет стандартную модель пользователя
    из auth фотографией аватарки. Связан PK с таблицей User
    """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    foto = models.CharField(max_length=300)
