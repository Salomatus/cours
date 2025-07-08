from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ("messages_subject", "messages_body")
    search_fields = ("messages_subject",)
