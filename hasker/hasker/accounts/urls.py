from django.urls import include, re_path, path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

# Набор URL, отвечающих за вход, выход и регистрицию в app accounts
urlpatterns = [
    path('login/', SignUp.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path("register/", Register.as_view(), name="register"),
    path('', views.SettingsView.as_view(), name='accounts'),
    path('get_settings/', views.SettingsViewData.as_view(), name='get_settings'),
    path('change_user_data/', views.SettingsChangeData.as_view(), name='change_settings'),  
]

from django.urls import include, re_path, path
from . import views


# Набор URL, отвечающих за перенаправление запросов на необходимые функции
# в app settings