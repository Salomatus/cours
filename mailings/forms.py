from django import forms

from mailings.models import Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = [
            "name",
            "message",
            "clients",
            "start_date_time",
            "end_date_time",
            "status",
        ]
        widgets = {
            "start_date_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
