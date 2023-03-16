from rest_framework import serializers

# Сериалайзер для получения токенов
class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, allow_blank=False)
    user_id = serializers.IntegerField(required=True)