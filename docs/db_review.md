# Database Review for `academico`

This document summarizes structural and data quality findings identified while reviewing the provided MySQL dump for the `academico` database. The goal is to highlight issues that are likely to cause malfunctions or maintenance pain so they can be addressed.

## 1. Referential Integrity & Table Design

- **`alertas.gestion` is not a foreign key.** The column holds raw integers (e.g., `2025`) instead of referencing `gestion.id`. Because the `gestion` table already stores the school year with numeric primary keys, `alertas` should either store `gestion_id` (FK) or normalize the value into its own lookup to avoid orphaned records.
- **Redundant assignment tables.** Both `asignacion_docente` and `asignaciones` keep the relationship between docente, materia, curso y paralelo. Maintaining two almost identical tables invites drift (different unique constraints, different FK coverage). Consider consolidating into one table and exposing the other need as a view.
- **Partial soft-delete support.** Several tables (e.g., `asignaciones`, `matriculas`, `alertas`) expose `activo`/`eliminado_en` flags but lack triggers to keep them in sync (unlike `cursos` or `personas`). Updates must now be coordinated manually in application code. Adding consistent triggers or views would reduce human error.
- **`gestion.id` dual usage.** The table mixes numeric IDs (`1`) with year-like IDs (`2025`). Foreign keys that rely on auto-increment semantics (e.g., from `asignacion_docente`) will behave differently depending on which convention is followed. Stick to surrogate IDs (1,2,3,…) and keep the textual year in `nombre`.

## 2. Data Quality Problems

- **Invalid `anio_ingreso` values.** Several rows insert `0000` into a `YEAR` column even though the server SQL mode disables zero dates. Relying on this sentinel value breaks date calculations and may fail on stricter environments. Use `NULL` or the actual year.
- **Duplicated personas.** There are many `personas` rows with identical nombres/apellidos and empty CIs. Since empty strings get normalized to `NULL` in the generated `ci_comp_exp_key`, uniqueness is never enforced, leading to duplicates that propagate to docentes/estudiantes. Introduce a uniqueness rule (e.g., over name + birth date) or require actual CI numbers.
- **Misaligned enrollment data.** `matriculas` references `asignacion_docente.id` `1`, but that assignment belongs to gestion `1` while the student rows with `anio_ingreso=0000` appear to be placeholders. Verify that active students are enrolled in the correct gestion and that soft-deleted assignments cannot keep dangling matriculas.

## 3. Constraint & Index Observations

- **Overlapping unique keys in `asignacion_docente`.** Having both `uq_asig` (with `gestion_id`) and `uq_asig_doc` (without it) may block valid reassignment of the same docente to the same materia across different gestiones. If yearly reassignments are expected, drop or relax the second constraint.
- **Generated columns rely on enums.** Tables like `docentes`, `estudiantes`, `materias` and `usuarios` compute `activo` from enum state. Any future change to the enum literals must keep the generated logic aligned, otherwise toggling state will fail. Consider replacing with triggers or check constraints so changes stay DRY.
- **Collation drift.** Some tables use `utf8mb4_unicode_ci`, others default to `utf8mb4_0900_ai_ci`. Mixing collations can cause implicit conversion warnings and index usage issues. Align everything on a single collation (`utf8mb4_unicode_ci` or `utf8mb4_0900_ai_ci`) for consistency.

## 4. Operational Considerations

- **Triggers missing `DEFINER` portability.** Stored procedures and triggers are created with `DEFINER='root'@'localhost'`. Restoring on another server or using non-root accounts will fail unless `--definer` is stripped or the definer exists. Prefer `SQL SECURITY INVOKER` or omit explicit definers.
- **No archival for audit logs.** `audit_logs` keeps all entries forever and only uses soft-delete flags. Long-term growth can hurt performance; consider partitioning by date or introducing a retention policy.
- **Views without security filtering.** Views such as `vw_permisos_por_usuario` expose all roles/vistas combinations even when the underlying rows are soft-deleted. Add `WHERE` clauses for `activo=1` to prevent returning stale permissions.

## Next Steps

1. Normalize foreign keys (`alertas`, `gestion`, redundant tables) and align unique constraints with real business rules.
2. Clean current data (remove `0000` years, deduplicate personas) and enforce it via stricter constraints or application validation.
3. Standardize soft-delete handling, collations, and trigger definers to ease future migrations.

Addressing these items should resolve the biggest inconsistencies and make the schema easier to evolve.
