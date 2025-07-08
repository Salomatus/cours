from django.urls import path

from . import views
from .views import MailingStatsView

app_name = "catalogs"

urlpatterns = [
    path("mailing_reports/", views.mailing_report, name="mailing_report"),
    path("stats/", MailingStatsView.as_view(), name="mailing_stat"),
]
