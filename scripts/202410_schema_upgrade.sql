-- SQL script to align the Académico schema with the new backend.
-- Tested against MySQL 8.0+. Execute with a privileged user.

-- === Catálogo básico ===
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    UNIQUE KEY uq_roles_nombre (nombre),
    UNIQUE KEY uq_roles_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS vistas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    codigo VARCHAR(60) NOT NULL,
    UNIQUE KEY uq_vistas_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rol_vistas (
    rol_id INT NOT NULL,
    vista_id INT NOT NULL,
    PRIMARY KEY (rol_id, vista_id),
    CONSTRAINT fk_rol_vistas_rol FOREIGN KEY (rol_id)
        REFERENCES roles (id) ON DELETE CASCADE,
    CONSTRAINT fk_rol_vistas_vista FOREIGN KEY (vista_id)
        REFERENCES vistas (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(120) NOT NULL,
    apellidos VARCHAR(120) NOT NULL,
    sexo CHAR(1) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    celular VARCHAR(20) NULL,
    direccion VARCHAR(255) NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE personas
    ADD COLUMN IF NOT EXISTS creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS ci_persona (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    ci_numero VARCHAR(20) NOT NULL,
    ci_complemento VARCHAR(5) NULL,
    ci_expedicion VARCHAR(5) NULL,
    UNIQUE KEY uq_ci_numero (ci_numero),
    CONSTRAINT fk_ci_persona FOREIGN KEY (persona_id)
        REFERENCES personas (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    rol_id INT NULL,
    estado ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    ultimo_acceso_en DATETIME NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_usuarios_username (username),
    CONSTRAINT fk_usuarios_persona FOREIGN KEY (persona_id)
        REFERENCES personas (id) ON DELETE CASCADE,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id)
        REFERENCES roles (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS rol_id INT NULL,
    ADD COLUMN IF NOT EXISTS estado ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    ADD COLUMN IF NOT EXISTS ultimo_acceso_en DATETIME NULL,
    ADD COLUMN IF NOT EXISTS creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    actor_id INT NULL,
    accion VARCHAR(60) NOT NULL,
    entidad VARCHAR(60) NOT NULL,
    entidad_id VARCHAR(60) NULL,
    ip_origen VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_actor FOREIGN KEY (actor_id)
        REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    codigo_est VARCHAR(30) NULL,
    CONSTRAINT fk_estudiante_persona FOREIGN KEY (persona_id)
        REFERENCES personas (id) ON DELETE CASCADE,
    UNIQUE KEY uq_est_codigo (codigo_est)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS docentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    titulo VARCHAR(120) NULL,
    profesion VARCHAR(120) NULL,
    CONSTRAINT fk_docente_persona FOREIGN KEY (persona_id)
        REFERENCES personas (id) ON DELETE CASCADE,
    UNIQUE KEY uq_docente_persona (persona_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS gestion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo TINYINT NOT NULL DEFAULT 1,
    UNIQUE KEY uq_gestion_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS niveles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    etiqueta VARCHAR(20) NOT NULL,
    UNIQUE KEY uq_niveles_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nivel_id INT NOT NULL,
    nombre VARCHAR(60) NOT NULL,
    etiqueta VARCHAR(20) NOT NULL,
    grado SMALLINT NULL,
    CONSTRAINT fk_curso_nivel FOREIGN KEY (nivel_id)
        REFERENCES niveles (id) ON DELETE CASCADE,
    UNIQUE KEY uq_curso_nivel_nombre (nivel_id, nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS paralelos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    etiqueta VARCHAR(10) NOT NULL,
    nombre VARCHAR(10) NOT NULL,
    CONSTRAINT fk_paralelo_curso FOREIGN KEY (curso_id)
        REFERENCES cursos (id) ON DELETE CASCADE,
    UNIQUE KEY uq_paralelo_curso_etiqueta (curso_id, etiqueta),
    UNIQUE KEY uq_paralelo_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    descripcion TEXT NULL,
    area VARCHAR(100) NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_materias_codigo (codigo),
    UNIQUE KEY uq_materias_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE materias
    ADD COLUMN IF NOT EXISTS descripcion TEXT NULL,
    ADD COLUMN IF NOT EXISTS area VARCHAR(100) NULL,
    ADD COLUMN IF NOT EXISTS estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO',
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ADD UNIQUE INDEX IF NOT EXISTS uq_materias_codigo (codigo),
    ADD UNIQUE INDEX IF NOT EXISTS uq_materias_nombre (nombre);

CREATE TABLE IF NOT EXISTS plan_curso_materia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    materia_id INT NOT NULL,
    horas_sem SMALLINT NULL,
    CONSTRAINT fk_plan_curso FOREIGN KEY (curso_id)
        REFERENCES cursos (id) ON DELETE CASCADE,
    CONSTRAINT fk_plan_materia FOREIGN KEY (materia_id)
        REFERENCES materias (id) ON DELETE CASCADE,
    UNIQUE KEY uq_plan (curso_id, materia_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS asignacion_docente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gestion_id INT NOT NULL,
    docente_id INT NOT NULL,
    materia_id INT NOT NULL,
    curso_id INT NOT NULL,
    paralelo_id INT NOT NULL,
    CONSTRAINT fk_asig_gestion FOREIGN KEY (gestion_id)
        REFERENCES gestion (id) ON DELETE CASCADE,
    CONSTRAINT fk_asig_docente FOREIGN KEY (docente_id)
        REFERENCES docentes (id) ON DELETE CASCADE,
    CONSTRAINT fk_asig_materia FOREIGN KEY (materia_id)
        REFERENCES materias (id) ON DELETE CASCADE,
    CONSTRAINT fk_asig_curso FOREIGN KEY (curso_id)
        REFERENCES cursos (id) ON DELETE CASCADE,
    CONSTRAINT fk_asig_paralelo FOREIGN KEY (paralelo_id)
        REFERENCES paralelos (id) ON DELETE CASCADE,
    UNIQUE KEY uq_asig (gestion_id, docente_id, materia_id, curso_id, paralelo_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS matriculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asignacion_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    CONSTRAINT fk_matricula_asig FOREIGN KEY (asignacion_id)
        REFERENCES asignacion_docente (id) ON DELETE CASCADE,
    CONSTRAINT fk_matricula_est FOREIGN KEY (estudiante_id)
        REFERENCES estudiantes (id) ON DELETE CASCADE,
    UNIQUE KEY uq_matricula (asignacion_id, estudiante_id),
    KEY ix_matriculas_asig (asignacion_id),
    KEY ix_matriculas_est (estudiante_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS evaluaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asignacion_id INT NOT NULL,
    titulo VARCHAR(120) NOT NULL,
    tipo ENUM('EXAMEN','TAREA','PROYECTO','PRACTICA','OTRO') NOT NULL DEFAULT 'OTRO',
    fecha DATE NOT NULL,
    ponderacion DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_eval_asig FOREIGN KEY (asignacion_id)
        REFERENCES asignacion_docente (id) ON DELETE CASCADE,
    UNIQUE KEY uq_eval_asig_titulo (asignacion_id, titulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluacion_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    calificacion DECIMAL(5,2) NOT NULL,
    observacion VARCHAR(255) NULL,
    CONSTRAINT fk_nota_eval FOREIGN KEY (evaluacion_id)
        REFERENCES evaluaciones (id) ON DELETE CASCADE,
    CONSTRAINT fk_nota_est FOREIGN KEY (estudiante_id)
        REFERENCES estudiantes (id) ON DELETE CASCADE,
    CONSTRAINT ck_nota_calificacion CHECK (calificacion >= 0 AND calificacion <= 100),
    UNIQUE KEY uq_nota_eval_est (evaluacion_id, estudiante_id),
    KEY idx_nota_est (estudiante_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS asistencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    asignacion_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    estado ENUM('PRESENTE','AUSENTE','TARDE','JUSTIFICADO') NOT NULL DEFAULT 'PRESENTE',
    observacion VARCHAR(255) NULL,
    CONSTRAINT fk_asistencia_asig FOREIGN KEY (asignacion_id)
        REFERENCES asignacion_docente (id) ON DELETE CASCADE,
    CONSTRAINT fk_asistencia_est FOREIGN KEY (estudiante_id)
        REFERENCES estudiantes (id) ON DELETE CASCADE,
    UNIQUE KEY uq_asistencia_unica (fecha, asignacion_id, estudiante_id),
    KEY idx_asistencia_fecha (fecha),
    KEY idx_asistencia_asig (asignacion_id),
    KEY idx_asistencia_est (estudiante_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gestion INT NOT NULL,
    asignacion_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    score INT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'NUEVO',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alerta_asig FOREIGN KEY (asignacion_id)
        REFERENCES asignacion_docente (id) ON DELETE CASCADE,
    CONSTRAINT fk_alerta_est FOREIGN KEY (estudiante_id)
        REFERENCES estudiantes (id) ON DELETE CASCADE,
    KEY idx_alerta_gestion (gestion),
    KEY idx_alerta_asig (asignacion_id),
    KEY idx_alerta_est (estudiante_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

