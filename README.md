# Guía de GitHub Copilot en VS Code

Sitio estático (GitHub Pages) con la guía y documentación completa de **Context Engineering**
con GitHub Copilot en VS Code: `/init`, instructions, prompt files, Agent Skills, Custom Agents,
orquestación, hooks, MCP, Agent Plugins y adopción en monorepos.

👉 **Sitio publicado:** _(se añade tras activar Pages — ver más abajo)_

## Estructura

| Archivo | Qué es |
|---|---|
| `README-copilot.md` | **La fuente de verdad.** Todo el contenido de la guía en Markdown. Edita esto. |
| `build.py` | Genera `index.html` incrustando el Markdown (base64). Corre `python3 build.py` tras editar. |
| `index.html` | El sitio generado (un solo archivo, se commitea para que Pages lo sirva). |
| `.nojekyll` | Le dice a GitHub Pages que sirva el HTML tal cual, sin procesar con Jekyll. |

## Editar y regenerar

```bash
# 1. Edita el contenido
$EDITOR README-copilot.md

# 2. Regenera el sitio
python3 build.py

# 3. Previsualiza localmente
python3 -m http.server 8099 --directory .
# abre http://localhost:8099/
```

> El sitio usa `marked` y `highlight.js` desde CDN (jsdelivr) para renderizar el Markdown y
> resaltar el código. El contenido va incrustado en `index.html`, así que la página funciona
> con doble clic o servida por Pages, sin backend.

## Publicar en GitHub Pages

Ver los comandos de `gh` en la sección de publicación del chat, o:

1. Crea el repo y haz push (`main`).
2. **Settings → Pages → Source: Deploy from a branch → `main` / root**.
3. La URL será `https://<usuario>.github.io/<repo>/`.

Para mostrar el botón **GitHub** en la barra del sitio, edita `const REPO_URL = ""` en `index.html`
(o en la plantilla dentro de `build.py`) con la URL de tu repo.
