from django import forms
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import redirect, render, get_object_or_404
from users.forms import Profile, RegisterForm
from users.models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, View


class RegisterView(CreateView):
    model = CustomUser
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy(
        "users:login"
    )  # Перенаправление на авторизацию после регистрации

    def form_valid(self, form):
        messages.success(
            self.request, "Вы успешно зарегистрировались. Пожалуйста, войдите."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка регистрации. Проверьте введенные данные.")
        return super().form_invalid(form)


class LoginView(LoginView):
    template_name = "users/login.html"
    success_url = reverse_lazy(
        "mailing:home"
    )  # Перенаправление домой после авторизации

    def get_success_url(self):
        return self.success_url


class LogoutView(LogoutView):
    next_page = reverse_lazy(
        "users:login"
    )  # Перенаправление на авторизацию после выхода



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("email", "avatar", "phone", "country")


class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "mailings/user_list.html"
    context_object_name = "users"


class ToggleUserStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Контроллер для блокировки/разблокировки пользователей"""

    def test_func(self):
        # Проверяем права на блокировку пользователей
        return self.request.user.has_perm("users.can_block_user")

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = not user.is_active
        user.save()

        action = "разблокирован" if user.is_active else "заблокирован"
        messages.success(request, f"Пользователь {user.email} успешно {action}")

        return redirect("messaging:user_list")

