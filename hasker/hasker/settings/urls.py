from django.urls import include, re_path, path

from . import views


# Набор URL, отвечающих за перенаправление запросов на необходимые функции
# в app settings
urlpatterns = [
    path('', views.SettingsView.as_view(), name='settings'),
    path('get_settings/', views.SettingsViewData.as_view(), name='get_settings'),
    path('change_user_data/', views.SettingsChangeData.as_view(), name='change_settings'),  
      
]