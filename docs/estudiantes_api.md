# API de Estudiantes

Esta sección describe los contratos actuales de la API de estudiantes expuestos por el backend. Úsalo como referencia para tu frontend.

## Crear estudiante

```
POST /api/v1/estudiantes
```

### Cuerpo (`application/json`)

```json
{
  "codigo_rude": "RUDE-001",
  "anio_ingreso": 2024,
  "situacion": "REGULAR",
  "estado": "ACTIVO",
  "persona_id": 123,
  "persona": null
}
```

Notas:

* Debes enviar **solo** `persona_id` o el objeto `persona`. Si mandas ambos o ninguno la petición será rechazada.
* `codigo_rude` se recorta automáticamente (se eliminan espacios iniciales y finales) y tiene un máximo de 30 caracteres.
* Si omites `anio_ingreso` se asumirá el año actual.

### Respuesta `201`

```json
{
  "id": 45,
  "codigo_rude": "RUDE-001",
  "anio_ingreso": 2024,
  "situacion": "REGULAR",
  "estado": "ACTIVO",
  "persona_id": 123,
  "persona": {
    "id": 123,
    "nombres": "Ana",
    "apellidos": "Pérez",
    "sexo": "FEMENINO",
    "fecha_nacimiento": "2000-01-01",
    "celular": "78945612",
    "direccion": "Av. Siempre Viva",
    "ci": {
      "ci_numero": "CI-123",
      "ci_complemento": null,
      "ci_expedicion": "LP"
    }
  }
}
```

## Listar estudiantes

```
GET /api/v1/estudiantes
```

### Parámetros de consulta soportados

| Parámetro     | Tipo    | Descripción                                                 |
|---------------|---------|-------------------------------------------------------------|
| `persona_id`  | entero  | Filtra por ID de persona.                                   |
| `codigo_rude` | texto   | Coincidencia exacta de código RUDE.                         |
| `estado`      | enum    | `ACTIVO`, `INACTIVO` o `TODOS` (valor por defecto: `ACTIVO`).|
| `limit`       | entero  | Límite de resultados (1-500, por defecto 100).              |
| `offset`      | entero  | Desplazamiento inicial.                                     |
| `page`        | entero  | Página 1..n (alternativo a `offset`).                       |
| `page_size`   | entero  | Tamaño de página si usas `page` (1-500).                    |

### Respuesta `200`

```json
[
  {
    "id": 45,
    "codigo_rude": "RUDE-001",
    "anio_ingreso": 2024,
    "situacion": "REGULAR",
    "estado": "ACTIVO",
    "persona_id": 123,
    "persona": { "id": 123, "nombres": "Ana", "apellidos": "Pérez", "sexo": "FEMENINO" }
  }
]
```

La relación `persona` se carga automáticamente para que no tengas que hacer otra petición.

## Obtener un estudiante

```
GET /api/v1/estudiantes/{id}
```

### Respuesta `200`

Igual al formato de `EstudianteOut` mostrado arriba.

### Respuesta `404`

```json
{"detail": "Estudiante no encontrado"}
```

## Errores comunes

* `400 codigo_rude ya existe`: intenta registrar un RUDE que ya está en uso.
* `400 La persona ya está registrada como estudiante`: la persona asociada ya tiene ficha de estudiante.
* `404 Persona no encontrada`: el `persona_id` enviado no existe.
