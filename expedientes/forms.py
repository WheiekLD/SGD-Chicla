from django import forms
from django.contrib.auth import password_validation

from .models import Area, DocumentType, Record, User


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150, widget=forms.TextInput(attrs={"autocomplete": "username", "autocapitalize": "none"}))
    password = forms.CharField(label="Contraseña", max_length=256, strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ["document_type", "channel", "subject", "sender", "area", "due"]
        labels = {
            "document_type": "Tipo de documento", "channel": "Canal de ingreso",
            "subject": "Asunto", "sender": "Remitente", "area": "Área sugerida",
            "due": "Fecha objetivo (opcional)",
        }
        widgets = {"due": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["document_type"].queryset = DocumentType.objects.filter(active=True)
        self.fields["area"].queryset = Area.objects.filter(active=True)


class MovementForm(forms.Form):
    assignee = forms.ModelChoiceField(label="Responsable de destino", queryset=User.objects.none())
    note = forms.CharField(label="Observación", max_length=300, required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if action == "derive":
            self.fields["assignee"].queryset = User.objects.filter(
                role=User.Role.AREA, is_active=True, area__active=True,
            ).select_related("area").order_by("area__name", "first_name", "username")
            self.fields["assignee"].label_from_instance = lambda user: f"{user.area} · {user.display_name}"
        else:
            del self.fields["assignee"]
        if action == "return":
            self.fields["note"].label = "Motivo de devolución"
            self.fields["note"].required = True


class AttachmentForm(forms.Form):
    pdf = forms.FileField(label="Archivo PDF", widget=forms.ClearableFileInput(attrs={"accept": ".pdf,application/pdf"}))


class AccountForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña", max_length=256, strip=False, required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "role", "area", "is_active"]
        labels = {
            "username": "Usuario", "first_name": "Nombre", "last_name": "Apellidos",
            "role": "Perfil", "area": "Área", "is_active": "Cuenta activa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["area"].queryset = Area.objects.filter(active=True)
        self.fields["password"].required = not self.instance.pk
        if self.instance.pk:
            self.fields["password"].help_text = "Déjala vacía para conservar la contraseña actual."

    def clean(self):
        data = super().clean()
        if data.get("role") == User.Role.AREA and not data.get("area"):
            self.add_error("area", "Selecciona el área del responsable.")
        if (data.get("is_active") and self.instance.pk and not data.get("password")
                and (not self.instance.password or not self.instance.has_usable_password())):
            self.add_error("password", "Define una contraseña antes de activar la cuenta.")
        if data.get("password"):
            for field in ("username", "first_name", "last_name"):
                setattr(self.instance, field, data.get(field, ""))
            try:
                password_validation.validate_password(data["password"], self.instance)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        if password := self.cleaned_data.get("password"):
            user.set_password(password)
        if commit:
            user.save()
        return user


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ["name"]
        labels = {"name": "Nombre del área"}


class TypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ["name"]
        labels = {"name": "Nombre del tipo documentario"}
