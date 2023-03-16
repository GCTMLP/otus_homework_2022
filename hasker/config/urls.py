from django.urls import include, path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('settings/', include('hasker.settings.urls')),
    path('auth/', include('hasker.accounts.urls')),
    path('', include('hasker.questions.urls')),
    path('answers/', include('hasker.answers.urls')),
    path('api/', include('hasker.api.polls.urls')),
    path('api/api-token-auth/', CustomAuthToken.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

