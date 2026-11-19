from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from pypdf import PdfWriter

from .models import Area, Attachment, AuditEvent, DocumentType, Record, StorageQuota

User = get_user_model()


class DemoBootstrapTests(TestCase):
    def test_shared_secret_creates_accounts_and_preserves_later_changes(self):
        with patch.dict("os.environ", {"DEMO_PASSWORD": "Bosque-Reloj-734-Lab", "SEED_DEMO": "1"}):
            call_command("prepare", verbosity=0)

        accounts = {account.username: account for account in User.objects.all()}
        self.assertEqual(
            {name: account.role for name, account in accounts.items()},
            {"admin": User.Role.ADMIN, "mesa": User.Role.OFFICE, "elena": User.Role.AREA, "marco": User.Role.AREA},
        )
        for account in accounts.values():
            self.assertTrue(account.is_active)
            self.assertTrue(account.check_password("Bosque-Reloj-734-Lab"))
        self.assertEqual(len({account.password for account in accounts.values()}), 4)

        account = accounts["mesa"]
        account.set_password("Montana-Ruta-734-Lab")
        account.is_active = False
        account.save()
        with patch.dict("os.environ", {"DEMO_PASSWORD": "Otra-Frase-734-Lab", "SEED_DEMO": "1"}):
            call_command("prepare", verbosity=0)
        account.refresh_from_db()
        self.assertFalse(account.is_active)
        self.assertTrue(account.check_password("Montana-Ruta-734-Lab"))
        self.assertEqual(Record.objects.count(), 3)


@override_settings(DEBUG=False, STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class WorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.area = Area.objects.create(name="Gestión Ambiental")
        cls.other_area = Area.objects.create(name="Infraestructura")
        cls.kind = DocumentType.objects.create(name="Solicitud")
        cls.password = "Abedul-Cauce-Prototipo-734"
        cls.admin = User.objects.create_user("admin", password=cls.password, role=User.Role.ADMIN)
        cls.office = User.objects.create_user("mesa", password=cls.password, role=User.Role.OFFICE)
        cls.recipient = User.objects.create_user("elena", password=cls.password, role=User.Role.AREA, area=cls.area)
        cls.other = User.objects.create_user("marco", password=cls.password, role=User.Role.AREA, area=cls.other_area)

    def client_as(self, user):
        client = Client()
        client.force_login(user)
        return client

    def create_record(self, client, subject="Solicitud de limpieza"):
        response = client.post(reverse("new_record"), {
            "subject": subject, "sender": "Remitente ficticio",
            "document_type": self.kind.pk, "channel": "desk",
        })
        item = Record.objects.get(subject=subject)
        self.assertRedirects(response, reverse("record", args=[item.pk]))
        return item

    def change(self, client, item, action, **data):
        return client.post(reverse("transition", args=[item.pk, action]), data)

    def test_complete_custody_flow_and_private_pdf(self):
        office = self.client_as(self.office)
        recipient = self.client_as(self.recipient)
        outsider = self.client_as(self.other)
        item = self.create_record(office)
        self.assertContains(office.get(reverse("receipt", args=[item.pk])), item.code)
        self.assertEqual(self.change(office, item, "derive", assignee=self.recipient.pk).status_code, 302)
        self.assertEqual(outsider.get(reverse("record", args=[item.pk])).status_code, 404)
        self.assertEqual(self.change(recipient, item, "receive").status_code, 302)
        self.assertContains(self.change(recipient, item, "return", note=" "), "Motivo de devolución")
        self.assertEqual(self.change(recipient, item, "return", note="Área incorrecta").status_code, 302)
        self.assertEqual(self.change(office, item, "derive", assignee=self.recipient.pk).status_code, 302)
        self.assertEqual(self.change(recipient, item, "receive").status_code, 302)

        upload = reverse("upload", args=[item.pk])
        invalid = SimpleUploadedFile("texto.txt", b"contenido de prueba")
        self.assertContains(recipient.post(upload, {"pdf": invalid}), "Selecciona un archivo PDF válido.", status_code=400)
        pdf = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(pdf)
        valid = SimpleUploadedFile("ejemplo.pdf", pdf.getvalue(), content_type="application/pdf")
        self.assertEqual(recipient.post(upload, {"pdf": valid}).status_code, 302)
        attachment = Attachment.objects.get(record=item)
        self.assertEqual(StorageQuota.objects.get(pk=1).used, len(pdf.getvalue()))
        download = reverse("download", args=[attachment.pk])
        self.assertEqual(outsider.get(download).status_code, 404)
        response = recipient.get(download)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), pdf.getvalue())
        self.assertEqual(self.change(recipient, item, "finish").status_code, 302)
        self.assertEqual(self.change(office, item, "archive").status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.state, Record.State.ARCHIVED)
        self.assertContains(office.get(reverse("archive")), item.code)
        self.assertContains(office.get(reverse("inbox")), "No hay expedientes")
        self.assertContains(self.client_as(self.admin).get(reverse("audit")), "Expediente archivado")
        self.assertEqual(item.movements.count(), 9)

    def test_login_logout_and_audit(self):
        client = Client()
        client.post(reverse("login"), {"username": self.office.username, "password": "incorrecta"})
        self.assertTrue(AuditEvent.objects.filter(action="Inicio de sesión", outcome="Rechazado").exists())
        response = client.post(reverse("login"), {"username": self.office.username, "password": self.password})
        self.assertRedirects(response, reverse("inbox"))
        session_key = client.session.session_key
        self.assertEqual(client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(client.post(reverse("logout")), reverse("login"))
        self.assertFalse(Session.objects.filter(session_key=session_key).exists())
        self.assertEqual(client.get(reverse("inbox")).status_code, 302)
        self.assertTrue(self.office.password.startswith("pbkdf2_sha256$"))

    @override_settings(SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
    def test_https_cookie_properties(self):
        client = Client()
        response = client.post(
            reverse("login"), {"username": self.office.username, "password": self.password}, secure=True,
        )
        cookie = response.cookies["chicla_session"]
        self.assertTrue(cookie["secure"])
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")

    def test_inactivity_and_privileged_routes(self):
        client = self.client_as(self.office)
        self.assertEqual(client.get(reverse("accounts")).status_code, 403)
        session = client.session
        session["last_seen"] = int((timezone.now() - timedelta(minutes=6)).timestamp())
        session.save()
        self.assertEqual(client.get(reverse("inbox")).status_code, 302)
        self.assertTrue(AuditEvent.objects.filter(action="Sesión caducada").exists())

    def test_form_validation_search_and_csrf(self):
        admin = self.client_as(self.admin)
        response = admin.post(reverse("new_account"), {
            "username": "nueva", "password": "corta", "role": "office", "is_active": "on",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="nueva").exists())
        self.assertEqual(admin.post(reverse("new_record"), {"subject": " "}).status_code, 200)
        self.assertFalse(Record.objects.exists())
        item = self.create_record(admin)
        self.assertContains(admin.get(reverse("inbox"), {"q": item.code}), item.subject)
        self.assertContains(admin.get(reverse("inbox"), {"q": "texto inexistente"}), "No hay expedientes")
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.office)
        self.assertEqual(strict.post(reverse("new_record"), {}).status_code, 403)

    def test_generic_server_error(self):
        client = Client(raise_request_exception=False)
        client.force_login(self.office)
        with patch("expedientes.views.accessible_records", side_effect=RuntimeError("mensaje interno simulado")):
            response = client.get(reverse("inbox"))
        self.assertContains(response, "No se pudo completar la solicitud", status_code=500)
        self.assertNotContains(response, "mensaje interno simulado", status_code=500)

    def test_initial_demo_accounts_can_only_be_activated_with_password(self):
        admin = self.client_as(self.admin)
        new_user = User.objects.create_user("sincredencial", role=User.Role.OFFICE, is_active=False)
        url = reverse("edit_account", args=[new_user.pk])
        form = {"username": new_user.username, "role": "office", "is_active": "on"}
        response = admin.post(url, form)
        self.assertContains(response, "Define una contraseña antes de activar la cuenta.")
        new_user.refresh_from_db()
        self.assertFalse(new_user.is_active)
        self.assertRedirects(admin.post(url, {**form, "password": self.password}), reverse("accounts"))
        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)
        self.assertTrue(new_user.check_password(self.password))
