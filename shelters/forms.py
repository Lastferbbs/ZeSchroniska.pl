from django import forms
from django.template.loader import render_to_string
from django.core.mail import send_mail


class ContactPageForm(forms.Form):
    name = forms.CharField(
        label="Imię",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Email",
        max_length=100,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    message = forms.CharField(
        label="Wiadomość", widget=forms.Textarea(attrs={"class": "form-control"})
    )

    def send_email(self):
        form = self
        html = render_to_string(
            "shelters/contact_message.html",
            {
                "name": form.cleaned_data["name"],
                "email": form.cleaned_data["email"],
                "message": form.cleaned_data["message"],
            },
        )

        send_mail(
            "Wiadomość z formularza kontaktowego",
            "This is the message body",
            "blablabla@gmail.com",
            ["0xferbx@gmail.com"],
            html_message=html,
        )
