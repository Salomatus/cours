from django.urls import path
from . import views
from mailings.views import (
    MailingListView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    MailingDetailView,
    MailingDeactivateView,
)


app_name = "mailings"

urlpatterns = [
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/<int:pk>/update/",
        MailingUpdateView.as_view(),
        name="mailing_update",
    ),
    path(
        "mailings/<int:pk>/delete/",
        MailingDeleteView.as_view(),
        name="mailing_delete",
    ),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path(
        "mailings/<int:pk>/deactivate/",
        MailingDeactivateView.as_view(),
        name="mailing_deactivate",
    ),
    path("send_mailing/", views.send_mailing, name="send_mailing"),
]
