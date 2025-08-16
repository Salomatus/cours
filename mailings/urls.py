from django.urls import path

from .views import (AttemptListView, ClientCreateView, ClientDeleteView,
                    ClientListView, ClientUpdateView, MailingCreateView,
                    MailingDeleteView, MailingDetailView, MailingListView,
                    MailingUpdateView, MessageCreateView, MessageDeleteView,
                    MessageDetailView, MessageListView, MessageUpdateView,
                    StartMailingView, ToggleUserStatusView, UserListView,
                    UserMailingsView, home)

app_name = "mailings"


urlpatterns = [
    path("", home, name="home"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/update/<int:pk>/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "messages/delete/<int:pk>/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/update/<int:pk>/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/delete/<int:pk>/", ClientDeleteView.as_view(), name="client_delete"),
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/update/<int:pk>/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailings/delete/<int:pk>/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path("mailings/start/<int:pk>/", StartMailingView.as_view(), name="start_mailing"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("attempts/", AttemptListView.as_view(), name="attempt_list"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("mailings/", UserMailingsView.as_view(), name="user_mailings"),
    path("users/<int:pk>/toggle/", ToggleUserStatusView.as_view(), name="toggle_user"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),

]
