import re
from io import BytesIO
from pathlib import PurePosixPath

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from .forms import AccountForm, AreaForm, AttachmentForm, LoginForm, MovementForm, RecordForm, TypeForm
from .models import Area, Attachment, AuditEvent, DocumentType, Movement, Record, StorageQuota, User
from .services import accessible_records, audit, move, permitted_actions, verify_login


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM django_migrations LIMIT 1")
    except DatabaseError:
        return HttpResponse("No disponible", status=503, content_type="text/plain")
    return HttpResponse("OK", content_type="text/plain")


@never_cache
@require_http_methods(["GET", "POST"])
def sign_in(request):
    if request.user.is_authenticated:
        return redirect("inbox")
    form = LoginForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = verify_login(request, form.cleaned_data["username"], form.cleaned_data["password"])
        if user is not None:
            login(request, user)
            request.session["last_seen"] = int(timezone.now().timestamp())
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            audit(request, "Inicio de sesión")
            return redirect("inbox")
        form.add_error(None, "No se pudo iniciar sesión. Revisa tus datos o vuelve a intentar más tarde.")
    return render(request, "login.html", {"form": form})


@never_cache
@login_required
@require_POST
def sign_out(request):
    audit(request, "Cierre de sesión")
    logout(request)
    return redirect("login")


def deny(request, action, record=None):
    audit(request, action, "Denegado", record)
    raise PermissionDenied


def require_admin(request):
    if request.user.role != User.Role.ADMIN:
        deny(request, "Acceso administrativo")


def get_record(request, pk, lock=False):
    records = accessible_records(request.user)
    if lock:
        records = records.select_for_update()
    else:
        records = records.select_related("area", "document_type", "assignee")
    item = records.filter(pk=pk).first()
    if item is None:
        # The same response covers missing records and records outside this user's scope.
        audit(request, "Acceso a expediente", "Denegado")
        raise Http404
    return item


def pager(request, queryset):
    page = Paginator(queryset, 12).get_page(request.GET.get("pagina"))
    query = request.GET.copy()
    query.pop("pagina", None)
    return {"page": page, "page_query": query.urlencode()}


def date_filter(queryset, request):
    for key, comparison in (("desde", "gte"), ("hasta", "lte")):
        try:
            value = request.GET.get(key, "")
            date = parse_date(value) if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) else None
        except ValueError:
            date = None
        if date:
            queryset = queryset.filter(**{f"created_at__date__{comparison}": date})
    return queryset


@never_cache
@login_required
@require_GET
def inbox(request, archived=False):
    pool = accessible_records(request.user)
    pool = pool.filter(state=Record.State.ARCHIVED) if archived else pool.exclude(state=Record.State.ARCHIVED)
    counts = dict(pool.values("state").annotate(total=Count("pk")).values_list("state", "total"))
    tab_labels = [
        ("", "Todos"), ("registered", "Por derivar"), ("pending", "Por recibir"),
        ("active", "En atención"), ("returned", "Devueltos"), ("done", "Atendidos"),
    ]
    tabs = [(key, label, counts.get(key, 0) if key else sum(counts.values())) for key, label in tab_labels]
    state = request.GET.get("estado", "")
    area = request.GET.get("area", "")
    term = request.GET.get("q", "").strip()[:120]
    filtered = pool
    if state and not archived:
        filtered = filtered.filter(state=state)
    if area.isascii() and area.isdigit() and len(area) <= 18:
        filtered = filtered.filter(area_id=int(area))
    if term:
        query = Q(subject__icontains=term) | Q(sender__icontains=term)
        if match := re.fullmatch(r"(?:CH-([0-9]{4})-)?([0-9]{1,18})", term, re.IGNORECASE):
            code = Q(pk=int(match[2]))
            if match[1] is not None and 1900 <= int(match[1]) <= 9998:
                code &= Q(created_at__year=int(match[1]))
            elif match[1] is not None:
                code = Q(pk__in=[])
            query |= code
        filtered = filtered.filter(query)
    filtered = date_filter(filtered, request).select_related("document_type", "area")
    return render(request, "inbox.html", {
        **pager(request, filtered), "archived": archived, "tabs": tabs,
        "metrics": tabs[2:5], "state": state, "area_selected": area, "term": term,
        "areas": Area.objects.filter(active=True), "section": "archive" if archived else "inbox",
    })


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def new_record(request):
    if request.user.role not in (User.Role.ADMIN, User.Role.OFFICE):
        deny(request, "Registro de expediente")
    form = RecordForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            item.creator = request.user
            item.save()
            Movement.objects.create(record=item, actor=request.user, title="Expediente registrado")
            audit(request, "Expediente registrado", record=item)
        messages.success(request, f"Expediente {item.code} registrado.")
        return redirect("record", pk=item.pk)
    return render(request, "form.html", {
        "form": form, "title": "Registrar expediente", "section": "new_record",
        "intro": "Completa los datos de ingreso para generar el cargo interno.",
        "submit": "Registrar expediente", "back": reverse("inbox"),
    })


def detail_context(request, item):
    return {
        "item": item, "actions": permitted_actions(request.user, item),
        "movements": item.movements.select_related("actor"),
        "attachments": item.attachments.defer("content"),
        "attachment_form": AttachmentForm(),
        "archived": item.state == Record.State.ARCHIVED,
        "section": "archive" if item.state == Record.State.ARCHIVED else "inbox",
    }


@never_cache
@login_required
@require_GET
def record_detail(request, pk):
    return render(request, "record.html", detail_context(request, get_record(request, pk)))


@never_cache
@login_required
@require_GET
def receipt(request, pk):
    item = get_record(request, pk)
    return render(request, "receipt.html", {"item": item, "section": "inbox"})


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def transition(request, pk, action):
    item = get_record(request, pk)
    actions = permitted_actions(request.user, item)
    if action not in actions:
        deny(request, "Movimiento de expediente", item)
    form = MovementForm(action, request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # Recheck access and state after locking to handle simultaneous changes.
            locked = get_record(request, pk, lock=True)
            permitted = action in permitted_actions(request.user, locked)
            saved = permitted and move(request, locked, action, form.cleaned_data)
        if not permitted:
            deny(request, "Movimiento de expediente", item)
        if saved:
            messages.success(request, "Movimiento registrado.")
            if action == "return" and request.user.role == User.Role.AREA:
                return redirect("inbox")
            return redirect("record", pk=pk)
        form.add_error("assignee", "El responsable dejó de estar disponible. Selecciona otro.")
    return render(request, "form.html", {
        "form": form, "title": actions[action], "section": "inbox", "intro": item.code,
        "submit": actions[action], "back": reverse("record", args=[pk]),
    })


def read_pdf(file):
    if file.size > settings.MAX_ATTACHMENT_BYTES:
        raise ValueError("El PDF supera el límite de 5 MiB.")
    raw = file.read(settings.MAX_ATTACHMENT_BYTES + 1)
    if len(raw) > settings.MAX_ATTACHMENT_BYTES:
        raise ValueError("El PDF supera el límite de 5 MiB.")
    if not file.name.lower().endswith(".pdf") or not raw.startswith(b"%PDF-"):
        raise ValueError("Selecciona un archivo PDF válido.")
    try:
        reader = PdfReader(BytesIO(raw), strict=True)
        if reader.is_encrypted or reader.root_object.get("/Type") != "/Catalog":
            raise ValueError("Selecciona un PDF válido sin contraseña.")
    except (PyPdfError, ValueError, TypeError, KeyError, RecursionError):
        raise ValueError("Selecciona un PDF válido sin contraseña.") from None
    return raw


@never_cache
@login_required
@require_POST
def upload_attachment(request, pk):
    item = get_record(request, pk)
    if item.state == Record.State.ARCHIVED:
        deny(request, "Carga de adjunto", item)
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        file = form.cleaned_data["pdf"]
        try:
            raw = read_pdf(file)
            with transaction.atomic():
                locked = get_record(request, pk, lock=True)
                if locked.state == Record.State.ARCHIVED:
                    raise ValueError("El expediente ya fue archivado.")
                if locked.attachments.count() >= 3:
                    raise ValueError("El expediente admite hasta tres adjuntos.")
                quota, _ = StorageQuota.objects.select_for_update().get_or_create(pk=1)
                if quota.used + len(raw) > settings.ATTACHMENT_QUOTA_BYTES:
                    raise ValueError("Se alcanzó la cuota de adjuntos del prototipo web.")
                filename = PurePosixPath(file.name.replace(chr(92), "/")).name
                filename = "".join(char for char in filename if char.isprintable())
                filename = filename[:-4][:126] + ".pdf"
                Attachment.objects.create(record=locked, uploaded_by=request.user, name=filename, size=len(raw), content=raw)
                quota.used += len(raw)
                quota.save(update_fields=["used"])
                Movement.objects.create(record=locked, actor=request.user, title="Adjunto agregado", note=filename)
                audit(request, "Carga de adjunto", record=locked)
            messages.success(request, "PDF adjuntado.")
            return redirect("record", pk=pk)
        except ValueError as error:
            form.add_error("pdf", str(error))
    audit(request, "Carga de adjunto", "Rechazado", item)
    return render(request, "record.html", {**detail_context(request, item), "attachment_form": form}, status=400)


@never_cache
@login_required
@require_GET
def download_attachment(request, pk):
    attachment = Attachment.objects.filter(pk=pk, record__in=accessible_records(request.user)).first()
    if attachment is None:
        audit(request, "Descarga de adjunto", "Denegado")
        raise Http404
    audit(request, "Descarga de adjunto", record=attachment.record)
    return FileResponse(BytesIO(bytes(attachment.content)), as_attachment=True, filename=attachment.name, content_type="application/pdf")


@never_cache
@login_required
@require_GET
def accounts(request):
    require_admin(request)
    return render(request, "accounts.html", {
        **pager(request, User.objects.select_related("area").order_by("username")), "section": "accounts",
    })


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def account_editor(request, pk=None):
    require_admin(request)
    user = get_object_or_404(User, pk=pk) if pk is not None else User()
    form = AccountForm(request.POST if request.method == "POST" else None, instance=user)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                if pk is not None:
                    current = User.objects.select_for_update().get(pk=pk)
                    form.instance.password = current.password
                    if pk == request.user.pk and (form.cleaned_data["role"] != User.Role.ADMIN or not form.cleaned_data["is_active"]):
                        form.add_error(None, "Tu propia cuenta debe seguir activa y conservar el perfil de administrador.")
                    if current.role == User.Role.AREA and (
                        not form.cleaned_data["is_active"] or form.cleaned_data["role"] != User.Role.AREA
                        or current.area_id != getattr(form.cleaned_data["area"], "pk", None)
                    ) and current.assigned_records.filter(state__in=(Record.State.PENDING, Record.State.ACTIVE)).exists():
                        form.add_error(None, "La cuenta tiene expedientes pendientes. Devuélvelos a Mesa de Partes antes de cambiar su asignación.")
                if not form.errors:
                    form.save()
                    audit(request, "Cuenta actualizada" if pk else "Cuenta creada")
        except IntegrityError:
            if User.objects.filter(username=form.cleaned_data["username"]).exclude(pk=pk).exists():
                form.add_error("username", "Este nombre de usuario ya está en uso.")
            else:
                raise
        if not form.errors:
            messages.success(request, "Cuenta guardada.")
            return redirect("accounts")
    return render(request, "form.html", {
        "form": form, "title": "Editar cuenta" if pk else "Crear cuenta", "section": "accounts",
        "intro": "Configura los permisos de una cuenta del sistema.", "submit": "Guardar cuenta", "back": reverse("accounts"),
    })


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def catalog(request, kind):
    require_admin(request)
    configs = {"areas": (Area, AreaForm, "Áreas"), "tipos": (DocumentType, TypeForm, "Tipos documentarios")}
    if kind not in configs:
        raise Http404
    model, form_class, title = configs[kind]
    form = form_class(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
                audit(request, "Catálogo actualizado")
        except IntegrityError:
            if model.objects.filter(name=form.cleaned_data["name"]).exists():
                form.add_error("name", "Este nombre ya existe en el catálogo.")
            else:
                raise
        else:
            messages.success(request, "Catálogo actualizado.")
            return redirect("catalog", kind=kind)
    return render(request, "catalog.html", {"page": pager(request, model.objects.all())["page"], "title": title, "form": form, "section": "accounts"})


@never_cache
@login_required
@require_GET
def audit_log(request):
    require_admin(request)
    events = AuditEvent.objects.select_related("actor", "record")
    term = request.GET.get("q", "").strip()[:100]
    outcome = request.GET.get("resultado", "")
    if term:
        events = events.filter(Q(action__icontains=term) | Q(actor__username__icontains=term))
    if outcome in ("Correcto", "Rechazado", "Denegado"):
        events = events.filter(outcome=outcome)
    return render(request, "audit.html", {**pager(request, date_filter(events, request)), "section": "audit", "term": term, "outcome": outcome})


def bad_request(request, exception):
    return render(request, "error.html", {"title": "Solicitud inválida", "description": "Revisa los datos y vuelve a intentarlo."}, status=400)


def forbidden(request, exception):
    return render(request, "error.html", {"title": "Acceso denegado", "description": "Tu perfil no tiene permiso para realizar esta acción."}, status=403)


def not_found(request, exception):
    return render(request, "error.html", {"title": "Página no disponible", "description": "Vuelve a la bandeja para consultar tus expedientes."}, status=404)


def server_error(request):
    return render(request, "error.html", {"title": "No se pudo completar la solicitud", "description": "Vuelve a intentarlo. Si el problema continúa, informa al administrador."}, status=500)


def csrf_failure(request, reason=""):
    return render(request, "error.html", {"title": "El formulario caducó", "description": "Recarga la página y vuelve a enviar el formulario."}, status=403)
