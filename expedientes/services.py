import hashlib
import hmac
import ipaddress
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import AuditEvent, LoginThrottle, Movement, Record, User

S = Record.State
TRANSITIONS = {
    "derive": ("Derivar", "Expediente derivado", (S.REGISTERED, S.RETURNED), S.PENDING),
    "receive": ("Confirmar recepción", "Recepción confirmada", (S.PENDING,), S.ACTIVE),
    "return": ("Devolver", "Devuelto a Mesa de Partes", (S.PENDING, S.ACTIVE), S.RETURNED),
    "finish": ("Marcar como atendido", "Atención completada", (S.ACTIVE,), S.DONE),
    "archive": ("Archivar", "Expediente archivado", (S.DONE,), S.ARCHIVED),
}


def audit(request, action, outcome="Correcto", record=None, actor=None):
    AuditEvent.objects.create(
        actor=actor or (request.user if request.user.is_authenticated else None),
        record=record, action=action, outcome=outcome,
    )


def accessible_records(user):
    records = Record.objects.all()
    if user.role == User.Role.ADMIN:
        return records
    if user.role == User.Role.OFFICE:
        return records.filter(Q(creator=user) | Q(assignee=user))
    if user.role == User.Role.AREA:
        return records.filter(assignee=user)
    return records.none()


def permitted_actions(user, record):
    if user.role == User.Role.ADMIN:
        keys = TRANSITIONS.keys()
    elif user.role == User.Role.OFFICE:
        keys = ("derive", "archive")
    else:
        keys = ("receive", "return", "finish")
    return {key: TRANSITIONS[key][0] for key in keys if record.state in TRANSITIONS[key][2]}


def move(request, record, action, data):
    _, title, _, state = TRANSITIONS[action]
    destination = ""
    if action == "derive":
        assignee = User.objects.select_for_update(of=("self",)).filter(
            pk=data["assignee"].pk, role=User.Role.AREA, is_active=True, area__active=True,
        ).first()
        if assignee is None:
            return False
        record.assignee, record.area = assignee, assignee.area
        destination = f"{assignee.area} · {assignee.display_name}"
    elif action == "return":
        record.assignee = None
        destination = "Mesa de Partes"
    record.state = state
    record.save(update_fields=["state", "assignee", "area"])
    Movement.objects.create(
        record=record, actor=request.user, title=title, note=data["note"], destination=destination[:90],
    )
    audit(request, title, record=record)
    return True


def client_address(request):
    address = request.META.get("REMOTE_ADDR", "")
    if settings.ON_RENDER:
        # Render appends its observed client address to the forwarding chain.
        address = request.META.get("HTTP_X_FORWARDED_FOR", address).split(",")[-1].strip()
    try:
        return str(ipaddress.ip_address(address))
    except ValueError:
        return "unknown"


@transaction.atomic
def verify_login(request, username, password):
    now = timezone.now()
    cutoff = now - timedelta(minutes=10)
    scope_limits = [(f"account:{username.casefold()}", 8), (f"source:{client_address(request)}", 30)]
    keys = sorted((hmac.new(settings.SECRET_KEY.encode(), scope.encode(), hashlib.sha256).hexdigest(), limit)
                  for scope, limit in scope_limits)
    counters = []
    for key, limit in keys:
        counter, _ = LoginThrottle.objects.select_for_update().get_or_create(key=key, defaults={"window": now})
        if counter.window <= cutoff:
            counter.window, counter.count = now, 0
            counter.save(update_fields=["window", "count"])
        counters.append((counter, limit))
    if any(counter.count >= limit for counter, limit in counters):
        return None
    user = authenticate(request, username=username, password=password)
    if user is None:
        for counter, _ in counters:
            counter.count += 1
            counter.save(update_fields=["count"])
        audit(request, "Inicio de sesión", "Rechazado")
    return user
