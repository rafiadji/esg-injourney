from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_activity_list, name='user-activity-list'),
]