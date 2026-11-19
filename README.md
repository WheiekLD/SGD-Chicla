# SGD Chicla

Prototipo web del Sistema de Gestión Documentaria de Chicla. Implementado en Django 5.2 LTS y PostgreSQL 17. El personal de Mesa de Partes registra y deriva expedientes, los responsables confirman recepción, devuelven o atienden los casos, y el personal autorizado archiva los atendidos. Cada expediente tiene un cargo imprimible, un historial de custodia y adjuntos privados.

## Desplegar en Render Free

1. Sube esta carpeta de proyecto a un repositorio Git de tu cuenta. Incluye `render.yaml`, `requirements.txt`, `manage.py`, `sgd/`, `expedientes/`, `templates/` y `static/`. Las dependencias y bases locales se excluyen mediante `.gitignore`.
2. En [Render](https://dashboard.render.com/), elige **New → Blueprint**, conecta el repositorio y selecciona la rama que contiene `render.yaml`.
3. Cuando Render solicite `DEMO_PASSWORD`, escribe una contraseña de 15 a 256 caracteres que no sea común ni parecida a los nombres de las cuentas. Esa será la contraseña inicial de las cuatro cuentas en una base nueva. El Blueprint genera `SECRET_KEY` y conecta el servicio web Free con PostgreSQL Free 17.
4. Abre la URL HTTPS que aparezca en Render e ingresa con cualquiera de los usuarios de la tabla. Las cuatro cuentas se crean activas en una instalación nueva con `SEED_DEMO=1`.
5. Puedes retirar `DEMO_PASSWORD` de **Environment** después de confirmar los accesos. Si inicializas otra base vacía, vuelve a configurar la variable. Cada cuenta guarda su propio hash y puedes cambiar su contraseña en **Usuarios y áreas**.

Render solicita el secreto al crear el Blueprint. En un servicio ya creado, agrega `DEMO_PASSWORD` manualmente en **Environment**. Las cuentas existentes conservan su contraseña y estado. Si alguna cuenta de prueba ya existe desactivada, puedes asignarle una contraseña y activarla en **Usuarios y áreas**.

La URL del servicio es pública y los módulos de trabajo exigen autenticación. Usa exclusivamente cuentas, expedientes y archivos sintéticos. Para iniciar una base nueva con solo el administrador y los catálogos, cambia `SEED_DEMO` a `"0"` en `render.yaml` antes de aplicar el Blueprint.

Render Free duerme tras 15 minutos de inactividad y puede tardar alrededor de un minuto en volver a responder. La base gratuita tiene 1 GB y vence a los 30 días desde su creación. Programa las pruebas dentro de ese plazo. Los archivos del contenedor son temporales. El SGD conserva expedientes, adjuntos, sesiones y bitácora en PostgreSQL. [Guía de Blueprint](https://render.com/docs/blueprint-spec) · [Límites de Render Free](https://render.com/docs/free)

## Usuarios y roles del prototipo web

| Usuario | Rol | Área | Funciones principales |
| --- | --- | --- | --- |
| `admin` | Administrador | Todas | Gestiona usuarios y catálogos, consulta la bitácora y opera sobre todos los expedientes. |
| `mesa` | Mesa de Partes | Mesa de Partes | Registra expedientes, genera cargos, deriva casos autorizados y archiva los atendidos. |
| `elena` | Responsable de área | Gestión Ambiental | Recibe, devuelve o atiende los expedientes asignados a su cuenta. |
| `marco` | Responsable de área | Infraestructura | Recibe, devuelve o atiende los expedientes asignados a su cuenta. |

## Ejecutar en Windows

Necesitas Python 3.13 o 3.14 y una base PostgreSQL 17 vacía para el proyecto. En PowerShell, desde la raíz, ajusta `DATABASE_URL` y elige tu contraseña inicial.

```powershell
python -m venv .venv
& .venv/Scripts/python.exe -m pip install -r requirements.txt
$env:DJANGO_DEBUG = '1'
$env:DATABASE_URL = 'postgresql://sgd:CONTRASENA_DE_BD@127.0.0.1:5432/sgd'
$env:DEMO_PASSWORD = Read-Host 'Contraseña inicial para las cuentas del prototipo web'
$env:SEED_DEMO = '1'
& .venv/Scripts/python.exe manage.py prepare
& .venv/Scripts/python.exe manage.py runserver
```

Abre `http://127.0.0.1:8000`. Codifica los caracteres reservados si la contraseña de la base aparece dentro de la URL. `prepare` aplica migraciones e inicializa los catálogos y las cuentas. El modo de depuración solo se habilita para desarrollo local.

## Verificación y auditoría

- Ejecuta `python manage.py test` con una base local y un usuario de PostgreSQL con permiso para crear la base temporal de pruebas.
- `/salud/` confirma la disponibilidad de la base y del esquema inicial. La cuenta de administrador permite consultar la bitácora.
- El pie del portal muestra los primeros 12 caracteres del commit que Render está ejecutando.
- El límite de inactividad es de 300 segundos. Puedes ajustar `SESSION_IDLE_SECONDS` en el entorno entre 30 y 3600 segundos. Registra el valor junto con el commit y la URL antes de evaluar.
- Los adjuntos son PDF de hasta 5 MiB, con un máximo de tres por expediente y 100 MiB totales. La descarga exige permiso sobre el expediente.
- Usa [la matriz de auditoría](Auditoria_P01-P10.md) para recoger evidencias propias. Los resultados del equipo se registran allí tras ejecutar la evaluación.

## Respaldo

Antes del vencimiento de la base de Render, habilita temporalmente la conexión externa de PostgreSQL para tu IP en el panel. Usa su URL externa con TLS y restaura en una base local vacía. Guarda el volcado de forma privada. Devuelve el acceso externo a la lista vacía al terminar.

```powershell
pg_dump --format=custom --no-owner --no-privileges --file=sgd-chicla.dump --dbname=$env:SGD_BACKUP_URL
pg_restore --no-owner --no-privileges --exit-on-error --dbname=$env:SGD_RESTORE_URL sgd-chicla.dump
```

[Respaldo de PostgreSQL en Render](https://render.com/docs/postgresql-backups) · [Conexiones externas y reglas de IP](https://render.com/docs/postgresql-creating-connecting#restricting-external-access)
