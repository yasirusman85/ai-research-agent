from django.urls import path
from . import views

urlpatterns = [
    path('chat', views.chat_agent, name='chat'),
    path('human-feedback', views.human_feedback, name='human_feedback'),
    path('stream', views.stream_agent, name='stream'),
]
