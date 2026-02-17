from django import forms
from django.forms import BooleanField
from mailings.models import Client, Mailing, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = [
            "message",
            "clients",
            "start_time",
            "end_time",
            "owner",
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ClientsForm(forms.ModelForm):
    class Meta:
        model = Client
        form_class = ["email", "full_name", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Введите дополнительную информацию"}
            ),
        }
        help_texts = {"comment": "Введите дополнительную информацию о получателе"}

    def clean(self):
        cleaned_data = super(ClientsForm, self).clean()
        email = cleaned_data.get("email")
        full_name = cleaned_data.get("full_name")

        if not email:
            raise forms.ValidationError("Поле Email обязательно для заполнения")
        if not full_name:
            raise forms.ValidationError("Поле ФИО обязательно для заполнения")

        if email:
            owner = self.instance.owner if self.instance.pk else None
            if (
                owner is not None
                and Client.objects.filter(email=email, owner=owner).exists()
            ):
                raise forms.ValidationError(
                    "Этот email уже используется другим получателем"
                )

        return cleaned_data


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        form_class = ["messages_subject", "messages_body"]


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_custom_help_texts()
        self.apply_styling()
        self.clean_widget_attrs()

    def set_custom_help_texts(self):
        """Установление кастомных подсказок для полей"""
        password_help_texts = {
            'password1': 'Придумайте пароль, содержащий не менее 8 символов',
            'password2': 'Введите пароль еще раз'
        }
        for field_name, help_text in password_help_texts.items():
            if field_name in self.field:
                self.field[field_name].help_text = help_text

    def apply_styling(self, DateTimeLocalInput=None):
        """Применение стилизации ко всем полям"""

        for field_name, field in self.field.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

            if field.help_text:
                field.widget.attrs['placeholder'] = field.help_text
                field.widget.attrs['data-help'] = field.help_text
                field.help_text = ''

            if isinstance(field, forms.Textarea):
                field.widget.attrs.update({
                    'rows': 8,
                    'class': 'form-control message-textarea'
                })
            elif isinstance(field, forms.DateTimeField):
                field.widget = DateTimeLocalInput()
                field.widget.attrs.update({
                    'class': 'form-control datetimepicker',
                    'autocomplete': 'off'
                })

    def clean_widget_attrs(self):
        """Очистка всех нежелательных атрибутов виджета"""
        attrs_to_remove = [
            'aria-describedby',
            'data-toggle',
            'data-placement',
            'title',
            'data-original-title'
        ]

        for field in self.field.values():
            for attr in attrs_to_remove:
                field.widget.attrs.pop(attr, None)
