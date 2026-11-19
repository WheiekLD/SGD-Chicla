from django.conf import settings


def release(request):
    return {"sgd_release": settings.RELEASE[:12]}
