from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_rate_exchange_api, name='get_rate_exchange_api'),
]
