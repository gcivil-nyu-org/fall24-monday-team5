from django.urls import path
from . import views

app_name = "groups"

urlpatterns = [
    path("", views.group_list_view, name="group_list"),
    path("<int:group_id>/", views.group_detail_view, name="group_detail"),
    path("create/", views.create_group_view, name="create_group"),
    path("<int:group_id>/send_message/", views.send_group_message, name="send_message"),
    path("group/<int:group_id>/choose_users/", views.invite_users, name="invite_users"),
    path("group/<int:group_id>/invite/", views.send_invitation, name="send_invitation"),
    path("invitation/<int:invitation_id>/response/", views.respond_to_invitation, name="respond_to_invitation"),
    path("invitations/respond/<int:invitation_id>/", views.respond_to_invitation, name="respond_to_invitation"),
]
