# Diseño de SGD Chicla

La bandeja organiza el trabajo por estado. La ficha reúne custodia, acciones y evidencia del recorrido. La navegación lateral mantiene visibles los módulos principales y el encabezado identifica el perfil seleccionado.

## Sistema visual

- Azul marino para la barra lateral y el acceso, azul medio para las acciones principales y azules claros para selección, estados y fondos. La paleta sigue el color azul solicitado por la gestión municipal.
- El escudo aportado por el usuario aparece completo y en color en el acceso, la navegación y el cargo de recepción. El fondo de todas las pantallas incluye una marca de agua tenue del mismo escudo. El cargo impreso también incorpora el escudo y su marca de agua.
- Manrope en títulos y DM Sans en controles y tablas, con fuentes del sistema como respaldo. Códigos y conteos usan números tabulares.
- Los estados combinan etiqueta, icono y color. El ámbar indica recepción pendiente, el azul indica atención en curso o concluida y el terracota indica devolución. Los colores de advertencia y error mantienen su significado funcional.
- La bandeja usa tabla en escritorio y fichas compactas en móvil, con código, asunto, área, estado y fecha visibles. El foco de teclado permanece visible y los formularios mantienen etiquetas asociadas a sus campos.

## Pantallas de la maqueta

Bandeja, registro de ingreso, ficha e historial de custodia, archivo, usuarios y áreas, y bitácora. El selector de perfiles permite revisar los permisos visuales de administración, Mesa de Partes y responsable de área. Los expedientes nuevos y sus movimientos se conservan durante la sesión de la página. La maqueta valida la experiencia visual y el flujo. La autenticación, la validación del servidor y la persistencia corresponden a la implementación en Django y PostgreSQL.

## Aplicación funcional

Las plantillas Django reutilizan `static/styles.css`. La pantalla de acceso sustituye el selector de perfiles de la maqueta. El encabezado muestra la cuenta autenticada y su rol. Los formularios, filtros y acciones envían solicitudes a Django. El JavaScript de la aplicación maneja iconos, navegación móvil e impresión.
