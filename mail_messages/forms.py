from django import forms

from .models import Message


class MessagesForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["messages_subject", "messages_body"]
