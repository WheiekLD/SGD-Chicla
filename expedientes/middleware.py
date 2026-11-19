from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone

from .models import AuditEvent


class ExpireInactiveSession:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info != "/salud/" and request.user.is_authenticated:
            now = int(timezone.now().timestamp())
            last_seen = request.session.get("last_seen", now)
            if now - last_seen >= settings.SESSION_IDLE_SECONDS:
                AuditEvent.objects.create(actor=request.user, action="Sesión caducada")
                logout(request)
                messages.info(request, "La sesión caducó por inactividad. Vuelve a ingresar.")
            else:
                request.session["last_seen"] = now
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return self.get_response(request)
