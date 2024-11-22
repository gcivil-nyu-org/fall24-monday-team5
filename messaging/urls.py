from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.messaging_view, name='messaging'),
    path("add_friend/", views.add_friend, name="add_friend"),
    path('confirm_request/', views.confirm_request, name='confirm_request'),
    path('delete_friend/', views.delete_friend, name='delete_friend'),
    path('send_message/', views.send_message, name='send_message'),
]