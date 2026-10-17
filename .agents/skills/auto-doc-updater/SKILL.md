---
name: auto-doc-updater
description: >-
  Crea o actualiza la documentación del proyecto basándose en los cambios recientes del código
  (archivos modificados, git diff, commits recientes). Se activa al solicitar "Crea documentacion",
  "Actualiza la documentacion", "Documenta los cambios", "Generate docs", o frases afines.
  Preserva y utiliza la documentación existente como base en lugar de sobrescribirla.
---

# Auto Doc Updater Skill

Esta skill guía al agente para inspeccionar los cambios recientes en el código fuente del proyecto y actualizar incrementalmente la documentación existente (por ejemplo `README.md`, archivos en `docs/`, `CHANGELOG.md`, o docstrings) sin borrar ni reemplazar la estructura original.

---

## Cuándo activar esta Skill
Activa esta skill cuando el usuario pida:
- "Crea documentación" / "Crea documentacion"
- "Actualiza la documentación" / "Actualiza la documentacion"
- "Documenta los cambios"
- "Genera docs de los cambios"
- "Update project documentation" / "Generate docs"

---

## Flujo de Trabajo

### Paso 1: Inspeccionar los Cambios Recientes
Ejecuta comandos de inspección en el repositorio usando la herramienta de comandos para entender qué ha cambiado:

1. **Cambios en el área de trabajo (sin confirmar y estacados):**
   - `git status`
   - `git diff` y `git diff --cached`
2. **Commits recientes y diferencias con la rama base (si aplica):**
   - `git log -n 5 --stat`
   - `git diff main...HEAD` o `git diff master...HEAD` (si existe rama previa)

Analiza qué módulos, funciones, APIs, parámetros o scripts fueron agregados, modificados o eliminados.

---

### Paso 2: Localizar la Documentación Existente
Busca en el repositorio la documentación existente para usarla como base:

1. Busca archivos Markdown clave en la raíz y subdirectorios:
   - `README.md`
   - `CHANGELOG.md`
   - `docs/` o `.github/`
2. Revisa las secciones existentes dentro de estos archivos usando `view_file` para entender el estilo, tono y estructura.

---

### Paso 3: Planificar las Actualizaciones Incrementales
Sigue estas reglas fundamentales de actualización:

- **REGLA DE ORO - No Sobrescribir**: NUNCA borres ni reemplaces el contenido previo relevante. Usa el documento existente como cimiento.
- **Insertar/Extender**: Añade nuevas secciones o amplía las secciones existentes donde los cambios aporten nuevo valor o funcionalidad.
- **Actualizar Firmas/Ejemplos**: Si se modificaron nombres de funciones, argumentos, scripts o endpoints, actualiza únicamente los fragmentos o tablas afectadas.
- **Registrar en CHANGELOG (si existe)**: Si hay un `CHANGELOG.md`, añade una entrada bajo la versión adecuada o la sección `[Unreleased]` detailing los cambios realizados.

---

### Paso 4: Aplicar los Cambios
Utiliza las herramientas `replace_file_content` o `multi_replace_file_content` para modificar los archivos de documentación de forma precisa y quirúrgica.

Si no existe ningún archivo de documentación previo (por ejemplo, el proyecto no tiene `README.md`), crea uno inicial estructurado y limpio usando `write_to_file`.

---

### Paso 5: Reportar y Verificar
Presenta al usuario un resumen conciso de:
- Qué archivos de documentación fueron actualizados o creados.
- Qué secciones específicas fueron ampliadas o corregidas según los cambios detectados.
