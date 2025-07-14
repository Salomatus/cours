from django.urls import path
from mailings.views import (ClientCreateView, ClientDeleteView, ClientListView,
                           ClientUpdateView, MailingCreateView,
                           MailingDeleteView, MailingListView,
                           MailingUpdateView, MessageCreateView,
                           MessageDeleteView, MessageListView,
                           MessageUpdateView, StartMailingView, home,
                           mailing_reports)

app_name = "mailing"


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
    path("reports/", mailing_reports, name="mailing_reports"),
]
