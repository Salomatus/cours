from pyexpat.errors import messages

from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django_apscheduler.models import DjangoJob
from mailings.models import Client, Mailing, MailingAttempt, Message


@cache_page(60 * 15)  # Кешируем на 15 минут
@login_required
def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status="running").count()
    unique_clients = Client.objects.values("email").distinct().count()
    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_clients": unique_clients,
    }
    return render(request, "mailing/home.html", context)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ["subject", "body"]
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Сообщение успешно создано.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Ошибка создания сообщения. Проверьте введенные данные."
        )
        return super().form_invalid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ["subject", "body"]
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Сообщение успешно обновлено.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Ошибка обновления сообщения. Проверьте введенные данные."
        )
        return super().form_invalid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Сообщение успешно удалено.")
        return super().delete(request, *args, **kwargs)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = "mailing/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Клиент успешно создан.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Ошибка создания клиента. Проверьте введенные данные."
        )
        return super().form_invalid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = "mailing/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Клиент успешно обновлен.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Ошибка обновления клиента. Проверьте введенные данные."
        )
        return super().form_invalid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Клиент успешно удален.")
        return super().delete(request, *args, **kwargs)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    template_name = "mailing/mailing_form.html"
    fields = ["start_time", "end_time", "status", "message", "clients"]
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        mailing = form.save()

        # Планируем задачу schedule_mailing_wrapper
        start_time = mailing.start_time
        end_time = mailing.end_time

        DjangoJob.objects.create(
            name=f"mailing_task_{mailing.pk}",
            task="mailing.tasks.schedule_mailing_wrapper",  # Corrected task path
            args=[str(mailing.pk)],  # Передаем ID рассылки как строку
            next_run_time=start_time,
            end_datetime=end_time,
            replace_existing=True,
        )

        messages.success(self.request, "Рассылка успешно создана и запланирована.")
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    template_name = "mailing/mailing_form.html"
    fields = ["start_time", "end_time", "status", "message", "clients"]
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Рассылка успешно обновлена.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Ошибка обновления рассылки. Проверьте введенные данные."
        )
        return super().form_invalid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Рассылка успешно удалена.")
        return super().delete(request, *args, **kwargs)


class StartMailingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

        # Запускаем задачу Celery асинхронно
        # send_mailing_task.delay(mailing.pk) больше не нужно, так как рассылка планируется
        # schedule_mailing_wrapper.delay(mailing.pk)
        if mailing.start_time <= timezone.now():
            messages.error(
                request, "Нельзя запустить рассылку, дата начала которой уже прошла"
            )
            return redirect("mailing:mailing_list")

        mailing.status = "running"
        mailing.save()

        messages.success(request, f'Рассылка "{mailing.pk}" была запущена.')
        return redirect("mailing:mailing_list")


@login_required
def mailing_reports(request):
    """
    Отображает отчеты о попытках рассылки для текущего пользователя.
    """

    # Fetch mailings owned by the current user
    mailings = Mailing.objects.filter(owner=request.user)

    # Fetch attempt statistics for those mailings
    mailing_attempts = (
        MailingAttempt.objects.filter(mailing__in=mailings)
        .values("mailing")
        .annotate(
            total_attempts=Count("mailing"),
            successful_attempts=Count("mailing", filter=models.Q(status="success")),
            failed_attempts=Count("mailing", filter=models.Q(status="failure")),
        )
    )

    # Подготовьте словарь для учета количества попыток для каждой рассылки
    mailing_stats = {attempt["mailing"]: attempt for attempt in mailing_attempts}

    # Передача данных в шаблон
    context = {
        "mailings": mailings,
        "mailing_stats": mailing_stats,
    }
    return render(request, "mailing/mailing_reports.html", context)
