# GitHub Copilot en VS Code — Guía y Documentación Completa

> Guía de referencia **y** explicación conceptual del *Context Engineering* con GitHub Copilot en Visual Studio Code.
> Basada en la documentación oficial: [Customize AI in VS Code](https://code.visualstudio.com/docs/copilot/customization/overview)

---

## 📑 Tabla de contenido

1. [El concepto: por qué customizar](#1-el-concepto-por-qué-customizar)
2. [Mapa mental de las piezas](#2-mapa-mental-de-las-piezas)
3. [`/init` y `copilot-instructions.md`](#3-init-y-copilot-instructionsmd)
4. [Instructions por archivo (`*.instructions.md`)](#4-instructions-por-archivo-instructionsmd)
5. [Prompt files (`*.prompt.md`)](#5-prompt-files-promptmd)
6. [Agent Skills (`SKILL.md`)](#6-agent-skills-skillmd)
7. [Custom Agents (`*.agent.md`)](#7-custom-agents-agentmd)
8. [Tools disponibles para un Custom Agent](#8-tools-disponibles-para-un-custom-agent)
9. [Orquestación: agentes que hablan con agentes](#9-orquestación-agentes-que-hablan-con-agentes)
10. [Hooks (automatización determinística)](#10-hooks-automatización-determinística)
11. [MCP Servers](#11-mcp-servers)
12. [Agent Plugins (preview)](#12-agent-plugins-preview)
13. [Combinando todo: recetas prácticas](#13-combinando-todo-recetas-prácticas)
14. [Orquestación con handoffs (Planner, BE, FE, QA)](#14-orquestación-con-handoffs-planner-be-fe-qa)
15. [El AI-SDLC: orquestación de agentes con validación humana](#15-el-ai-sdlc-orquestación-de-agentes-con-validación-humana)
16. [Adopción en proyectos existentes y monorepos grandes](#16-adopción-en-proyectos-existentes-y-monorepos-grandes)
17. [Operar y controlar al agente (modos, contexto, loop, permisos)](#17-operar-y-controlar-al-agente-modos-contexto-loop-permisos)
18. [Estructura final del proyecto](#18-estructura-final-del-proyecto)
19. [Tabla de comandos y troubleshooting](#19-tabla-de-comandos-y-troubleshooting)
20. [Tips para instrucciones efectivas](#20-tips-para-instrucciones-efectivas)
21. [Recursos oficiales](#21-recursos-oficiales)

---

## 1. El concepto: por qué customizar

Los modelos de IA tienen conocimiento general amplio, **pero no conocen tu codebase ni las prácticas de tu equipo**.

> *"Think of the AI as a skilled new team member: it writes great code, but doesn't know your conventions, architecture decisions, or preferred libraries."* — VS Code Docs

La customización es cómo le das ese contexto para que las respuestas reflejen **tus estándares y tu arquitectura**. Esto es lo que se conoce como **Context Engineering**.

**Regla de oro de VS Code:** empieza con instrucciones globales, y agrega capas especializadas *sólo cuando aparece una necesidad recurrente*. No configures todo de una vez.

### Referencia rápida: ¿qué herramienta uso?

| Necesidad | Herramienta | Cuándo aplica |
|---|---|---|
| Reglas para **todo** el proyecto | `copilot-instructions.md` | Siempre, en cada request |
| Reglas por **tipo de archivo** | `*.instructions.md` | Cuando el archivo coincide con el glob |
| Tarea **repetible** bajo demanda | `*.prompt.md` | Cuando invocas el slash command |
| **Workflow** multi-paso con scripts | Agent Skills | Cuando la tarea coincide con la descripción |
| **Persona** de IA especializada | Custom Agents | Cuando lo seleccionas o un agente te delega |
| Conectar a **APIs/DBs externas** | MCP Servers | Cuando la tarea requiere la herramienta |
| **Garantizar** que algo ocurra | Hooks | En un evento del ciclo del agente |

---

## 2. Mapa mental de las piezas

```
Editor (sin interrumpir tu flujo)
  ├── Inline Suggestions       ← mientras tipeas (Tab / Esc)
  ├── Next Edit Suggestions    ← predice tu próximo cambio
  ├── Inline Chat (⌘I)         ← edits in-place con diff
  └── Smart Actions            ← commit msg, fix, rename, explain

Agentes (tareas completas end-to-end)
  ├── Local Agent              ← interactivo, contexto del editor
  ├── Background Agent         ← autónomo, Git worktree, paralelo
  ├── Cloud Agent              ← branch + PR automático
  ├── Plan Agent               ← plan → delegar implementación
  └── Third-party (Claude, Codex)

Context Engineering (lo que configuras una vez, se commitea al repo)
  ├── copilot-instructions.md  ← SIEMPRE activo
  ├── *.instructions.md        ← por archivo/carpeta (glob)
  ├── *.prompt.md              ← slash commands
  ├── *.agent.md               ← personas especializadas + orquestación
  ├── Skills (SKILL.md)        ← workflows reutilizables y portables
  ├── Hooks                    ← automatización determinística
  ├── MCP Servers              ← conexión a APIs / datos externos
  └── Agent Plugins (preview)  ← bundle instalable de todo lo anterior
```

**Cómo se relacionan (jerarquía de "peso"):**

- **Instructions globales** (`copilot-instructions.md`) = *siempre* en el contexto (barato, corto). Las **instructions por archivo** (`*.instructions.md`) sólo se cargan cuando el archivo abierto coincide con su glob `applyTo`.
- **Prompts / Skills / Agents** = se cargan *bajo demanda* (progressive loading), por eso puedes tener muchos sin saturar el contexto.
- **Hooks** = no dependen del modelo; se ejecutan *sí o sí* en un evento.
- **MCP** = amplía *qué puede hacer* el agente (nuevas tools).

---

## 3. `/init` y `copilot-instructions.md`

### ¿Qué significa?

`/init` es un **slash command** que arranca todo tu setup de Context Engineering. Es el punto de partida.

### ¿Qué hace?

En el chat de Copilot (modo Agent), escribes:

```
/init
```

Copilot **analiza tu workspace** (stack, dependencias, estructura de carpetas, patrones existentes) y genera automáticamente:

```
.github/copilot-instructions.md
```

Este archivo se inyecta **en cada request** de chat de forma automática.

### Ventajas de tenerlo

- ✅ No tienes que repetir el contexto de tu proyecto en cada prompt.
- ✅ Todo el equipo comparte el mismo contexto (se commitea al repo).
- ✅ Copilot deja de "adivinar" tu stack y respeta tus convenciones.
- ✅ Es la base sobre la que se apoyan prompts, agents y skills.

### Cómo se crea a mano

No necesitas `/init`. Puedes crear el archivo directamente:

**Archivo:** `.github/copilot-instructions.md`

```markdown
# Proyecto: TaskFlow

## Stack
- Backend: ASP.NET Core 8 Web API (C#), Entity Framework Core, PostgreSQL
- Frontend: Angular 17 standalone components + signals
- Tests: xUnit (backend), Jasmine/Karma (frontend)

## Convenciones que SÍ importan (lo no obvio)
- Usar inyección de dependencias por constructor — nunca `new` de un servicio dentro de otro.
- Los endpoints devuelven `ActionResult<T>` con los helpers `Ok()`, `NotFound()`, etc., nunca objetos crudos.
- El acceso a datos va SIEMPRE por un repository/EF DbContext, nunca SQL inline en el controller.
- En Angular usar signals para estado local, no `BehaviorSubject`, salvo streams reales.

## Patrones a evitar
- No usar `dynamic` ni `object` en C# donde exista un tipo concreto.
- No poner lógica de negocio en el controller — va en la capa de servicios.
- No suscribirse a Observables en el template sin `async` pipe (memory leaks).
```

> **Nota:** no hace falta frontmatter en `copilot-instructions.md`. Es Markdown puro.

### Alternativas: `AGENTS.md` y `CLAUDE.md`

VS Code también reconoce como instrucciones **always-on** (equivalentes a `copilot-instructions.md`):

- **`AGENTS.md`** — estándar reconocido por múltiples agentes (encaja con la portabilidad de los Skills). Va en la raíz del workspace y, de forma **experimental**, admite un `AGENTS.md` **por subcarpeta** (activando `chat.useNestedAgentsMdFiles`) — útil en monorepos para reglas por módulo sin depender sólo de `applyTo` (ver §16).
- **`CLAUDE.md`** — se aplica como instrucciones always-on, igual que `AGENTS.md`.

Puedes convivir con los tres; elige uno como fuente principal para no duplicar reglas.

### Cómo mantenerlo

- **Revísalo después de `/init`** — la IA infiere el stack, pero no las *decisiones de arquitectura*. Agrega el "por qué".
- **Enfócate en lo no obvio.** Omite lo que ya enforcea un linter/formatter.
- **Actualízalo cuando cambien las reglas del equipo** (nueva librería preferida, nuevo patrón).
- **Versiona en git** — es la fuente de verdad compartida.
- **Diagnóstico:** click derecho en el Chat → `Diagnostics` para ver qué instrucciones se cargaron.

---

## 4. Instructions por archivo (`*.instructions.md`)

### ¿Qué es?

Reglas que aplican **sólo a una parte del codebase**, no a todo. Por ejemplo: reglas distintas para `backend/` que para `frontend/`.

### El formato

**Archivo:** `.github/instructions/backend.instructions.md`

```markdown
---
name: 'Backend rules'
description: 'Convenciones para el código de backend .NET'
applyTo: 'backend/**/*.cs'   # glob pattern — sin esto, no aplica automáticamente
---

# Reglas de backend (ASP.NET Core)
- Un controller por recurso; hereda de `ControllerBase`, no de `Controller`.
- Validar el input con FluentValidation antes de llegar al servicio.
- Toda operación async devuelve `Task<ActionResult<T>>` y usa `CancellationToken`.
- Nunca exponer entidades EF directamente — mapear a DTOs.
```

**El campo clave es `applyTo`** (un glob):

| `applyTo` | Aplica a |
|---|---|
| `backend/**/*.cs` | Todos los `.cs` del backend |
| `**/*Tests.cs` | Todos los archivos de test de xUnit |
| `frontend/**/*.component.ts` | Componentes Angular |
| *(omitido)* | No se aplica automáticamente (sólo referenciable) |

### Ventajas

- ✅ Reglas específicas sin contaminar el contexto global.
- ✅ Copilot sólo las carga cuando trabajas en archivos que coinciden con el glob → **ahorra contexto**.
- ✅ Ideal para monorepos con distintos lenguajes/frameworks por carpeta.

### Cómo se hace

Con IA:
```
/create-instruction
```
Describes la convención y Copilot genera el archivo con el `applyTo` correcto. O lo creas a mano con el formato de arriba.

### Prioridad cuando hay conflicto

1. **Instrucciones personales (user-level)** — viven en tu perfil de usuario (no en el repo) y aplican a **todos** tus workspaces. Se crean con *New Instructions (User)* en el editor de Agent Customizations (comando `Chat: New Instructions File`). Útiles para preferencias tuyas que no quieres imponer al equipo.
2. **Instrucciones del repo** (`.github/copilot-instructions.md` + `*.instructions.md`) — compartidas con el equipo vía git.
3. **Instrucciones de la organización** — definidas a nivel de organización (GitHub), aplican a todos sus repos.

---

## 5. Prompt files (`*.prompt.md`)

### ¿Qué es?

Una **tarea repetible empaquetada como slash command**. En vez de escribir el mismo prompt largo cada vez ("créame un controller con su servicio, DTO y validación siguiendo el patrón X..."), lo guardas una vez y lo invocas con `/new-controller`.

### El formato

**Archivo:** `.github/prompts/new-controller.prompt.md`

```markdown
---
description: 'Scaffoldea un nuevo controller de API con su servicio y DTO'
name: 'new-controller'
agent: agent
tools: ['edit/createFile', 'read/readFile', 'edit/editFiles']   # sintaxis set/tool (ver §8)
---

Crea un nuevo controller REST para el recurso `${input:name}` en
`backend/Controllers/${input:name}Controller.cs`, siguiendo el patrón existente
en `backend/Controllers/ProductsController.cs`.
Incluye:
- controller que hereda de ControllerBase con `[ApiController]` y ruta `[Route("api/[controller]")]`
- interfaz `I${input:name}Service` + implementación registrada por DI
- DTOs de request/response (no exponer entidades EF)
- endpoints async con `CancellationToken` y `ActionResult<T>`
```

- **`${input:name}`** → variable que el usuario rellena al invocar.
- **`tools`** → limita qué herramientas puede usar ese prompt.
- **`agent: agent`** → corre en modo agente.

### Cómo invocarlo

```
/new-controller
```
Copilot te pide el `name` y ejecuta el prompt.

### Ventajas

- ✅ Consistencia: la misma tarea siempre se hace igual.
- ✅ Onboarding: un junior invoca `/create-pr` sin saber el proceso interno.
- ✅ Reutiliza instrucciones (referencia con Markdown links en vez de duplicar).

### Cómo se crea

```
/create-prompt
```

### Cómo mantenerlo

- Retira los prompts que ya nadie usa — un menú `/` saturado estorba.
- Cuando cambie el patrón que scaffoldean (p.ej. el ejemplo de referencia), actualiza el prompt.
- Versiónalos en git y revísalos en PR como cualquier código.

---

## 6. Agent Skills (`SKILL.md`)

### ¿Qué es?

La pieza más potente para **workflows complejos y reutilizables** (deploy, testing, debugging). A diferencia de un prompt file, un Skill puede incluir **scripts ejecutables y ejemplos de referencia**, no sólo instrucciones.

> Docs: [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
> Es un **open standard** ([agentskills.io](https://agentskills.io)) — portable entre VS Code, Copilot CLI y el coding agent.

### Estructura de carpetas

> ⚠️ El nombre del directorio **DEBE coincidir** con el campo `name` del `SKILL.md`.

```
.github/skills/
└── ef-migration/         ← nombre del dir = campo `name`
    ├── SKILL.md          ← instrucciones principales (REQUERIDO)
    ├── scripts/          ← scripts ejecutables (opcional)
    └── examples/         ← ejemplos de referencia (opcional)
```

Ubicaciones válidas: `.github/skills/`, `.claude/skills/`, `.agents/skills/` (proyecto) · `~/.copilot/skills/`, `~/.claude/skills/` (personales).

### El formato del SKILL.md

```markdown
---
name: ef-migration                # REQUERIDO — igual al nombre del directorio (max 64 chars; minúsculas, números y guiones)
description: >                    # REQUERIDO — QUÉ hace y CUÁNDO usarlo (máx. 1024 chars)
  Crea y aplica migraciones de Entity Framework Core de forma segura.
  Úsalo cuando cambies una entidad o el DbContext y necesites actualizar la base de datos.
argument-hint: '[nombre-migracion]'  # opcional — hint en el input del chat
user-invocable: true              # opcional — aparece como slash command (default: true)
disable-model-invocation: false   # opcional — si false, el agente lo carga solo cuando aplica
---

# Migración de EF Core

1. Ejecuta `scripts/build.sh` para compilar y detectar errores antes de migrar.
2. Si compila, corre `dotnet ef migrations add $ARGUMENTS` en `backend/`.
3. Revisa el archivo de migración generado (verifica que no borre columnas por accidente).
4. Aplica con `dotnet ef database update` y reporta el resultado.

Ver `examples/migracion-esperada.cs` como referencia del formato correcto.
```

### Cómo lo carga Copilot: **3 niveles progresivos** (la clave de la eficiencia)

1. **Discovery** — siempre lee sólo `name` + `description` (ligero, siempre en contexto).
2. **Carga de instrucciones** — cuando el request coincide con la descripción, carga el body del `SKILL.md`.
3. **Acceso a recursos** — sólo carga `scripts/` y `examples/` cuando el body los referencia.

👉 Por eso puedes tener **decenas de skills instalados sin saturar el contexto**.

### Skills vs. Prompts vs. Instructions

| Aspecto | Agent Skills | Custom Instructions | Prompt Files |
|---|---|---|---|
| Propósito | Workflows especializados | Estándares de código | Prompts puntuales |
| Contenido | Instrucciones + scripts + ejemplos | Sólo instrucciones | Sólo template |
| Portabilidad | VS Code, CLI, cloud agent | VS Code + GitHub.com | Local VS Code |
| Carga | On-demand, progresiva | Globales: siempre · por archivo: al coincidir el glob | Por conversación |
| Estándar | Abierto (agentskills.io) | VS Code | VS Code |

### Cómo se crea

```
/create-skill
```

> ⭐ **No arranques de cero.** La galería oficial **[Awesome GitHub Copilot](https://awesome-copilot.github.com/)** tiene **skills, agents, instructions, prompts y plugins** contribuidos por la comunidad, listos para copiar y adaptar. Es el mejor lugar para tomar ideas al crear tus propios skills y custom agents (§7). Ver también §21.

### Cómo mantenerlo

- **El `description` es lo más crítico**: de él depende el *discovery* (nivel 1). Si el skill deja de activarse cuando debería, casi siempre es la descripción, no el body.
- Divide un skill que crece demasiado en varios más específicos.
- Mantén los `scripts/` probados: si el comando subyacente cambia, el skill se rompe en silencio.

---

## 7. Custom Agents (`*.agent.md`)

### ¿Qué es?

Una **persona de IA especializada** con su propio prompt de sistema, su set de tools restringido y su modelo. Ejemplos: un *DBA*, un *Security Reviewer*, un *.NET API Expert*, un *Angular Expert*, un *Planner de solo-lectura*.

> Docs: [Custom agents in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-agents) — disponibles desde VS Code 1.106.
> Antes se llamaban **custom chat modes** (`.chatmode.md` → renombrar a `.agent.md`).

### El formato completo

**Archivo:** `.github/agents/dotnet-api-expert.agent.md`

```markdown
---
name: 'dotnet-api-expert'
description: 'Especialista en ASP.NET Core Web API. Úsalo para crear o modificar controllers y servicios.'
tools: ['edit', 'search/codebase', 'execute/runInTerminal']   # ver sección 8
agents: ['security-reviewer']       # subagentes que puede invocar ([] = ninguno, '*' = todos)
model: 'Claude Sonnet 4.5 (copilot)'  # opcional — modelo específico o array de prioridad
user-invocable: true                # opcional — aparece en el dropdown de agentes
target: vscode                      # opcional — 'vscode' o 'github-copilot'
handoffs:                           # opcional — botones de transición a otro agente
  - label: 'Revisar seguridad'
    agent: security-reviewer
    prompt: 'Revisa el código de la API buscando problemas de seguridad.'
    send: false                     # true = envía el prompt automáticamente
---

Eres un experto en ASP.NET Core 8 con C#.
Sigues arquitectura por capas (Controller → Service → Repository) e inyección
de dependencias por constructor. Mapeas entidades EF a DTOs, nunca las expones.
Siempre validas que compile con `dotnet build` antes de dar por terminada una tarea.
```

### Campos del frontmatter

| Campo | Qué hace |
|---|---|
| `name` | Identificador (default: nombre del archivo) |
| `description` | Texto en el dropdown / placeholder |
| `argument-hint` | Guía en el input del chat |
| `tools` | Array de tools / tool sets permitidos (ver §8) |
| `agents` | Subagentes invocables (`[]`, lista, o `*`) |
| `model` | Modelo único o array de prioridad (intenta en orden) |
| `user-invocable` | Si aparece en el dropdown (default: true) |
| `disable-model-invocation` | Si es `true`, **impide** que otros agentes lo invoquen como subagente (default: `false` = sí puede ser delegado) |
| `target` | Entorno: `vscode` o `github-copilot` |
| `mcp-servers` | Config JSON de MCP servers — **sólo** para `target: github-copilot` (en agentes locales, ver §11) |
| `handoffs` | Transiciones guiadas a otros agentes |
| `hooks` | Hooks con scope de agente (Preview) |

### Ventajas

- ✅ **Enfoque**: un agente de solo-lectura no puede romper archivos por accidente (restringes `tools`).
- ✅ **Seguridad**: un *Security Reviewer* sin permiso de `edit` sólo analiza, no modifica.
- ✅ **Modelo por tarea**: usa un modelo potente para arquitectura y uno rápido para tareas mecánicas.
- ✅ **Reutilizable y versionado** en el repo.

### Compatibilidad con Claude Code

VS Code también detecta archivos `.md` en `.claude/agents/` con el formato de sub-agents de Claude Code — **las mismas definiciones funcionan en ambas herramientas**.

### Cómo se crea

```
/create-agent
```

### Cómo mantenerlo

- Revisa el `tools` cuando cambie el rol: quítale lo que ya no use (mínimo privilegio).
- Mantén sincronizados `agents:` y `handoffs:` con los agentes que realmente existen — una referencia a un agente borrado rompe la orquestación.
- Ajusta el `description` si el agente deja de aparecer/delegarse cuando debería.

> **Campo `hooks` (Preview):** además de los hooks de proyecto (§10), un `.agent.md` puede declarar `hooks:` en su frontmatter para que **sólo** se ejecuten cuando ese agente está activo (requiere habilitar `chat.useCustomAgentHooks`). Útil, por ejemplo, para forzar un formateo únicamente durante ese agente.

---

## 8. Tools disponibles para un Custom Agent

Esta es la pregunta clave: **¿qué puedo poner en el campo `tools`?**

Puedes usar tres tipos: **tool sets** (grupos), **tools individuales**, y **tools de MCP/extensiones**.

### Tool Sets (grupos — la forma más cómoda)

Poner el nombre del set habilita todas sus tools de golpe:

| Tool set | Qué habilita |
|---|---|
| `read` | Leer archivos del workspace |
| `edit` | Crear/editar archivos y directorios |
| `search` | Buscar archivos y contenido en el workspace |
| `execute` | Ejecutar tasks, comandos de terminal y tests |
| `web` | Acceder a contenido web |
| `browser` | Interactuar con el browser integrado (navegar, click, screenshot) |
| `vscode` | Funcionalidad de VS Code y desarrollo de extensiones |
| `agent` | Delegar tareas a otros agentes (subagentes) |

### Tools individuales (control fino)

Si quieres precisión, referencia la tool exacta con la sintaxis `set/tool`:

| Tool | Qué hace |
|---|---|
| `read/readFile` | Leer el contenido de un archivo |
| `read/problems` | Leer issues del panel Problems |
| `read/terminalLastCommand` | Último comando de terminal y su output |
| `read/terminalSelection` | Selección actual en la terminal |
| `edit/createFile` | Crear un archivo nuevo |
| `edit/createDirectory` | Crear un directorio nuevo |
| `edit/editFiles` | Aplicar edits a archivos existentes |
| `edit/editNotebook` | Editar un notebook |
| `search/codebase` | Búsqueda semántica de contexto relevante |
| `search/fileSearch` | Buscar archivos por glob |
| `search/textSearch` | Buscar texto en archivos |
| `search/listDirectory` | Listar archivos de un directorio |
| `search/usages` | "Find References" + "Go to Definition" + "Find Implementation" |
| `search/changes` | Lista de cambios del control de versiones |
| `execute/runInTerminal` | Ejecutar un comando en la terminal |
| `execute/getTerminalOutput` | Obtener output de un comando en ejecución |
| `execute/createAndRunTask` | Crear y correr una task |
| `execute/runNotebookCell` | Ejecutar una celda de notebook |
| `execute/testFailure` | Info de tests que fallaron |
| `web/fetch` | Traer el contenido de una página web |
| `agent/runSubagent` | Correr un subagente aislado (orquestación) |
| `githubRepo` | Búsqueda semántica en un repo de GitHub |
| `githubTextSearch` | Búsqueda de texto en GitHub |
| `newWorkspace` | Crear un workspace nuevo |
| `selection` | Obtener la selección actual del editor |
| `todos` | Trackear progreso con una lista de tareas |
| `vscode/runCommand` | Ejecutar un comando de VS Code |
| `vscode/extensions` | Buscar/preguntar sobre extensiones |
| `vscode/installExtension` | Instalar una extensión |
| `vscode/askQuestions` | Que el agente haga preguntas clarificadoras |
| `vscode/VSCodeAPI` | Preguntar sobre la API de VS Code |

> En el chat, estas tools se referencian con `#` (ej. `#search/codebase`, `#web/fetch`). En el frontmatter YAML van sin `#`.

### Tools de MCP y extensiones

Si conectas un **MCP Server** (§11) o instalas una extensión que aporta tools, esas tools también aparecen y puedes ponerlas en el array `tools`.

### Estrategia recomendada de `tools`

```yaml
# Agente de solo-lectura (planner / reviewer) — NO puede modificar nada
tools: ['read', 'search/codebase', 'search/usages']

# Agente implementador — puede editar y ejecutar
tools: ['read', 'edit', 'search', 'execute/runInTerminal']

# Agente orquestador — puede delegar
tools: ['read', 'search/codebase', 'agent']   # ¡el set 'agent' es obligatorio para orquestar!
```

**Principio:** dale a cada agente **el mínimo set de tools que necesita**. Un reviewer sin `edit` es un reviewer que no puede romper nada.

---

## 9. Orquestación: agentes que hablan con agentes

Hay **dos mecanismos** para que un agente colabore con otro. No son lo mismo.

### Mecanismo A — Subagentes (`agents` + tool `agent`)

Un agente **delega** una subtarea a otro agente, que corre en un **contexto aislado** y devuelve el resultado. El agente padre sigue en control.

**Requisitos:**
1. Listar el subagente en el campo `agents`.
2. Incluir el tool set `agent` (o `agent/runSubagent`) en `tools`.

**Ejemplo — un orquestador que delega:**

**Archivo:** `.github/agents/feature-orchestrator.agent.md`

```markdown
---
name: 'feature-orchestrator'
description: 'Coordina la implementación completa de una feature delegando a especialistas.'
tools: ['read', 'search/codebase', 'agent']   # 'agent' = puede invocar subagentes
agents: ['dotnet-api-expert', 'angular-expert', 'security-reviewer', 'test-writer']  # a quiénes puede delegar
model: 'Claude Sonnet 4.5 (copilot)'
---

Eres un orquestador. Tu trabajo es coordinar, NO escribir código directamente.

Flujo (feature end-to-end):
1. Delega el endpoint de la API al subagente `dotnet-api-expert`.
2. Delega la pantalla que lo consume al subagente `angular-expert`.
3. Cuando terminen, delega la revisión al subagente `security-reviewer`.
4. Finalmente, delega los tests al subagente `test-writer`.
5. Resume los resultados de cada subagente para el usuario.
```

Los subagentes (`dotnet-api-expert`, etc.) son archivos `.agent.md` independientes. Cada uno tiene su propio `tools` y `model`.

> **Nota:** para que un agente se pueda invocar a sí mismo recursivamente, hay que activar `chat.subagents.allowInvocationsFromSubagents`.

**Diagrama:**

```
feature-orchestrator  (solo-lectura + delegación)
   │
   ├──▶ dotnet-api-expert   (edit + runInTerminal)   → crea el controller + servicio
   │
   ├──▶ angular-expert      (edit + runInTerminal)   → crea el componente que lo consume
   │
   ├──▶ security-reviewer   (solo-lectura)           → audita el código
   │
   └──▶ test-writer         (edit)                    → escribe los tests (xUnit + Jasmine)
```

**Los subagentes son archivos `.agent.md` normales.** Siguen el patrón de §7; sólo cambian el rol y las tools. Ejemplos mínimos de los que faltan:

```markdown
--- .github/agents/angular-expert.agent.md ---
name: 'angular-expert'
description: 'Especialista en Angular 17. Crea componentes standalone que consumen la API.'
tools: ['edit', 'search/codebase', 'execute/runInTerminal']
---
Eres experto en Angular 17 (standalone + signals). Usas el `async` pipe, tipas todo y
validas con `ng build` antes de terminar.
```

```markdown
--- .github/agents/security-reviewer.agent.md ---
name: 'security-reviewer'
description: 'Audita código buscando vulnerabilidades. Sólo lee, no modifica.'
tools: ['read', 'search/codebase', 'search/usages']   # ¡sin 'edit'! solo audita
---
Eres un revisor de seguridad. Buscas inyección, auth rota, secretos hardcodeados y
validación faltante. Reportas hallazgos; no editas.
```

`test-writer` sigue el mismo molde (rol: escribir tests; `tools: ['read', 'edit', 'execute/runInTerminal']`).

### Mecanismo B — Handoffs (transiciones guiadas por el humano)

En vez de delegar automáticamente, el agente termina su respuesta y muestra **botones** para pasar a otro agente con contexto pre-cargado. **El desarrollador aprueba cada transición.**

```yaml
handoffs:
  - label: 'Implementar el plan'
    agent: implementation-agent
    prompt: 'Implementa el plan que acabamos de definir.'
    send: false      # false = rellena el prompt pero espera tu OK; true = lo envía solo
  - label: 'Revisar seguridad'
    agent: security-reviewer
    prompt: 'Revisa el código buscando vulnerabilidades.'
    send: true
```

Después de cada respuesta aparecen los botones. Flujo típico:

```
Plan Agent  →  [botón: Implementar]  →  Implementation Agent  →  [botón: Revisar]  →  Security Reviewer
```

### Subagentes vs. Handoffs — ¿cuándo cada uno?

| | Subagentes (`agents`) | Handoffs |
|---|---|---|
| Quién decide la transición | El **agente** (automático) | El **humano** (click en botón) |
| Contexto | Aislado por subagente | Compartido, pre-cargado |
| Control | Padre orquesta todo | Paso a paso, con aprobación |
| Uso ideal | Pipeline autónomo | Workflow supervisado (Plan→Impl→Review) |

---

## 10. Hooks (automatización determinística)

### ¿Qué es?

Comandos shell que se ejecutan en **puntos fijos del ciclo del agente**. A diferencia de las instrucciones (que *guían*), los hooks **garantizan** que algo ocurre — sin importar cómo fue el prompt.

> Docs: [Agent hooks in VS Code](https://code.visualstudio.com/docs/copilot/customization/hooks)

### Eventos disponibles

| Evento | Cuándo dispara | Uso típico |
|---|---|---|
| `SessionStart` | Al iniciar sesión | Inyectar contexto, validar estado |
| `UserPromptSubmit` | Al enviar un prompt | Auditar, añadir contexto |
| `PreToolUse` | Antes de invocar una tool | **Bloquear operaciones peligrosas** |
| `PostToolUse` | Después de una tool | **Formatter/linter automático** |
| `PreCompact` | Antes de compactar el contexto | Exportar estado |
| `SubagentStart` | Al lanzar un subagente | Inicializar recursos |
| `SubagentStop` | Al terminar un subagente | Agregar resultados |
| `Stop` | Al finalizar la sesión | Reportes, limpieza |

### Ubicación

```
.github/hooks/            ← hooks del proyecto (se commitean)
.claude/settings.json     ← hooks locales del workspace
~/.copilot/hooks          ← hooks personales, formato nativo Copilot (todos los proyectos)
~/.claude/settings.json   ← hooks personales, formato Claude (todos los proyectos)
```

### Cómo controla al agente (exit codes)

| Exit code | Comportamiento |
|---|---|
| `0` | Éxito — el agente continúa |
| `2` | Error bloqueante — detiene la operación y muestra el error al modelo |
| Otro | Warning — avisa pero continúa |

**Dos formas de bloquear (no las confundas):**

- **Exit code `2`** — bloqueo *simple*: detiene el procesamiento y pasa `stderr` al modelo. Útil cuando basta con "parar y avisar".
- **Salida JSON con `permissionDecision: "deny"`** (y exit `0`) — control *fino* sobre una sola invocación de tool en `PreToolUse`: `allow` / `deny` / `ask`, **sin detener la sesión**. Es lo que usan los ejemplos de abajo porque permiten dejar pasar el resto.

### Ejemplo: auto-formatear tras cada edit (`.cs` con dotnet format, `.ts` con Prettier)

**Archivo:** `.github/hooks/post-edit.json`

```json
{
  "hooks": {
    "PostToolUse": [
      { "type": "command", "command": ".github/hooks/scripts/format-on-edit.sh", "timeout": 60 }
    ]
  }
}
```

**Archivo:** `.github/hooks/scripts/format-on-edit.sh`

```bash
#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.filePath // empty')
if [[ "$FILE" == *.cs ]]; then
  # dotnet format espera una ruta RELATIVA al proyecto en --include, pero VS Code
  # entrega filePath ABSOLUTO. Entramos al proyecto y pasamos la ruta relativa.
  ( cd backend && dotnet format --include "${FILE#*/backend/}" )
  echo '{"continue": true, "systemMessage": "✅ dotnet format aplicado en '"$FILE"'"}'
elif [[ "$FILE" == *.ts || "$FILE" == *.html || "$FILE" == *.scss ]]; then
  npx prettier --write "$FILE"
  echo '{"continue": true, "systemMessage": "✅ Prettier aplicado en '"$FILE"'"}'
else
  echo '{"continue": true}'
fi
```

```bash
chmod +x .github/hooks/scripts/format-on-edit.sh   # una sola vez
```

**Resultado:** cada vez que el agente edite un `.cs`, corre `dotnet format`; si toca un `.ts`/`.html`/`.scss` de Angular, corre Prettier — sin que nadie lo pida.

### Ejemplo: bloquear comandos destructivos (`rm -rf`, `DROP TABLE`)

**Archivo:** `.github/hooks/scripts/block-dangerous-commands.sh`

```bash
#!/bin/bash
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# -i = case-insensitive; [[:space:]]+ tolera espacios/tabs múltiples. Es una HEURÍSTICA,
# no una lista exhaustiva: cúbrela con permisos reales, no confíes solo en el patrón.
if [[ "$TOOL" == "runInTerminal" ]] && echo "$COMMAND" | grep -qiE "rm[[:space:]]+-[rf]+|drop[[:space:]]+table|delete[[:space:]]+from|truncate[[:space:]]+table"; then
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Comando bloqueado por política de seguridad"}}'
  exit 0
fi
echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'
```

Registrado en un `PreToolUse`. **Crear con IA:** `/create-hook`.

---

## 11. MCP Servers

### ¿Qué es?

**Model Context Protocol** — el estándar para conectar el agente a **tus propias tools, bases de datos y servicios**. Le da al agente capacidades que no vienen de fábrica (consultar tu DB real, tu Jira, tu AWS, etc.).

> Docs: [MCP Servers in VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)

### Para qué sirve

- Trabajar con **datos reales del proyecto**, no sólo código.
- Ejemplos: un MCP de PostgreSQL para consultar el schema real; un MCP de AWS para revisar recursos desplegados; un MCP de GitHub para issues/PRs.

### Cómo se registra (paso previo)

Antes de poder usar un MCP server hay que **declararlo**. En VS Code se hace en `.vscode/mcp.json`
(workspace) o en la config de usuario — o con el comando `MCP: Add Server`:

```json
// .vscode/mcp.json
{
  "servers": {
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/taskflow"]
    }
  }
}
```

Una vez declarado y arrancado (y confiado la primera vez), sus tools aparecen en el chat.

### Cómo se usa en un custom agent

Ya registrado, las tools del MCP se **listan en el campo `tools`**, igual que las built-in:

```yaml
---
name: 'db-analyst'
description: 'Analiza el schema real de la base de datos.'
tools: ['read', 'search/codebase', 'postgres/query']   # 'postgres/query' viene del MCP registrado arriba
---
Eres un analista de datos. Consulta el schema real antes de sugerir migraciones.
```

> ⚠️ **No confundas con el campo `mcp-servers` del frontmatter.** Ese campo sólo aplica a
> custom agents con `target: github-copilot` y su valor es **config JSON** del server (no una lista
> de nombres). Para un agente **local** de VS Code no se usa: basta declarar el server en `mcp.json`
> y listar sus tools en `tools`.

### Ejemplo real: `codebase-memory-mcp`

Un MCP muy usado que ilustra el caso "datos reales, no solo código":
**[DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)** (MIT, ⭐ ~37k)
indexa tu repo en un **grafo de conocimiento persistente** y expone tools para consultar estructura,
llamadas, rutas HTTP, dead code, etc. — con queries en <1 ms y, según el proyecto, ~99% menos tokens
que explorar archivo por archivo. Es un binario estático local (el código no sale de tu máquina).

Registrarlo en `.vscode/mcp.json` (una vez instalado el binario):

```json
{
  "servers": {
    "codebase-memory": {
      "type": "stdio",
      "command": "codebase-memory-mcp"
    }
  }
}
```

Y luego sus tools quedan disponibles para un agente — ideal para un **explorador de solo-lectura**:

```yaml
---
name: 'repo-explorer'
description: 'Explora la arquitectura del repo vía grafo, sin escanear archivo por archivo.'
tools: ['read', 'codebase-memory/search', 'codebase-memory/trace']  # tools del MCP registrado
---
Antes de responder, consultá el grafo del codebase en vez de leer archivos sueltos.
```

> ⚠️ **Evalúa antes de instalar cualquier MCP de terceros.** Este es popular y MIT, pero corre
> como binario local con acceso a tu código. Prefiere métodos de instalación auditables (Homebrew,
> npm, binario firmado) sobre un `curl … | bash` a ciegas, y revisa qué permisos concede.

---

## 12. Agent Plugins (preview)

### ¿Qué es?

El **séptimo** mecanismo oficial de customización. Un Agent Plugin es un **bundle instalable**
que empaqueta varias de las piezas anteriores (instructions + prompts + agents + skills + hooks +
MCP) en un solo paquete distribuible desde un **marketplace**.

> Docs: [Customize AI in VS Code — overview](https://code.visualstudio.com/docs/copilot/customization/overview) (sección *Agent plugins*)

### ¿Qué hace / ventajas?

- ✅ **Adopción sin construir**: instalas un workflow probado en vez de escribir cada archivo a mano.
- ✅ **Distribución**: es la vía natural para repartir un mismo paquete de customizaciones a
  **muchos equipos o módulos** — directamente relevante para la §16 (monorepos): en vez de copiar
  `.github/agents/`, `skills/` y `hooks/` a cada repo, publicas un plugin y cada equipo lo instala.
- ✅ **Consistencia**: todos arrancan con la misma configuración base.

### Cómo se usa

Se instala desde el editor (marketplace de plugins). Al instalarlo, sus instructions, prompts,
agents, skills y hooks quedan disponibles como si los hubieras creado tú.

> Es una función en **preview**: la superficie exacta (comandos, formato del bundle) puede cambiar.
> Úsalo para adoptar paquetes existentes; para lo propio del equipo, sigue versionando `.github/`.

---

## 13. Combinando todo: recetas prácticas

Aquí es donde las piezas cobran sentido. Ejemplos concretos de composición.

### Receta 1 — Un prompt que usa un custom agent

Un prompt file puede fijar `agent:` para que corra bajo una persona específica:

**Archivo:** `.github/prompts/harden-endpoint.prompt.md`

```markdown
---
description: 'Endurece un endpoint existente con validación y manejo de errores'
name: 'harden-endpoint'
agent: dotnet-api-expert       # ← corre bajo el custom agent, no el genérico
tools: ['read/readFile', 'edit/editFiles']   # sintaxis set/tool (ver §8)
---

Toma el controller `backend/Controllers/${input:name}Controller.cs` y añádele:
- validación de request con FluentValidation
- manejo de errores centralizado (ProblemDetails, no try/catch repetido)
- `[Authorize]` en los endpoints que lo requieran
- `CancellationToken` en las operaciones async que falten
```

Invocas `/harden-endpoint`, rellenas `name`, y la tarea corre con el conocimiento y las reglas del `dotnet-api-expert`. **Prompt (el "qué") + Agent (el "quién").**

### Receta 2 — Custom agent orquestando a otro (modo orquestación)

El caso que pediste explícitamente. Un agente coordinador delega a especialistas vía subagentes:

```
   feature-orchestrator
   tools: ['read', 'search/codebase', 'agent']
   agents: ['dotnet-api-expert', 'angular-expert', 'security-reviewer', 'test-writer']
          │
   ┌──────┴───────────────────┬──────────────────┬─────────────────┐
   ▼                          ▼                  ▼                 ▼
dotnet-api-expert     angular-expert     security-reviewer    test-writer
(edit, terminal)      (edit, terminal)    (solo lectura)       (edit)
crea controller+svc   crea el componente  audita               escribe tests
```

El orquestador **no escribe código** — sólo coordina. Cada subagente tiene tools mínimas para su rol. (Ver el archivo completo en §9, Mecanismo A.)

### Receta 3 — Workflow supervisado con Handoffs + Plan Agent

Para features complejas, encadena aprobando cada paso:

```
Plan Agent            →  genera plan paso a paso (solo lectura)
  └─ handoff "Implementar" →  Implementation Agent  (edit + terminal)
       └─ handoff "Revisar"    →  Security Reviewer  (solo lectura)
```

Combina el **Plan Agent** (analiza el codebase antes de codear) con **handoffs** en tus custom agents. Tú apruebas cada transición.

### Receta 4 — Skill + Hook trabajando juntos

- El **Skill `ef-migration`** ejecuta la migración de EF Core (workflow con scripts).
- El **Hook `PreToolUse`** bloquea la migración si detecta un comando peligroso (`DROP TABLE`, `database drop`).
- El **Hook `PostToolUse`** loguea el resultado de la migración.

El skill hace *lo que quieres que pase*; el hook *garantiza los límites* pase lo que pase.

### Receta 5 — La cadena completa de Context Engineering

```
copilot-instructions.md   → contexto base (siempre)
        +
backend.instructions.md   → reglas del backend .NET (al tocar backend/**/*.cs)
        +
/new-controller (prompt)  → scaffoldea con el patrón correcto
        +
dotnet-api-expert (agent) → lo revisa un especialista
        +
ef-migration (skill)      → migra la base de datos
        +
hooks                     → formatea (dotnet format) y protege en cada paso
        +
postgres (MCP)            → valida contra el schema real
```

---

## 14. Orquestación con handoffs (Planner, BE, FE, QA)

Ejemplo completo y copy-paste de un workflow multi-agente **guiado por handoffs**: un
**planificador** que delega a **backend**, luego **frontend**, luego **QA** — donde *tú apruebas
cada transición*. Es la versión supervisada de la orquestación (compárala con los subagentes
automáticos de la [§9](#9-orquestación-agentes-que-hablan-con-agentes)).

> Docs: [Custom agents — Handoffs](https://code.visualstudio.com/docs/copilot/customization/custom-agents).
> *"After a chat response completes, handoff buttons appear that let users move to the next agent with relevant context and a pre-filled prompt."*

### Cómo funciona un handoff

En el frontmatter de un agente declaras botones que aparecen **al terminar su respuesta**:

| Campo | Qué hace | Default |
|---|---|---|
| `label` | Texto del botón | *requerido* |
| `agent` | Agente destino (debe coincidir con su `name`) | *requerido* |
| `prompt` | Texto pre-cargado en el input del destino | opcional |
| `send` | Si `true`, envía el prompt automáticamente | `false` |
| `model` | Modelo para ese handoff (formato `Nombre (vendor)`) | el actual |

Dos claves de la orquestación con handoffs:

- **La sesión es compartida**: cuando arranca el backend, *ya ve el plan*; cuando arranca el frontend, ve los endpoints que creó el backend. No repites contexto.
- **El humano aprueba cada salto** (`send: false`): revisas el prompt pre-cargado antes de enviarlo. Con `send: true` el salto es automático.

**Escenario:** agregar la feature *"comentarios en tareas"* (endpoint + pantalla + tests) a TaskFlow (.NET + Angular). Los 4 agentes van en `.github/agents/`.

### 1️⃣ `feature-planner.agent.md` — planificador (solo lectura)

```markdown
---
name: 'feature-planner'
description: 'Analiza el codebase y produce un plan de implementación. No escribe código.'
tools: ['read', 'search/codebase', 'search/usages']   # ¡sin edit! solo planifica
model: 'Claude Sonnet 4.5 (copilot)'
user-invocable: true
handoffs:
  - label: '→ Implementar backend'
    agent: backend-dev
    prompt: 'Implementa la parte de backend del plan anterior, paso por paso.'
    send: false
    model: 'Claude Sonnet 4.5 (copilot)'
---

Eres un arquitecto de software. Ante una feature:
1. Explora el codebase relevante (entidades, controllers, componentes existentes).
2. Produce un **plan numerado** separando trabajo de **backend**, **frontend** y **QA**.
3. Señala archivos a tocar, contratos de API (DTOs, rutas) y riesgos.
NO escribes código: tu entregable es el plan. Al terminar, ofrece el handoff a `backend-dev`.
```

### 2️⃣ `backend-dev.agent.md` — backend (.NET)

```markdown
---
name: 'backend-dev'
description: 'Implementa la API en ASP.NET Core 8 siguiendo el plan.'
tools: ['read', 'edit', 'search/codebase', 'execute/runInTerminal']
model: 'Claude Sonnet 4.5 (copilot)'
handoffs:
  - label: '→ Implementar frontend'
    agent: frontend-dev
    prompt: 'El backend ya está listo (revisa los endpoints y DTOs de arriba). Implementa el frontend que los consume.'
    send: false
  - label: '↩ Volver a planificar'
    agent: feature-planner
    prompt: 'Encontré un problema al implementar; revisemos el plan.'
    send: false
---

Eres experto en ASP.NET Core 8 (Controller → Service → Repository, DI por constructor, DTOs).
Implementas SOLO el backend del plan. Validas con `dotnet build` antes de terminar.
Al finalizar, resume los endpoints/DTOs creados y ofrece el handoff a `frontend-dev`.
```

### 3️⃣ `frontend-dev.agent.md` — frontend (Angular)

```markdown
---
name: 'frontend-dev'
description: 'Implementa la UI en Angular 17 que consume la API.'
tools: ['read', 'edit', 'search/codebase', 'execute/runInTerminal']
model: 'Claude Sonnet 4.5 (copilot)'
handoffs:
  - label: '→ Probar y validar (QA)'
    agent: qa-engineer
    prompt: 'La feature está implementada (backend + frontend). Escribe y ejecuta las pruebas y revisa la calidad.'
    send: false
---

Eres experto en Angular 17 (standalone + signals, `async` pipe, tipado estricto).
Implementas SOLO el frontend, consumiendo los endpoints que definió `backend-dev`.
Validas con `ng build`. Al terminar, ofrece el handoff a `qa-engineer`.
```

### 4️⃣ `qa-engineer.agent.md` — QA (tests + revisión)

```markdown
---
name: 'qa-engineer'
description: 'Escribe/ejecuta tests (xUnit + Jasmine) y revisa la calidad de la feature.'
tools: ['read', 'edit', 'search/codebase', 'search/usages', 'execute/runInTerminal']
model: 'Claude Sonnet 4.5 (copilot)'
handoffs:
  - label: '↩ Corregir backend'
    agent: backend-dev
    prompt: 'QA encontró estos fallos en la API (ver arriba). Corrígelos.'
    send: false
  - label: '↩ Corregir frontend'
    agent: frontend-dev
    prompt: 'QA encontró estos fallos en la UI (ver arriba). Corrígelos.'
    send: false
---

Eres ingeniero de QA. Escribes tests unitarios/integración, los ejecutas
(`dotnet test`, `ng test`) y revisas edge cases. Si todo pasa, lo confirmas.
Si algo falla, resumes los fallos y ofreces el handoff al agente responsable.
```

### El flujo de la orquestación

```
   [Tú] seleccionas 'feature-planner' y describes la feature
            │
            ▼
   feature-planner  ── produce el plan (solo lectura)
            │  clic botón "→ Implementar backend"   (send:false → revisas el prompt)
            ▼
   backend-dev      ── crea controller + servicio + DTOs, dotnet build
            │  clic "→ Implementar frontend"
            ▼
   frontend-dev     ── crea el componente Angular, ng build
            │  clic "→ Probar y validar (QA)"
            ▼
   qa-engineer      ── escribe y corre tests
            │
     ┌──────┴───────── ¿fallos?
     │ sí                            │ no
     ▼                              ▼
  "↩ Corregir backend/frontend"   ✅ feature lista
  (vuelve al dev responsable)
```

- **Los back-edges** (`↩ Corregir…`) hacen la orquestación realista: QA no solo avanza, también devuelve el trabajo al dev correcto si encuentra bugs. Es un grafo, no solo una línea.
- **`agent:` debe coincidir con el `name`** del `.agent.md` destino, y los cuatro archivos van en `.github/agents/`.

### Handoffs vs. subagentes — no confundir

| | **Handoffs** (esta sección) | **Subagentes** (`agents:` + tool `agent`) |
|---|---|---|
| Quién transiciona | El **humano** (clic en botón) | El **agente** (automático) |
| Contexto | **Compartido** (misma sesión) | **Aislado** por subagente |
| Ideal para | Workflow supervisado paso a paso | Pipeline autónomo sin intervención |

Si quisieras que un **orquestador** hiciera todo esto solo (sin clic), usarías el campo `agents:` + el tool set `agent` — ver [§9](#9-orquestación-agentes-que-hablan-con-agentes). Los handoffs son la versión *guiada por ti*.

---

## 15. El AI-SDLC: orquestación de agentes con validación humana

El AI-SDLC es un **framework de 6 etapas encadenadas** que lleva *de un input de negocio crudo a un
handoff técnico ejecutable*, **sin escribir código a mano hasta el final**. No es una herramienta: es
un **proceso**. Cada etapa es un agente de IA que **recibe un artefacto auditable y entrega otro
estructurado** que alimenta a la siguiente. Entre etapa y etapa hay un **HITL gate** (Human-in-the-Loop):
un punto de validación humana obligatoria que impide avanzar sin revisión.

> **El problema no es la IA — es la ausencia de un proceso repetible alrededor de ella.** La IA amplifica
> errores tan rápido como acelera el trabajo. El HITL gate es el **mecanismo de calidad**, no un trámite.

### La teoría de la orquestación

*Orquestar* no es un agente gigante que lo hace todo, sino **coordinar varios agentes especializados en
una cadena** donde el *output* de uno es el *input* del siguiente, con **puntos de control entre pasos**.
Una línea de ensamblaje, no un genio omnisciente. La cadena descansa en cuatro conceptos:

- **Fronteras de altitud.** Cada etapa opera a un nivel de abstracción y **no baja al siguiente**:
  Negocio → Funcional → Visual → Técnico. Una decisión de bajo nivel tomada demasiado pronto *contamina*
  las de alto nivel. Respetar la frontera es lo que hace cada artefacto auditable y firmable por el rol
  correcto (el BRD lo firma un sponsor; el Handoff, un Tech Lead).
- **HITL gate.** La IA no valida su propia calidad; el humano sí. El gate es **dónde se corta la
  propagación del error**. El humano no es un cuello de botella: es el control.
- **El artefacto es la interfaz.** Lo que pasa de una etapa a otra no es la conversación (efímera), sino
  un **artefacto estructurado y citado** que funciona como contrato. Eso da reproducibilidad.
- **Trazabilidad o nada.** Cada afirmación referencia su fuente (`§`, `archivo:línea`, `BRD-REQ-XXX`).
  Lo que no tiene fuente se degrada a supuesto — nunca a hecho.

**¿Por qué encadenar en vez de un solo agente?** Porque acota el contexto de cada etapa (menos
alucinación), hace cumplir las fronteras por diseño, y crea puntos de control auditables. Y la cadena
**no es lineal pura: es un grafo**. Cuando una etapa río abajo descubre un hueco, emite un **loop-back**:
en vez de *parchar hacia adelante*, el flujo **retrocede, enriquece el artefacto de origen y regenera**.
Es *fail-fast hacia atrás*.

### Las 6 etapas — qué significa cada una

**1 · Discovery / Research** *(opcional)* — **entender el problema antes de comprometerse a construir**.
Es la fase *divergente*: explora contexto regulatorio, competencia y patrones antes de que las siguientes
etapas *converjan*. Entrega un *dossier* citado. Sin esto, se construye sobre supuestos ("una app mejor")
en vez del dolor real del usuario.

**2 · BRD — Business Requirements** — el **contrato de negocio**: el *qué* y el *por qué*, firmable por
un sponsor (objetivos SMART, KPIs, alcance con *out-of-scope* explícito). **Frontera: cero tecnología** —
un BRD que dice "microservicios" ya rompió la altitud. Resuelve las features sin norte de negocio y el
*scope creep*.

**3 · PRD — Product Requirements** — el *qué* **funcional**: descompone el BRD en **historias verificables
por QA sin conocer la implementación** (Épicas → HU → criterios en **Gherkin**: Given/When/Then).
**Frontera: funcional, no técnico** — describe comportamiento observable, no "usar Redis". Resuelve el
salto de negocio a código sin especificar comportamiento testeable.

**4 · Diseño / Wireframes** *(opcional)* — el **contrato visual navegable**: traduce cada HU a pantallas,
con estados vacío/carga/error. **Frontera: visual, no técnico.**

**5 · Feasibility** — el ***reality check* contra el código real**. Es la **primera etapa que abre el
repositorio**: cruza el *deber ser* (PRD) con el *es* (código) y emite gaps, **ADRs** (decisiones de
arquitectura) y un veredicto (`viable` / `con condiciones` / `no viable` / `loop-back`). Resuelve prometer
tareas sin saber si el repo las soporta — como descubrir que falta un SDK y disparar un ADR *antes* de
generar tickets.

**6 · Handoff** — la **traducción a tareas ejecutables**: tickets **atómicos** que un dev + Copilot toman
sin preguntar nada (contrato, casos borde, *done criteria* y un prompt listo por tarea), ordenados en un
**DAG** de dependencias, con trazabilidad HU→Tarea→ADR. Resuelve el "handoff" que es solo el PRD copiado
y las tareas gigantes tipo "implementar módulo de pagos".

> **La regla de oro de la altitud:** el BRD nunca habla de tecnología; el PRD nunca habla de código;
> Feasibility es la primera que toca el repo; el Handoff es la única que genera prompts para escribir código.

### 💡 Nota — cómo se podría llevar este marco a Copilot (a modo de ejemplo)

Todo lo anterior es *metodología*; encaja de forma natural con los primitivos de esta guía si quisieras
montarlo como workspace:

- **Cada etapa** (`brd_prompt.md`, `feasibility_prompt.md`…) → un **custom agent** (§7), con el `tools`
  acotado a su altitud (los primeros **solo-lectura**; Feasibility con `search/codebase` para abrir el repo).
- **Cada HITL gate** → un **handoff** con `send:false` (§14): el humano revisa el artefacto y aprueba el
  salto. Los **loop-backs** → *back-edges* de handoff.
- **Las reglas transversales** (trazabilidad, altitud) → **custom instructions** del workspace (§3).

Un agente de etapa se vería así (ejemplo — la frontera de altitud vive en `tools`):

```markdown
---
name: 'sdlc-brd'
description: 'AI-SDLC Etapa 2: info de negocio → BRD firmable. Nunca habla de tecnología.'
tools: ['read']                        # solo-lectura → no puede bajar a lo técnico
handoffs:
  - label: '✓ Gate de negocio OK → PRD'
    agent: sdlc-prd
    prompt: 'BRD aprobado. Descomponelo en épicas + HU + AC Gherkin.'
    send: false                        # el HITL revisa antes de avanzar
---
Eres el BRD Agent. Si falta un input requerido, te detenés y lo pedís — no inventás.
```

> Es solo *una forma* de implementarlo; el framework vale por su proceso, no por la herramienta.

---

## 16. Adopción en proyectos existentes y monorepos grandes

Aplicar esto en un proyecto *greenfield* (nuevo) es fácil. El reto real es un **codebase existente, enorme, con muchos módulos, deuda técnica y convenciones no escritas**. Aquí la estrategia es distinta: **no configures todo de una vez**. Adopción incremental, por capas y por módulo.

### El anti-patrón a evitar

❌ Correr `/init` una vez en la raíz de un monorepo de 50 módulos y esperar que el `copilot-instructions.md` resultante sirva. Va a salir un archivo genérico, gigante y poco útil que mezcla reglas de módulos que se contradicen entre sí, y que **satura el contexto en cada request**.

✅ En su lugar: un contexto raíz **delgado** + instrucciones **por módulo** vía `applyTo`.

### Estrategia por fases

#### Fase 0 — Mapear antes de escribir

Antes de generar nada, usa el agente en modo solo-lectura (o el **Plan Agent** — actívalo con `/plan` o desde el dropdown de agentes) para que **documente lo que ya existe**:

```
Analiza este repositorio y dame:
1. El listado de módulos/paquetes de primer nivel y qué hace cada uno.
2. El stack y versión por módulo (framework, lenguaje, build tool).
3. Los patrones de código repetidos que detectes (naming, estructura de carpetas, manejo de errores).
4. Las inconsistencias entre módulos.
```

Ese análisis es el **borrador** de tus futuras instructions. La IA infiere; tú corriges con el conocimiento tribal que no está en el código.

#### Fase 1 — Contexto raíz mínimo (el "mapa")

El `copilot-instructions.md` de la raíz **no debe contener reglas de cada módulo**. Debe ser un **índice/mapa** que oriente:

> Los ejemplos de esta sección usan un monorepo ilustrativo distinto ("AcmeCorp", layout `src/Api/` + `web/`) para mostrar el caso multi-módulo. No es el mismo proyecto de las secciones anteriores (`backend/` + `frontend/`); adapta las rutas al tuyo.

**Archivo:** `.github/copilot-instructions.md`

```markdown
# Monorepo: AcmeCorp Platform

## Qué es esto
Monorepo con 4 dominios. Cada uno tiene sus PROPIAS reglas en
`.github/instructions/`. Lee siempre las instructions del módulo en el que trabajas.

## Mapa de módulos
| Carpeta        | Qué es              | Stack                    | Instructions             |
|----------------|---------------------|--------------------------|--------------------------|
| `src/Api/`     | API REST            | ASP.NET Core 8 (C#)      | api.instructions.md      |
| `src/Domain/`  | Dominio + EF Core   | C# class libraries       | domain.instructions.md   |
| `web/`         | Frontend            | Angular 17               | web.instructions.md      |
| `legacy/`      | Sistema viejo       | ASP.NET Framework 4.x    | legacy.instructions.md   |

## Reglas que aplican a TODO el repo (pocas, sólo las universales)
- Conventional Commits en los mensajes de commit.
- Nunca commitear secretos ni cadenas de conexión; usar user-secrets / variables de entorno.
- No modificar `legacy/` sin aprobación (ver legacy.instructions.md).
```

**Clave:** en la raíz sólo van las reglas **verdaderamente universales**. Todo lo específico baja a las instructions por módulo.

#### Fase 2 — Instructions por módulo con `applyTo`

Aquí es donde `applyTo` brilla en un monorepo. Cada módulo carga **sólo** sus reglas cuando trabajas en él:

```
.github/instructions/
├── api.instructions.md         → applyTo: 'src/Api/**/*.cs'
├── domain.instructions.md      → applyTo: 'src/Domain/**/*.cs'
├── web.instructions.md         → applyTo: 'web/**'
└── legacy.instructions.md      → applyTo: 'legacy/**'
```

Esto resuelve el problema de módulos que se contradicen: las reglas de Angular **nunca** contaminan el contexto cuando editas la API en C#. Y el contexto se mantiene liviano porque sólo se carga lo relevante al archivo abierto.

**Empieza por 1 o 2 módulos**, los que más toques. No hace falta cubrir los 50 desde el día uno.

> 🆕 En monorepos con repos anidados, el setting `chat.useCustomizationsInParentRepositories` permite que un submódulo **descubra las customizaciones del repo padre** — útil para compartir reglas base sin duplicarlas en cada carpeta.

#### Fase 3 — Blindar lo que no se debe tocar

En proyectos grandes hay zonas frágiles (código legacy, generado, o crítico). Combina **instructions** (guían) con **hooks** (garantizan):

```markdown
# legacy.instructions.md (applyTo: 'legacy/**')
⚠️ Este módulo es legacy y está congelado. NO refactorizar.
Sólo cambios con ticket aprobado. Si te piden modificar aquí, avisa primero.
```

Y un hook `PreToolUse` que **bloquee edits** a rutas protegidas sin importar el prompt:

```bash
#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.filePath // empty')
if [[ "$FILE" == */legacy/* || "$FILE" == */generated/* ]]; then
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Ruta protegida (legacy/generated). Requiere aprobación manual."}}'
  exit 0
fi
echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'
```

La instruction *pide* no tocar; el hook lo *impide*.

#### Fase 4 — Agentes especializados por dominio

En un monorepo grande, un solo agente genérico se pierde. Crea **un custom agent por dominio**, cada uno con las tools mínimas y el conocimiento de su módulo:

```
.github/agents/
├── dotnet-api-expert.agent.md      ← experto en src/Api/
├── angular-expert.agent.md         ← experto en web/
├── legacy-guardian.agent.md        ← solo-lectura, para entender legacy/ sin romperlo
└── monorepo-orchestrator.agent.md  ← coordina cambios que cruzan módulos
```

**Ejemplo — agente de solo-lectura para explorar el código legacy (ASP.NET Framework) sin riesgo:**

```markdown
---
name: 'legacy-guardian'
description: 'Explica y documenta el módulo legacy ASP.NET SIN modificarlo.'
tools: ['read', 'search/codebase', 'search/usages']   # ¡sin 'edit'! no puede tocar nada
model: 'Claude Sonnet 4.5 (copilot)'
---
Eres un arqueólogo de código. Tu trabajo es EXPLICAR el módulo legacy/ (WebForms/MVC
sobre .NET Framework), mapear dependencias y riesgos de cara a la migración a .NET 8.
Nunca propones editar; sólo documentas y adviertes.
```

Para cambios que **cruzan varios módulos** (ej. renombrar un contrato de API que consumen la API y el frontend Angular), usa el **orquestador** (§9) que delega a cada experto de dominio.

#### Fase 5 — Migraciones grandes con Background/Cloud Agents

Para tareas masivas y repetitivas en un codebase grande (migrar de una librería a otra en 200 archivos, actualizar imports, aplicar un codemod), usa:

- **Background Agents** — corren en un **Git worktree aislado**, en paralelo, sin bloquear tu editor. Puedes lanzar varios para módulos independientes al mismo tiempo.
- **Cloud Agents** — generan un **branch + PR automático** para que el equipo lo revise.

Empaqueta la migración como un **Skill** (§6) con el procedimiento y los scripts, y delégalo a un background agent por módulo.

### Checklist de adopción incremental

```
[ ] Fase 0: Plan Agent mapea módulos, stacks e inconsistencias
[ ] Fase 1: copilot-instructions.md raíz = mapa delgado + reglas universales
[ ] Fase 2: instructions por módulo (empezar por los 1-2 más activos)
[ ] Fase 3: hooks que blindan legacy/ y código generado
[ ] Fase 4: 1 custom agent por dominio + orquestador para cambios cross-módulo
[ ] Fase 5: skills + background/cloud agents para migraciones masivas
[ ] Iterar: agregar la siguiente capa sólo cuando aparezca la necesidad recurrente
```

### Principios para no fracasar en un proyecto grande

1. **Empieza pequeño, mide, expande.** Configura 1 módulo, valida que Copilot respeta las reglas (con `Diagnostics`), y sólo entonces replica al siguiente.
2. **Contexto raíz delgado.** Un `copilot-instructions.md` gigante es un anti-patrón — dispersa el foco y consume tokens. Que sea un mapa, no un manual.
3. **`applyTo` es tu mejor amigo en monorepos.** Aísla reglas por carpeta para que no se contaminen entre módulos.
4. **Mínimo privilegio en tools.** Agentes de exploración sin `edit`; edits a zonas frágiles bloqueados por hooks.
5. **Codifica el conocimiento tribal.** Lo más valioso que agregas no es lo que la IA infiere del código, sino lo que **no está escrito**: por qué ese módulo está congelado, por qué se prefiere X librería, qué se rompe si tocas Y.
6. **Versiona y revisa en PR.** Trata los archivos de `.github/` como código: se revisan, se discuten y evolucionan con el equipo.

---

## 17. Operar y controlar al agente (modos, contexto, loop, permisos)

Hasta aquí *configuraste* al agente (instructions, prompts, skills, agents, hooks). Esta sección es
lo otro: cómo lo **operas y lo contienes** día a día — en qué modo trabaja, qué contexto le das,
cómo es su bucle de ejecución y cómo apruebas/limitas lo que hace.

### Los tres modos del chat: Ask · Edit · Agent

Copilot Chat tiene tres modos. Tus **custom agents** (§7) corren *sobre* el modo **Agent**.

| Modo | Qué hace | Cuándo |
|---|---|---|
| **Ask** | Responde y explica; **no** edita archivos ni corre nada | Preguntar, entender código, explorar opciones |
| **Edit** | Aplica ediciones a los archivos que **tú** eliges (multi-archivo), con diff | Cambios acotados donde tú marcas el alcance |
| **Agent** | **Autónomo**: decide qué archivos tocar, corre tools/terminal y **itera** hasta terminar | Tareas end-to-end (la base de todo lo de esta guía) |

> Cambias de modo con el selector del chat. Todo el *Context Engineering* (instructions, agents, tools, hooks) aplica en **Agent**.

### Darle contexto: `#`-mentions, adjuntos e imágenes

Además de lo que Copilot infiere solo, tú puedes **adjuntar contexto explícito**:

> *"You can explicitly add context to your prompt by typing `#` followed by the context item you want to mention."* — VS Code Docs

| Forma | Ejemplo | Qué añade |
|---|---|---|
| `#` + archivo/carpeta | `#UserService.cs` | Ese archivo o carpeta como contexto |
| `#` + símbolo | `#calcularTotal` | Una función/clase concreta |
| `#codebase` | `#codebase` | Búsqueda semántica en todo el repo |
| `#fetch` | `#fetch https://…` | El contenido de una URL |
| **Drag & drop** | arrastrar del Explorer/editor | Archivos/carpetas al chat |
| **Imágenes (vision)** | arrastrar/pegar un screenshot | Adjunta la imagen y preguntas sobre ella |
| **Browser → chat** | *Add Element / Screenshot / Console Logs to Chat* | Contexto desde el browser integrado |

> ⚠️ **No confundas `#context` con `#tools`.** Ambos usan `#`, pero los de §8 (`#search/codebase`, `#edit/editFiles`…) son *herramientas que el agente ejecuta*; estos son *contexto que tú adjuntas*. `#codebase` existe en ambas caras (es tool de búsqueda y forma de adjuntar el repo).

### Variables de prompt (en `*.prompt.md` y agents)

Para hacer los prompt files (§5) reutilizables, la doc confirma estas variables integradas:

| Variable | Qué inserta |
|---|---|
| `${selection}` | El texto seleccionado en el editor |
| `${input:nombre}` | Pide un valor al invocar (lo que ya usamos en §5) |
| `${input:nombre:placeholder}` | Igual, con texto de ayuda en el input |

```markdown
Refactoriza ${selection} siguiendo el patrón de `${input:patron:ej. Repository}`.
```

> Para pedir datos de forma interactiva también existe el tool `vscode/askQuestions`. Las variables estándar de VS Code (`${workspaceFolder}`, `${file}`…) suelen estar disponibles, pero la doc de prompt files solo documenta explícitamente `${selection}` y `${input:...}`.

### El loop agéntico y sus límites

En modo Agent, Copilot no responde una sola vez: corre un bucle **pensar → actuar → observar** y
se **auto-corrige** hasta terminar.

> *"responds to compile and lint errors, monitors terminal output, and **auto-corrects in a loop until the task is completed**"* — VS Code Blog

Está **acotado y es configurable**:

| Setting | Qué hace | Default |
|---|---|---|
| `chat.agent.maxRequests` | Nº máx. de requests por turno; al llegar, **se detiene y te pregunta si continúa** | `25` |
| `github.copilot.chat.agent.autoFix` | Auto-diagnostica y corrige errores en el código generado (self-healing) | `true` |

> Aquí encajan tus **hooks** (§10): el "ciclo del agente" que mencionan es *este* loop. `PreToolUse`/`PostToolUse` disparan en **cada vuelta**, no una sola vez por turno.

### Aprobaciones y permisos (contener al agente)

Antes de correr acciones sensibles (comandos de terminal, ediciones), el agente **pide aprobación**:
apruebas o deniegas cada tool call. Puedes ajustar cuánta autonomía darle:

| Setting | Qué hace | Default |
|---|---|---|
| `chat.tools.terminal.enableAutoApprove` | Aprueba comandos de terminal automáticamente | `true` |
| `chat.tools.global.autoApprove` | Aprueba **todas** las tools sin preguntar — ⚠️ **desactiva protecciones de seguridad** | `false` |

- **Niveles de permiso**: van desde "aprobar todo a mano" hasta "ejecución autónoma".
- **Agent sandboxing**: restringe acceso a **filesystem y red a nivel del sistema operativo**, para dejar correr al agente con red de seguridad.

> **Aprobaciones vs. Hooks**: las aprobaciones son *interactivas* (tú decides en el momento); los hooks (§10) son la *política determinística* que se aplica sola, sin importar el prompt. Se complementan: usa hooks para lo que **siempre** debe bloquearse (p. ej. `rm -rf`, tocar `legacy/`) y las aprobaciones para el resto.

### Sesiones y checkpoints

- **Sesiones persistentes**: el hilo de conversación se conserva y se **comparte** entre la Chat view y la ventana de Agents; puedes retomar donde quedaste.
- **Checkpoints**: puedes **deshacer las ediciones del agente** y volver a un punto anterior si una iteración salió mal — clave cuando el loop tocó varios archivos.

> Docs: [Agent mode](https://code.visualstudio.com/blogs/2025/04/07/agentMode) · [Copilot settings reference](https://code.visualstudio.com/docs/copilot/reference/copilot-settings) · [Manage context](https://code.visualstudio.com/docs/copilot/chat/copilot-chat-context)

---

## 18. Estructura final del proyecto

```
mi-proyecto/
└── .github/
    ├── copilot-instructions.md          ← SIEMPRE activo (todo el proyecto)
    ├── instructions/
    │   ├── backend.instructions.md       ← applyTo: backend/**/*.cs
    │   ├── frontend.instructions.md      ← applyTo: frontend/**
    │   └── tests.instructions.md         ← applyTo: **/*Tests.cs
    ├── prompts/
    │   ├── new-controller.prompt.md      ← /new-controller
    │   ├── harden-endpoint.prompt.md     ← /harden-endpoint (usa un agent)
    │   └── create-pr.prompt.md           ← /create-pr
    ├── agents/
    │   ├── feature-orchestrator.agent.md ← orquesta subagentes
    │   ├── dotnet-api-expert.agent.md
    │   ├── angular-expert.agent.md
    │   ├── security-reviewer.agent.md
    │   └── test-writer.agent.md
    ├── skills/
    │   └── ef-migration/
    │       ├── SKILL.md
    │       ├── scripts/
    │       └── examples/
    └── hooks/
        ├── post-edit.json                ← PostToolUse (dotnet format / Prettier)
        ├── security.json                 ← PreToolUse (bloqueo)
        └── scripts/
            ├── format-on-edit.sh
            └── block-dangerous-commands.sh
```

> **Todo en `.github/` se versiona y se comparte con el equipo automáticamente.**

---

## 19. Tabla de comandos y troubleshooting

### Comandos en el chat

| Comando | Acción |
|---|---|
| `/init` | Genera `copilot-instructions.md` analizando el workspace |
| `/create-instruction` | Genera un `*.instructions.md` |
| `/create-prompt` | Genera un `*.prompt.md` |
| `/create-agent` | Genera un `*.agent.md` |
| `/create-skill` | Genera una Agent Skill |
| `/create-hook` | Genera un Hook |
| `/plan` | Activa el **Plan Agent** (también seleccionable en el dropdown de agentes) |
| `/instructions` | Abre el menú de instrucciones configuradas |
| `/prompts` | Abre el menú de prompt files |

### Referenciar tools en el chat

- En **chat**: con `#` → `#search/codebase`, `#web/fetch`, `#edit/editFiles`.
- En **frontmatter YAML**: sin `#` → `tools: ['search/codebase', 'web/fetch']`.

### Troubleshooting

Si una instrucción/agente no se aplica:

1. **Ver qué se cargó:** click derecho en el Chat → `Diagnostics`.
2. **Ubicación:** `copilot-instructions.md` debe estar en `.github/` en la raíz.
3. **`applyTo`:** el glob debe coincidir con el archivo abierto.
4. **References:** la sección "References" en la respuesta del chat muestra qué instrucciones/tools se usaron.
5. **Subagentes no aparecen:** verifica que el tool set `agent` esté en `tools` **y** que el subagente esté listado en `agents`.

---

## 20. Tips para instrucciones efectivas

1. **Incluye el "por qué"** de cada regla.
   ```
   ❌ "Usa System.Text.Json para serializar"
   ✅ "Usa System.Text.Json en lugar de Newtonsoft.Json — es el serializador por defecto de .NET y evita una dependencia extra"
   ```
2. **Muestra patrones con ejemplos de código concretos** — la IA responde mejor a ejemplos que a reglas abstractas.
3. **Enfócate en lo no obvio** — omite lo que ya enforcea un linter/formatter.
4. **Reutiliza** — referencia instrucciones con Markdown links, no dupliques.
5. **Versiona todo en git** — `.github/` se comparte con el equipo automáticamente.

---

## 21. Recursos oficiales

**General**
- [Copilot in VS Code — Overview](https://code.visualstudio.com/docs/copilot/overview)
- [Agents overview](https://code.visualstudio.com/docs/copilot/agents/overview)
- [Background Agents](https://code.visualstudio.com/docs/copilot/agents/background-agents) · [Cloud Agents](https://code.visualstudio.com/docs/copilot/agents/cloud-agents) · [Plan Agent](https://code.visualstudio.com/docs/copilot/agents/planning)

**Context Engineering**
- [Customize AI in VS Code](https://code.visualstudio.com/docs/copilot/customization/overview)
- [Custom Instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Prompt Files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [Custom Agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [MCP Servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Hooks](https://code.visualstudio.com/docs/copilot/customization/hooks)
- [Agent Plugins — overview](https://code.visualstudio.com/docs/copilot/customization/overview)

**Galerías e inspiración** *(de dónde copiar ideas para tus skills, agents, instructions y prompts)*
- ⭐ **[Awesome GitHub Copilot](https://awesome-copilot.github.com/)** — galería oficial de la comunidad con **agents, instructions, skills, prompts y plugins** listos para copiar y adaptar. El mejor punto de partida para no arrancar de cero (ver §6, §7).
- [Repo de Awesome Copilot en GitHub](https://github.com/github/awesome-copilot) — el código fuente de la galería.

**Herramientas de autoría** *(nuevas, en preview)*
- **Agent Customizations editor** — UI unificada (desde *Configure Chat*) para crear y gestionar todos los tipos de customización en un solo lugar.
- **Chat Customizations Evaluations** *(extensión)* — analiza tus archivos de customización buscando **contradicciones, ambigüedades y conflictos** antes de usarlos (ver §19, Diagnostics).
