# SGD-Chicla — Requisitos y plan de implementación

Propuesta para un prototipo web de gestión documentaria de la Municipalidad Distrital de Chicla. El equipo auditor operará un sistema funcional con expedientes, usuarios y adjuntos sintéticos y obtendrá evidencias de su propia instancia. El flujo principal es **registro → derivación → atención → archivo interno**, con historial consultable en cada etapa.

## Investigación y decisiones de alcance

| Referencia | Qué aporta al prototipo |
| --- | --- |
| [Municipalidad Distrital de Chicla en Gob.pe](https://www.gob.pe/munichicla) y [Portal de Transparencia](https://www.transparencia.gob.pe/enlaces/pte_transparencia_enlaces.aspx?id_entidad=10630) | El índice oficial de Gob.pe muestra el acceso a Mesa de Partes y el PTE identifica la entidad. Sirven para contextualizar la recepción de expedientes. |
| [Oficio de Chicla publicado en SINIA](https://sinia.minam.gob.pe/sites/default/files/archivos/public/docs/2025054956.pdf) | Ejemplo oficial de tipos documentales como oficio e informe, y de la participación de distintas áreas. Los datos del prototipo serán inventados. |
| [Modelo de Gestión Documental de la PCM](https://www.gob.pe/es/62913-implementar-el-modelo-de-gestion-documental-mgd) | Marco general de recepción, emisión, archivo y despacho. Incluye responsabilidades, instrumentos de gestión, firma digital e interoperabilidad. El prototipo cubre la recepción, el trámite y archivo internos. |
| [SGD de la Municipalidad de San Jerónimo](https://sistema01.munisanjeronimocusco.gob.pe/sgd/index.html) | Presenta el SGD de funcionarios, la mesa de partes, la consulta ciudadana y la verificación de documentos como módulos distintos. El prototipo se centra en el SGD interno. |
| [SGD municipal de San Juan](https://www.informacionsgd.munisanjuan.gob.pe/) | La visibilidad depende de las áreas que intervienen en el trámite. También documenta asignación por área y persona, seguimiento en bandeja y un límite de 5 MB por archivo. |
| [Manuales del Instituto Nacional de Salud](https://www.gob.pe/84479-instituto-nacional-de-salud-manuales-del-sistema-de-gestion-documental-sgd) | Distinguen recepción, registro, despacho y búsqueda por estado. Orientan el diseño de la bandeja, el formulario y la ficha de expediente. |

El [Facebook enlazado](https://www.facebook.com/MuniChicla2023.2026/?locale=es_LA) bloqueó la consulta automatizada. Las fuentes públicas consultadas permiten describir el contexto de Chicla. El organigrama de prueba y las reglas del trámite son propuestas para el prototipo web. Las áreas de ejemplo serán Mesa de Partes, Secretaría General y Gestión Ambiental.

El alcance inicial comprende tres perfiles y las funciones requeridas para P01–P10. La mesa de partes ciudadana, el seguimiento público, la emisión oficial, la firma digital, el despacho externo, las notificaciones por correo, la interoperabilidad con PIDE y la conservación archivística normativa quedan para una versión institucional futura.

### Segunda revisión de sistemas municipales

- Chorrillos distingue los documentos remitidos que esperan recepción de los documentos ya recibidos. SGD Chicla mostrará la bandeja **Por recibir** y registrará quién confirmó la recepción y cuándo. [Manual SGD de Chorrillos](https://portal.munichorrillos.gob.pe/sites/default/files/documentos/sgd/manuales/01-manual-modulo-general.pdf)
- Ilabaya presenta bandejas de entrada, derivados y archivados, con estado, responsable y plazos. La ficha de Chicla incorporará canal de ingreso, responsable actual y fecha objetivo opcional. [Manual SIGED de Ilabaya](https://munilabaya.gob.pe/siged/manual_SIGED.pdf)
- Barranco documenta la redirección de trámites y la confirmación de recepción. El prototipo incorporará **Devuelto** como estado interno, con motivo obligatorio y posibilidad de nueva derivación. La observación ciudadana con subsanación queda para un módulo futuro. [Lineamientos de Barranco](https://cdn.www.gob.pe/uploads/document/file/5695000/5056904-022-2021-aprueba-directiva-de-lineamientos-para-la-gestion-documentaria.pdf)
- Quiñota distingue derivación, aceptación y cierre en el historial de seguimiento. Esa secuencia se aplica al historial interno de Chicla. [Manual de Quiñota](https://sgd.muniquinota.gob.pe/Manual_Tramites_Externos.pdf)

En el informe actualizado, los apartados 1.4, 2.4 y 2.9 ya señalan PostgreSQL. La figura de 2.4 aún muestra MySQL y un directorio de archivos. Al documentar la implementación habrá que actualizar esa figura, el modelo de adjuntos de 2.5, el entorno de 2.9 y las referencias a PHP en P07. El informe conserva escenarios de referencia en 3.3 y termina con marcadores en 3.4–3.6. Los resultados se incorporarán a partir de la ejecución y de sus evidencias.

## Roles y reglas de negocio

| Operación | Administrador | Personal administrativo | Responsable de área |
| --- | --- | --- | --- |
| Usuarios, roles, áreas y catálogos | Gestiona | — | — |
| Registrar expediente y obtener cargo interno | Sí | Sí | — |
| Buscar y consultar expediente e historial | Todos | Creados por su cuenta o asignados expresamente | Asignados a su cuenta |
| Derivar un expediente registrado o devuelto | Sí | Si tiene acceso y está en la etapa correspondiente | — |
| Confirmar recepción, devolver o marcar como atendido | Sí | — | Solo si está asignado a su cuenta |
| Archivar expediente atendido | Sí | Si tiene acceso | — |
| Cargar adjuntos en expedientes activos | Sí | En expedientes autorizados | En expedientes asignados |
| Descargar adjuntos | Sí | En expedientes autorizados | En expedientes asignados |
| Consultar bitácora técnica | Sí | — | — |

- El expediente tiene un código único e inmutable, como `CH-2026-000001`. PostgreSQL asegura su unicidad aunque dos personas registren al mismo tiempo. El cargo es imprimible y se identifica como «Prototipo web».
- Los estados son Registrado, Por recibir, En atención, Atendido, Archivado y Devuelto. Derivar coloca el expediente en Por recibir. Confirmar recepción lo mueve a En atención. Devolver exige motivo y devuelve el trámite a Mesa de Partes para nueva derivación. El destino debe ser un responsable activo del área seleccionada. Cada cambio registra fecha, usuario y observación cuando corresponda. El expediente archivado queda disponible para consulta autorizada.
- La visibilidad se aplica a las bandejas, los conteos, la búsqueda, las fichas, el historial y la descarga de adjuntos. La baja de un usuario es lógica para conservar la trazabilidad.
- Datos mínimos del expediente: código, tipo, asunto, remitente sintético, fecha de ingreso, canal, usuario registrador, área, responsable, estado y fecha objetivo opcional. Fecha y hora visibles en la zona de Perú.

## Requisitos funcionales

| ID | Requisito | Criterio de aceptación |
| --- | --- | --- |
| RF-01 | Inicio y cierre de sesión con cuentas individuales y panel según el rol. | Una cuenta activa entra y ve sus opciones. Al cerrar sesión, el servidor revoca su acceso. |
| RF-02 | Gestión administrativa de altas, bajas lógicas, roles y áreas. | El administrador puede crear y desactivar una cuenta. El servidor deniega estas operaciones a los otros perfiles. |
| RF-03 | Registro de expedientes y cargo imprimible. | Un registro válido recibe un código único. Un campo requerido vacío o fuera de formato se marca y el expediente queda sin crear. |
| RF-04 | Bandejas, búsqueda y ficha del expediente. | Se puede filtrar por código, asunto, estado, área y fecha dentro del conjunto autorizado. La ficha reúne datos, adjuntos y movimientos. |
| RF-05 | Derivación, recepción, devolución y seguimiento. | Una derivación válida aparece en Por recibir. El destinatario confirma la recepción o registra una devolución con motivo. Mesa de Partes puede volver a derivar. Cada acción deja un movimiento y el sistema rechaza transiciones fuera de flujo. |
| RF-06 | Carga y descarga privada de adjuntos. | Se admite un PDF de prueba válido dentro del límite. La aplicación rechaza un formato no permitido y registra el resultado. Solo usuarios autorizados pueden descargar. |
| RF-07 | Historial del expediente y bitácora administrativa. | El historial muestra el trámite. La bitácora permite filtrar accesos, denegaciones, cambios de roles, derivaciones, cambios de estado y operaciones de adjuntos por fecha, acción y resultado. |
| RF-08 | Catálogos y datos iniciales reproducibles. | El proyecto inicializa tipos documentales, áreas y expedientes ficticios en diferentes estados. Incluye una cuenta por rol y un segundo responsable en otra área para comprobar el aislamiento entre expedientes. |

## Requisitos no funcionales

| ID | Requisito verificable |
| --- | --- |
| RNF-01 Autenticación | Política de contraseñas propuesta de 15 caracteres mínimos y rechazo de contraseñas comunes. Hash PBKDF2-SHA256 con sal mediante el sistema de contraseñas de Django. Limitación de intentos por cuenta y origen, con registro de accesos fallidos y mensaje uniforme. |
| RNF-02 Sesiones | Sesiones almacenadas en PostgreSQL, expiración por inactividad medida en el servidor, cierre con revocación y cookie de sesión `Secure`, `HttpOnly` y `SameSite=Lax`. Intervalo inicial de 5 minutos configurable por entorno. |
| RNF-03 Autorización | Verificar rol y permiso sobre el expediente en cada operación sensible. Protección CSRF en operaciones que modifican datos, incluidos los formularios internos. |
| RNF-04 Validación y errores | Validar entradas en el servidor, usar parámetros del ORM para consultas, escapar la salida y devolver mensajes seguros. Los detalles técnicos quedan en registros internos sin secretos. |
| RNF-05 Adjuntos | Para el piloto, PDF de hasta 5 MiB, máximo 3 por expediente y cuota global de 100 MiB de contenido. Comprobar extensión y tipo del archivo, usar identificadores internos y entregar el PDF como descarga autorizada. |
| RNF-06 Integridad | Actualizar estado, movimiento y evento relacionado en una transacción. Las operaciones concurrentes sobre el mismo expediente respetan el flujo y el correlativo permanece único. |
| RNF-07 Usabilidad | Interfaz en español, navegable con teclado, formularios con etiquetas y errores junto al campo, tablas legibles y diseño adaptable. Bandejas y bitácora paginadas. |
| RNF-08 Persistencia y operación | Expedientes, adjuntos, sesiones y bitácora sobreviven a un reinicio de la aplicación. Registrar versión, commit y fecha de evaluación. Documentar exportación y restauración de PostgreSQL. |
| RNF-09 Privacidad | Usar cuentas y documentos inventados. La pantalla de acceso se identifica como prototipo web. Las capturas de auditoría ocultan contraseñas, tokens, secretos y datos de conexión. |

Los umbrales, estados y áreas del prototipo web son decisiones iniciales del diseño. Los controles técnicos se apoyan en [OWASP ASVS](https://asvs.owasp.org/), [Seguridad en Django](https://docs.djangoproject.com/en/5.2/topics/security/), [contraseñas en Django](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/) y [gestión de sesiones en Django](https://docs.djangoproject.com/en/5.2/topics/http/sessions/).

## Arquitectura elegida

**Python 3.13 + Django 5.2 LTS + Gunicorn + PostgreSQL 17.** Django renderiza las pantallas y entrega los formularios. WhiteNoise sirve CSS, JavaScript e imágenes de la interfaz. El servicio web usa el entorno nativo de Python de Render y arranca con un proceso de Gunicorn. Se ajustará el proceso tras medir el consumo y la respuesta del piloto. [Django LTS](https://www.djangoproject.com/download/) · [Guía de Django en Render](https://render.com/docs/deploy-django) · [PostgreSQL en Render](https://render.com/docs/postgresql-upgrading)

El modelo incluye usuarios, roles, áreas, expedientes, movimientos, adjuntos, eventos de auditoría y sesiones. PostgreSQL guarda los adjuntos pequeños como `bytea`. Los listados consultan los metadatos y la aplicación lee el contenido únicamente para una descarga autorizada. Así se usa una sola base de datos y se conserva el contenido cuando Render reinicia el servicio web. [Tipo binario de PostgreSQL 17](https://www.postgresql.org/docs/17/datatype-binary.html)

### Despliegue gratuito

- Un Web Service Free y una base Render Postgres Free 17 en la misma región, conectados mediante la URL interna. Render termina HTTPS en el dominio `onrender.com`. El acceso a la aplicación exige una cuenta. [Servicios web y puertos](https://render.com/docs/web-services) · [Conexión interna a PostgreSQL](https://render.com/docs/postgresql-creating-connecting)
- Render suspende el servicio tras 15 minutos sin tráfico y el primer acceso puede tardar alrededor de un minuto. El sistema de archivos del servicio es temporal. La base gratuita tiene 1 GB y caduca a los 30 días de su creación. Se creará cerca de la fecha de evaluación. [Límites del plan gratuito](https://render.com/docs/free)
- El repositorio incluirá `render.yaml`, dependencias con versiones fijadas y una inicialización repetible. Las migraciones se aplicarán al arrancar mediante un paso protegido contra ejecuciones concurrentes, antes de aceptar solicitudes. La creación inicial de cuentas se habilitará con credenciales definidas por el operador como secretos de entorno. [Referencia de Blueprint](https://render.com/docs/blueprint-spec) · [Etapas de despliegue de Render](https://render.com/docs/deploys)
- Se documentará un respaldo manual con `pg_dump` antes del vencimiento y se comprobará la restauración en PostgreSQL local. Para exportar desde el equipo se permitirá temporalmente el acceso externo desde su IP. Se documentará también la medición de uso para permanecer dentro de las cuotas. [Exportación manual](https://render.com/docs/postgresql-backups) · [Consumo y facturación](https://render.com/docs/faq)

## Trazabilidad con el informe

| Caso | Control que debe quedar disponible | Evidencia prevista |
| --- | --- | --- |
| P01 | Política de contraseñas en altas y cambios de credencial. | Formulario y respuesta de validación. |
| P02 | Roles y permisos efectivos en rutas, expedientes y adjuntos. | Comparación entre usuarios y registro de decisión de acceso. |
| P03 | Consultas parametrizadas y búsqueda limitada a expedientes autorizados. | Revisión del código y resultados de búsqueda con datos sintéticos. |
| P04 | Expiración por inactividad. | Intervalo configurado y evidencia de expiración. |
| P05 | Validación de adjuntos, almacenamiento privado y descarga autorizada. | Carga aceptada o rechazada según tipo y tamaño, registro y verificación de acceso. |
| P06 | Registro de accesos fallidos y acciones sensibles. | Bitácora anonimizada con eventos y resultados. |
| P07 | Hash de contraseñas de Django. | Configuración del algoritmo y muestra redactada del formato almacenado. |
| P08 | Mensajes genéricos y diagnóstico interno. | Evidencia del manejo de excepciones mediante prueba automatizada local y comportamiento visible de la aplicación. |
| P09 | Revocación al cerrar sesión. | Sesión cerrada y requisito de autenticarse para consultar una vista protegida. |
| P10 | Validación de campos del lado servidor. | Rechazo de datos inválidos y comprobación de que el expediente no se creó. |

La ficha de evidencia incluye fecha, rol, commit, resultado esperado, resultado observado y archivo asociado. Se comprobarán también los atributos de cookies, la persistencia tras reinicio y la restauración del respaldo. Si se confirma un defecto, se documentará su corrección y el resultado de la re-prueba.

## Plan de implementación

1. **Base técnica.** Crear el proyecto Django y su configuración local con PostgreSQL, dependencias, variables de entorno y ruta de salud. Verificar el arranque local y preparar el Blueprint de Render. La base gratuita se creará para la evaluación de la versión funcional.
2. **Acceso y permisos.** Implementar autenticación, sesiones, cuentas, roles y áreas. Verificar permisos de ruta y de expediente con responsables de dos áreas.
3. **Flujo documentario.** Construir bandejas, formulario, cargo, ficha, derivación y cambios de estado. Verificar el recorrido de registro a archivo y el historial.
4. **Adjuntos, bitácora y controles.** Implementar persistencia privada, límites, auditoría, validaciones y manejo de errores. Incorporar pruebas de regresión para reglas del flujo y controles del informe.
5. **Entrega desplegable.** Validar el Blueprint en un servicio gratuito, la carga inicial, la persistencia y el respaldo. Entregar código fuente, guía de despliegue y recuperación, datos sintéticos y matriz P01–P10 en blanco para la auditoría del equipo.

La entrega se considera lista cuando el proyecto puede iniciarse localmente y desplegarse en Render Free, los tres roles completan sus flujos autorizados y el equipo dispone de una instancia reproducible para registrar sus observaciones.
