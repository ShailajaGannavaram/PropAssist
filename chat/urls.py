from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('chat/stream/', views.chat_stream, name='chat_stream'),
    path('history/<str:session_id>/', views.get_history, name='get_history'),
]