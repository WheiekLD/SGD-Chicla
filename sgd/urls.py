from django.urls import include, path

urlpatterns = [path("", include("expedientes.urls"))]

handler400 = "expedientes.views.bad_request"
handler403 = "expedientes.views.forbidden"
handler404 = "expedientes.views.not_found"
handler500 = "expedientes.views.server_error"
