# Registro de auditoría del prototipo SGD Chicla

| Dato | Valor |
| --- | --- |
| URL del prototipo | |
| Commit desplegado | |
| Fecha y equipo auditor | |
| Tiempo de inactividad configurado | |
| Identificadores de cuentas sintéticas utilizadas | |

| Caso | Control y resultado esperado | Resultado observado | Evidencia | Estado |
| --- | --- | --- | --- | --- |
| P01 | El formulario de cuentas rechaza una contraseña por debajo de la política. | | | |
| P02 | Un perfil administrativo de Mesa de Partes carece de acceso a Usuarios y áreas. Un responsable solo consulta expedientes asignados. | | | |
| P03 | Las búsquedas respetan los permisos. La inspección del código confirma el uso del ORM con parámetros. | | | |
| P04 | Después del intervalo de inactividad, el sistema solicita autenticación. | | | |
| P05 | El sistema admite un PDF válido dentro del límite. Rechaza formatos no permitidos y restringe la descarga al personal autorizado. | | | |
| P06 | La bitácora registra accesos rechazados y actuaciones documentarias sin guardar credenciales. | | | |
| P07 | La inspección de la base muestra únicamente hashes de contraseña con sal para las cuentas activadas. Redacta los valores al capturar. | | | |
| P08 | El manejo de errores muestra una respuesta genérica y conserva el diagnóstico en los registros del servicio. La regresión automatizada verifica la respuesta a una excepción controlada en local. | | | |
| P09 | Tras cerrar sesión, una vista protegida exige volver a autenticarse. | | | |
| P10 | Los campos requeridos y los valores inválidos se rechazan en el servidor. El expediente inválido no se crea. | | | |

Estados de registro: pendiente, conforme, no conforme o no aplicable con justificación. Vincula cada captura a una versión, cuenta de prueba y fecha. Si hay una corrección, registra el caso, el commit corregido, la evidencia nueva y la decisión de cierre.
