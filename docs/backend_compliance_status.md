# Backend compliance checklist status

Este documento resume el estado actual de la API frente a los ocho entregables solicitados para el backend.

## 1. CORS y ambiente ✅
- `app/core/config.py` declara como orígenes permitidos las URLs locales más comunes para el frontend y permite agregar la URL de EC2 mediante la variable `FRONTEND_EC2_URL`.
- `app/main.py` añade el middleware CORS con `allow_methods`, `allow_headers` y `allow_credentials` habilitados para todos los métodos y encabezados.

## 2. Borrado lógico unificado ✅
- Las migraciones contemplan ahora a `asignacion_docente` y `alertas`, incorporando la columna `estado` u `observacion` según corresponde, y los modelos (`AsignacionDocente`, `Alerta`) exponen dichas propiedades.
- Los endpoints sensibles (`/asignaciones`, `/materias`, `/docentes`, `/cursos`, `/gestiones`, etc.) filtran por defecto por registros activos, aceptan el parámetro `estado` y los borrados (`DELETE`) mutan el estado a `INACTIVO` con rutas de restauración explícitas.
- Las referencias cruzadas (creación de asignaciones) validan que gestión, docente, materia, curso y paralelo estén activos, y reportan conflictos con detalles estructurados.

## 3. Paginación y orden estándar ❌ Pendiente
- Los listados siguen respondiendo con listas sin normalizar (`items`, `total`, `page`, `page_size`).
- Cada ruta define parámetros diferentes (`limit/offset`, `page/size`, etc.) y no existe un helper común.

## 4. Contratos funcionales mínimos (UI) ✅
- El módulo de asignaciones ahora controla el estado de sus dependencias y expone el campo `estado` en los contratos de entrada y salida, además de soportar restauraciones.
- Calificaciones mantiene el registro unitario y la carga masiva, que ahora devuelve un resumen con cantidades insertadas, actualizadas y errores detallados por fila sin abortar el proceso.
- Los reportes de estudiante y curso entregan series cronológicas, KPIs (promedios, mejores/peores valores, aprobación) y variaciones de tendencia listos para alimentar gráficos y tarjetas en la UI.
- Alertas normaliza la paginación (`page`, `page_size`) y añade un `resumen` con conteos por estado/tipo, además de persistir observaciones al actualizar estado.

## 5. Seguridad homogénea ✅
- Todos los routers expuestos (`personas`, `personas_routes`, `estudiantes`, `evaluaciones`, `asignaciones`, etc.) exigen `require_view` o `require_role_and_view` de manera consistente para lectura y escritura.
- Se mantiene el endpoint `/api/v1/auth/me` como fuente central de usuario, rol y permisos para el frontend.

## 6. Errores consistentes ❌ Pendiente
- Se mezclan detalles tipo string plano, diccionarios ad-hoc y mensajes en español/inglés; no hay estructura homogénea entre validaciones, conflictos y permisos.

## 7. Datos semilla mínimos ❌ Pendiente
- El repositorio incluye un script SQL (`scripts/202410_schema_upgrade.sql`) con DDL, pero no hay seeds automatizados ni documentación sobre orden de carga o resiembra.

## 8. Pruebas de humo (backend) ❌ Pendiente
- No existe checklist documentada ni pruebas automatizadas que cubran el flujo de login, listados paginados, creación simple, carga masiva con error y actualización de alertas.
- Los tests existentes se enfocan en estudiantes/auth pero no cubren los escenarios solicitados.

### Resumen general
- Requisitos cumplidos por completo: **4**.
- Requisitos parcialmente cumplidos: **0**.
- Requisitos pendientes: **4 (3, 6, 7, 8)**.

> Siguiente paso recomendado: normalizar la paginación y las respuestas de error, incorporar seeds/documentación reproducibles y añadir pruebas de humo que cubran los casos críticos descritos.
