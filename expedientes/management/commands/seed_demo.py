import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, CommandError
from django.db import transaction

from expedientes.models import Area, DocumentType, Movement, Record, User


class Command(BaseCommand):
    help = "Carga ejemplos sintéticos para una instalación ya inicializada."

    @transaction.atomic
    def handle(self, *args, **options):
        password = os.getenv("DEMO_PASSWORD")
        accounts = [
            ("mesa", "Mesa de Partes", User.Role.OFFICE, "Mesa de Partes"),
            ("elena", "Elena Torres", User.Role.AREA, "Gestión Ambiental"),
            ("marco", "Marco Díaz", User.Role.AREA, "Infraestructura"),
        ]
        users = {}
        for username, name, role, area in accounts:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": name, "role": role, "area": Area.objects.get(name=area), "is_active": False},
            )
            if created and password:
                try:
                    if len(password) > 256:
                        raise ValidationError("La contraseña admite hasta 256 caracteres.")
                    validate_password(password, user)
                except ValidationError as error:
                    raise CommandError(
                        f"DEMO_PASSWORD no cumple la política para {username}. " + " ".join(error.messages)
                    ) from None
                user.set_password(password)
                user.is_active = True
                user.save(update_fields=["password", "is_active"])
            elif created or (not user.is_active and not user.password):
                user.set_unusable_password()
                user.save(update_fields=["password"])
            users[username] = user
        kind = DocumentType.objects.get(name="Solicitud")
        examples = [
            ("Jornada de limpieza de espacios públicos", "elena", Record.State.PENDING),
            ("Mantenimiento de vía vecinal", "marco", Record.State.PENDING),
            ("Solicitud de información pública", None, Record.State.REGISTERED),
        ]
        for subject, username, state in examples:
            assignee = users.get(username)
            item, created = Record.objects.get_or_create(
                subject=subject, creator=users["mesa"], sender="Remitente sintético",
                defaults={"document_type": kind, "channel": Record.Channel.DESK, "assignee": assignee,
                          "area": assignee.area if assignee else None, "state": state},
            )
            if created:
                Movement.objects.create(record=item, actor=users["mesa"], title="Expediente registrado")
                if assignee:
                    Movement.objects.create(record=item, actor=users["mesa"], title="Expediente derivado", destination=str(assignee.area))
        self.stdout.write("Datos iniciales preparados.")
