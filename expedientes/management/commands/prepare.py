import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, CommandError, call_command
from django.db import connection, transaction

from expedientes.models import Area, DocumentType, User


class Command(BaseCommand):
    help = "Aplica migraciones e inicializa catálogos y la primera cuenta administradora."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_lock(%s)", [1729134105])
        try:
            call_command("migrate", interactive=False, verbosity=options["verbosity"])
            with transaction.atomic():
                self.initialize()
                if os.getenv("SEED_DEMO") == "1":
                    call_command("seed_demo")
        finally:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [1729134105])

    def initialize(self):
        for name in ("Mesa de Partes", "Secretaría General", "Gestión Ambiental", "Infraestructura"):
            Area.objects.get_or_create(name=name)
        for name in ("Solicitud", "Oficio", "Informe", "Acta", "Memorando"):
            DocumentType.objects.get_or_create(name=name)
        if User.objects.filter(role=User.Role.ADMIN, is_active=True).exists():
            return
        password = os.getenv("DEMO_PASSWORD") or os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
        if not password:
            raise CommandError("Configura DEMO_PASSWORD para crear la primera cuenta.")
        account = User(username="admin", first_name="Administración", role=User.Role.ADMIN)
        if User.objects.filter(username=account.username).exists():
            raise CommandError("El usuario inicial ya existe y requiere revisión del administrador.")
        try:
            if len(password) > 256:
                raise ValidationError("La contraseña admite hasta 256 caracteres.")
            validate_password(password, account)
        except ValidationError as error:
            raise CommandError("La contraseña inicial no cumple la política. " + " ".join(error.messages)) from None
        account.set_password(password)
        account.save()
        self.stdout.write("Cuenta administradora inicial creada.")
