from django.urls import path

from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("ingresar/", views.sign_in, name="login"),
    path("salir/", views.sign_out, name="logout"),
    path("salud/", views.health, name="health"),
    path("archivo/", views.inbox, {"archived": True}, name="archive"),
    path("expedientes/nuevo/", views.new_record, name="new_record"),
    path("expedientes/<int:pk>/", views.record_detail, name="record"),
    path("expedientes/<int:pk>/cargo/", views.receipt, name="receipt"),
    path("expedientes/<int:pk>/movimientos/<slug:action>/", views.transition, name="transition"),
    path("expedientes/<int:pk>/adjuntos/", views.upload_attachment, name="upload"),
    path("adjuntos/<uuid:pk>/", views.download_attachment, name="download"),
    path("administracion/usuarios/", views.accounts, name="accounts"),
    path("administracion/usuarios/nuevo/", views.account_editor, name="new_account"),
    path("administracion/usuarios/<int:pk>/", views.account_editor, name="edit_account"),
    path("administracion/catalogos/<slug:kind>/", views.catalog, name="catalog"),
    path("administracion/bitacora/", views.audit_log, name="audit"),
]
