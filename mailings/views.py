from pyexpat.errors import messages

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django_apscheduler.models import DjangoJob

import mailings.forms
import users.models
from mailings.models import Attempt, Client, Mailing, Message


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
    return render(request, "mailings/home.html", context)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "mailings/message_form.html"
    fields = ["subject", "body"]
    success_url = reverse_lazy("mailings:message_list")

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
    template_name = "mailings/message_form.html"
    fields = ["subject", "body"]
    success_url = reverse_lazy("mailings:message_list")

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
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Сообщение успешно удалено.")
        return super().delete(request, *args, **kwargs)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailings/message_detail.html"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailings/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['clients'].queryset = form.fields['clients'].queryset.filter(owner=self.request.user)
        return form


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = "mailings/client_form.html"
    form_class = mailings.forms.ClientsForm["email", "full_name", "comment"]
    success_url = reverse_lazy("mailings:client_list")

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
    template_name = "mailings/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("mailings:client_list")

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
    template_name = "mailings/client_confirm_delete.html"
    success_url = reverse_lazy("mailings:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Клиент успешно удален.")
        return super().delete(request, *args, **kwargs)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    template_name = "mailings/mailing_form.html"
    fields = ["start_time", "end_time", "status", "message", "clients"]
    success_url = reverse_lazy("mailings:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        mailing = form.save()

        # Планируем задачу schedule_mailing_wrapper
        start_time = mailing.start_time
        end_time = mailing.end_time

        DjangoJob.objects.create(
            name=f"mailing_task_{mailing.pk}",
            task="mailing.tasks.schedule_mailing_wrapper",
            args=[str(mailing.pk)],  # Передаем ID рассылки как строку
            next_run_time=start_time,
            end_datetime=end_time,
            replace_existing=True,
        )

        messages.success(self.request, "Рассылка успешно создана и запланирована.")
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    template_name = "mailings/mailing_form.html"
    fields = ["start_time", "end_time", "status", "message", "clients"]
    success_url = reverse_lazy("mailings:mailing_list")

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
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

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
            return redirect("mailings:mailing_list")

        mailing.status = "running"
        mailing.save()

        messages.success(request, f'Рассылка "{mailing.pk}" была запущена.')
        return redirect("mailings:mailing_list")


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class UserMailingsView(PermissionRequiredMixin, ListView):
    permission_required = "mailings.can_view_all_mailings"
    template_name = "mailings/user_mailings.html"
    context_object_name = "mailings"

    def dispatch(self, request, *args, **kwargs):
        self.target_user = get_object_or_404(users.models.CustomUser, pk=self.kwargs["user_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.target_user).select_related("message")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_user"] = self.target_user
        return context


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    permission_required = "users.view_user"
    model = users.models.CustomUser
    template_name = "mailings/user_list.html"
    context_object_name = "users"

    def test_func(self):
        return self.request.user.has_perm("users.can_view_all")

    def get_queryset(self):
        return users.models.CustomUser.objects.all()


class ToggleUserStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Контроллер для блокировки/разблокировки пользователей"""

    def test_func(self):
        return self.request.user.has_perm("users.can_block_user")

    def post(self, request, pk):
        user = get_object_or_404(users.models.CustomUser, pk=pk)
        user.is_blocked = not user.is_blocked
        user.save()

        action = "разблокирован" if not user.is_blocked else "заблокирован"
        messages.success(request, f"Пользователь {user.email} успешно {action}")

        return redirect("mailings:user_list")


class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "attempts/attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        return Attempt.objects.filter(mailing__owner=self.request.user)


@login_required
@permission_required("mailings.change_mailing")
def disable_mailing(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    mailing.is_active = False
    mailing.status = Mailing.COMPLETED
    mailing.save()
    return redirect("mailings:mailing_list")


class DisableMailingView(View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = False
        mailing.save()
        return redirect("mailings:mailing_list")


