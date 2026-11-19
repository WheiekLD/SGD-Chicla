import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Area(models.Model):
    name = models.CharField("área", max_length=90, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        OFFICE = "office", "Mesa de Partes"
        AREA = "area", "Responsable de área"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.OFFICE)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, null=True, blank=True)

    @property
    def display_name(self):
        return self.get_full_name() or self.username


class DocumentType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Record(models.Model):
    class State(models.TextChoices):
        REGISTERED = "registered", "Registrado"
        PENDING = "pending", "Por recibir"
        ACTIVE = "active", "En atención"
        RETURNED = "returned", "Devuelto"
        DONE = "done", "Atendido"
        ARCHIVED = "archived", "Archivado"

    class Channel(models.TextChoices):
        DESK = "desk", "Presencial"
        INTERNAL = "internal", "Interno"

    subject = models.CharField(max_length=120)
    sender = models.CharField(max_length=100)
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    channel = models.CharField(max_length=12, choices=Channel.choices)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_records")
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="assigned_records")
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.PROTECT)
    state = models.CharField(max_length=12, choices=State.choices, default=State.REGISTERED, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    due = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [models.Index(fields=["assignee", "state"])]

    @property
    def code(self):
        return f"CH-{timezone.localtime(self.created_at).year}-{self.pk:06d}"


class Movement(models.Model):
    record = models.ForeignKey(Record, on_delete=models.PROTECT, related_name="movements")
    actor = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=90)
    note = models.CharField(max_length=300, blank=True)
    destination = models.CharField(max_length=90, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at", "-pk"]


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(Record, on_delete=models.PROTECT, related_name="attachments")
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=130)
    size = models.PositiveIntegerField()
    content = models.BinaryField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]


class AuditEvent(models.Model):
    actor = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    record = models.ForeignKey(Record, null=True, on_delete=models.PROTECT)
    action = models.CharField(max_length=40)
    outcome = models.CharField(max_length=20, default="Correcto")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at", "-pk"]


class LoginThrottle(models.Model):
    key = models.CharField(max_length=64, unique=True)
    window = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)


class StorageQuota(models.Model):
    used = models.PositiveBigIntegerField(default=0)
