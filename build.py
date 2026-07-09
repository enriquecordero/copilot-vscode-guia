#!/usr/bin/env python3
"""Genera index.html a partir de README-copilot.md.

El Markdown es la ÚNICA fuente de verdad: edítalo y vuelve a correr `python3 build.py`.
El contenido se incrusta en index.html en base64, así la página funciona en cualquier
lado (doble clic, GitHub Pages, un servidor local) sin depender de fetch ni de CORS.
"""
import base64
import pathlib

SRC = pathlib.Path(__file__).parent / "README-copilot.md"
OUT = pathlib.Path(__file__).parent / "index.html"

md = SRC.read_text(encoding="utf-8")
b64 = base64.b64encode(md.encode("utf-8")).decode("ascii")

TEMPLATE = r"""<!doctype html>
<html lang="es" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub Copilot en VS Code — Guía completa</title>
<meta name="description" content="Guía y documentación completa de Context Engineering con GitHub Copilot en VS Code: instructions, prompts, skills, custom agents, orquestación, hooks, MCP y adopción en monorepos.">
<link id="hljs-light" rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css">
<link id="hljs-dark" rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css" disabled>
<style>
  :root{
    --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --accent:#0969da; --accent-soft:#ddf4ff;
    --border:#d1d9e0; --sidebar:#f6f8fa; --code-bg:#f6f8fa; --card:#f6f8fa;
    --topbar:rgba(255,255,255,.85); --shadow:0 1px 3px rgba(0,0,0,.08);
  }
  html[data-theme="dark"]{
    --bg:#0d1117; --fg:#e6edf3; --muted:#9198a1; --accent:#4493f8; --accent-soft:#193050;
    --border:#30363d; --sidebar:#0d1117; --code-bg:#161b22; --card:#161b22;
    --topbar:rgba(13,17,23,.85); --shadow:0 1px 3px rgba(0,0,0,.4);
  }
  *{box-sizing:border-box}
  [hidden]{display:none!important}
  html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--fg);
    font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased}

  /* Topbar */
  .topbar{position:fixed;top:0;left:0;right:0;height:56px;z-index:40;display:flex;align-items:center;
    gap:12px;padding:0 16px;background:var(--topbar);backdrop-filter:blur(8px);
    border-bottom:1px solid var(--border)}
  .brand{font-weight:700;font-size:15px;white-space:nowrap;letter-spacing:-.01em}
  .brand small{color:var(--muted);font-weight:500}
  .topbar .spacer{flex:1}
  #filter{width:min(280px,38vw);padding:7px 12px;border:1px solid var(--border);border-radius:8px;
    background:var(--bg);color:var(--fg);font-size:14px;outline:none}
  #filter:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
  .icon-btn{display:grid;place-items:center;width:38px;height:38px;border:1px solid var(--border);
    border-radius:8px;background:var(--bg);color:var(--fg);cursor:pointer;font-size:17px}
  .icon-btn:hover{border-color:var(--accent);color:var(--accent)}
  #menuBtn{display:none}
  .gh{display:inline-flex;align-items:center;gap:6px;padding:7px 12px;border:1px solid var(--border);
    border-radius:8px;color:var(--fg);text-decoration:none;font-size:14px;font-weight:600}
  .gh:hover{border-color:var(--accent);color:var(--accent)}

  /* Layout */
  .layout{display:flex;margin-top:56px}
  #sidebar{position:sticky;top:56px;align-self:flex-start;width:300px;flex:0 0 300px;
    height:calc(100vh - 56px);overflow-y:auto;padding:20px 12px 60px;background:var(--sidebar);
    border-right:1px solid var(--border)}
  #toc{list-style:none;margin:0;padding:0}
  #toc a{display:block;padding:6px 12px;margin:1px 0;color:var(--muted);text-decoration:none;
    font-size:14px;border-radius:7px;border-left:2px solid transparent;transition:background .12s,color .12s}
  #toc a:hover{background:var(--card);color:var(--fg)}
  #toc a.active{color:var(--accent);background:var(--accent-soft);font-weight:600}
  #toc a.hidden{display:none}
  .toc-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
    color:var(--muted);padding:0 12px 8px}

  main{flex:1;min-width:0;padding:0 6vw}
  article{max-width:840px;margin:0 auto;padding:36px 0 80px}

  /* Content typography */
  article h1{font-size:2.1em;line-height:1.2;margin:.2em 0 .6em;letter-spacing:-.02em}
  article h2{font-size:1.5em;margin:2.2em 0 .8em;padding-bottom:.3em;border-bottom:1px solid var(--border);
    letter-spacing:-.01em;scroll-margin-top:72px}
  article h3{font-size:1.18em;margin:1.8em 0 .6em;scroll-margin-top:72px}
  article h4{font-size:1em;margin:1.4em 0 .5em;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
  article p{margin:.7em 0}
  article a{color:var(--accent);text-decoration:none}
  article a:hover{text-decoration:underline}
  article ul,article ol{padding-left:1.5em;margin:.6em 0}
  article li{margin:.28em 0}
  article blockquote{margin:1em 0;padding:.5em 1em;border-left:4px solid var(--accent);
    background:var(--card);border-radius:0 8px 8px 0;color:var(--fg)}
  article blockquote p{margin:.3em 0}
  article hr{border:0;border-top:1px solid var(--border);margin:2.4em 0}
  article img{max-width:100%}

  /* Inline code + blocks */
  article :not(pre)>code{background:var(--code-bg);padding:.15em .4em;border-radius:6px;font-size:.87em;
    font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    border:1px solid var(--border)}
  article pre{position:relative;background:var(--code-bg);border:1px solid var(--border);border-radius:10px;
    padding:16px;overflow-x:auto;margin:1em 0;font-size:13.5px;line-height:1.55}
  article pre code{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    background:none;border:0;padding:0}
  .copy-btn{position:absolute;top:8px;right:8px;padding:4px 10px;font-size:12px;border:1px solid var(--border);
    border-radius:6px;background:var(--bg);color:var(--muted);cursor:pointer;opacity:0;transition:opacity .15s}
  article pre:hover .copy-btn{opacity:1}
  .copy-btn:hover{color:var(--accent);border-color:var(--accent)}
  .copy-btn.done{color:#1a7f37;border-color:#1a7f37}

  /* Tables */
  .table-wrap{overflow-x:auto;margin:1em 0}
  article table{border-collapse:collapse;width:100%;font-size:14px}
  article th,article td{border:1px solid var(--border);padding:8px 12px;text-align:left;vertical-align:top}
  article th{background:var(--card);font-weight:700}
  article tr:nth-child(even) td{background:var(--card)}

  /* Anchor link on headings */
  .anchor{opacity:0;margin-left:.35em;color:var(--muted);text-decoration:none;font-weight:400}
  h2:hover .anchor,h3:hover .anchor{opacity:1}

  article footer{margin-top:60px;padding-top:24px;border-top:1px solid var(--border);
    color:var(--muted);font-size:14px}

  #backTop{position:fixed;right:22px;bottom:22px;width:44px;height:44px;border-radius:50%;
    border:1px solid var(--border);background:var(--bg);color:var(--fg);cursor:pointer;font-size:18px;
    box-shadow:var(--shadow);opacity:0;pointer-events:none;transition:opacity .2s;z-index:30}
  #backTop.show{opacity:1;pointer-events:auto}
  #backTop:hover{color:var(--accent);border-color:var(--accent)}

  .scrim{display:none;position:fixed;inset:56px 0 0;background:rgba(0,0,0,.4);z-index:35}

  @media (max-width:900px){
    #menuBtn{display:grid}
    .brand small{display:none}
    main{padding:0 20px}
    #sidebar{position:fixed;top:56px;left:0;bottom:0;height:auto;z-index:36;width:290px;
      transform:translateX(-100%);transition:transform .22s ease;box-shadow:var(--shadow)}
    #sidebar.open{transform:translateX(0)}
    .scrim.open{display:block}
    #filter{width:auto;flex:1}
  }
  @media print{.topbar,#sidebar,#backTop{display:none}main{padding:0}article{max-width:none}}
</style>
</head>
<body>
  <header class="topbar">
    <button id="menuBtn" class="icon-btn" aria-label="Menú">☰</button>
    <span class="brand">Copilot&nbsp;·&nbsp;VS&nbsp;Code <small>Guía completa</small></span>
    <span class="spacer"></span>
    <input id="filter" type="search" placeholder="Filtrar secciones…" aria-label="Filtrar secciones">
    <button id="themeBtn" class="icon-btn" aria-label="Cambiar tema">🌙</button>
    <a id="ghLink" class="gh" href="#" hidden>GitHub</a>
  </header>

  <div class="layout">
    <aside id="sidebar">
      <div class="toc-title">Contenido</div>
      <nav><ul id="toc"></ul></nav>
    </aside>
    <main>
      <article id="content">Cargando…</article>
    </main>
  </div>

  <div class="scrim" id="scrim"></div>
  <button id="backTop" aria-label="Volver arriba">↑</button>

  <script id="md" type="application/octet-stream">__MARKDOWN_B64__</script>
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
  <script>
  // ==== CONFIG ====
  // Pon aquí la URL de tu repo para mostrar el botón "GitHub" en la barra superior:
  const REPO_URL = "https://github.com/enriquecordero/copilot-vscode-guia";

  // ==== Decodifica el Markdown (base64 → UTF-8) ====
  const b64 = document.getElementById("md").textContent.trim();
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const source = new TextDecoder("utf-8").decode(bytes);

  // ==== GitHub-style slugify (para que la TOC del markdown enlace bien) ====
  const seen = {};
  function slugify(text){
    let s = text.normalize("NFC").toLowerCase().trim()
      .replace(/[^\p{L}\p{N} \-]/gu, "")
      .replace(/\s+/g, "-");
    if(seen[s] != null){ seen[s]++; s = s + "-" + seen[s]; } else { seen[s] = 0; }
    return s;
  }

  // ==== Render ====
  marked.setOptions({ gfm:true, breaks:false, headerIds:false, mangle:false });
  const content = document.getElementById("content");
  content.innerHTML = marked.parse(source);

  // Ids + anchors en h2/h3
  content.querySelectorAll("h1,h2,h3").forEach(h => {
    if(h.tagName !== "H1" && !h.id) h.id = slugify(h.textContent);
    if(h.tagName === "H2" || h.tagName === "H3"){
      const a = document.createElement("a");
      a.className = "anchor"; a.href = "#" + h.id; a.textContent = "#";
      h.appendChild(a);
    }
  });

  // Envuelve tablas para scroll horizontal en móvil
  content.querySelectorAll("table").forEach(t => {
    const w = document.createElement("div"); w.className = "table-wrap";
    t.parentNode.insertBefore(w, t); w.appendChild(t);
  });

  // Resalta sólo bloques con lenguaje declarado (no toca los diagramas ASCII)
  content.querySelectorAll('pre code[class*="language-"]').forEach(el => {
    try { hljs.highlightElement(el); } catch(e){}
  });

  // Botón copiar en cada bloque de código
  content.querySelectorAll("pre").forEach(pre => {
    const btn = document.createElement("button");
    btn.className = "copy-btn"; btn.textContent = "Copiar";
    btn.addEventListener("click", () => {
      const code = pre.querySelector("code");
      navigator.clipboard.writeText(code ? code.textContent : pre.textContent).then(() => {
        btn.textContent = "¡Copiado!"; btn.classList.add("done");
        setTimeout(() => { btn.textContent = "Copiar"; btn.classList.remove("done"); }, 1400);
      });
    });
    pre.appendChild(btn);
  });

  // ==== Sidebar TOC a partir de los h2 ====
  const toc = document.getElementById("toc");
  const headings = [...content.querySelectorAll("h2")];
  const links = [];
  headings.forEach(h => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = "#" + h.id;
    a.textContent = h.textContent.replace(/#$/, "").trim();
    a.dataset.text = a.textContent.toLowerCase();
    li.appendChild(a); toc.appendChild(li);
    links.push(a);
  });

  // Filtro de secciones
  const filter = document.getElementById("filter");
  filter.addEventListener("input", () => {
    const q = filter.value.toLowerCase().trim();
    links.forEach(a => a.classList.toggle("hidden", q && !a.dataset.text.includes(q)));
  });

  // Sección activa según scroll
  const byId = {};
  links.forEach(a => byId[a.getAttribute("href").slice(1)] = a);
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if(e.isIntersecting){
        links.forEach(a => a.classList.remove("active"));
        const a = byId[e.target.id];
        if(a){ a.classList.add("active");
          a.scrollIntoView({block:"nearest"}); }
      }
    });
  }, { rootMargin:"-70px 0px -75% 0px", threshold:0 });
  headings.forEach(h => obs.observe(h));

  // ==== Tema claro/oscuro ====
  const root = document.documentElement;
  const themeBtn = document.getElementById("themeBtn");
  const hLight = document.getElementById("hljs-light");
  const hDark = document.getElementById("hljs-dark");
  function applyTheme(t){
    root.setAttribute("data-theme", t);
    themeBtn.textContent = t === "dark" ? "☀️" : "🌙";
    hLight.disabled = t === "dark";
    hDark.disabled = t !== "dark";
  }
  const saved = localStorage.getItem("theme");
  applyTheme(saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  themeBtn.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem("theme", next); applyTheme(next);
  });

  // ==== Menú móvil ====
  const sidebar = document.getElementById("sidebar");
  const scrim = document.getElementById("scrim");
  const menuBtn = document.getElementById("menuBtn");
  function closeMenu(){ sidebar.classList.remove("open"); scrim.classList.remove("open"); }
  menuBtn.addEventListener("click", () => { sidebar.classList.toggle("open"); scrim.classList.toggle("open"); });
  scrim.addEventListener("click", closeMenu);
  toc.addEventListener("click", e => { if(e.target.tagName === "A") closeMenu(); });

  // ==== Volver arriba ====
  const backTop = document.getElementById("backTop");
  backTop.addEventListener("click", () => window.scrollTo({top:0, behavior:"smooth"}));
  addEventListener("scroll", () => backTop.classList.toggle("show", scrollY > 600));

  // ==== Enlace a GitHub ====
  if(REPO_URL){ const g = document.getElementById("ghLink"); g.href = REPO_URL; g.hidden = false; }

  // ==== Pie ====
  const footer = document.createElement("footer");
  footer.innerHTML = 'Generado desde <code>README-copilot.md</code> · Basado en la ' +
    '<a href="https://code.visualstudio.com/docs/copilot/customization/overview">documentación oficial de VS Code</a>.';
  content.appendChild(footer);
  </script>
</body>
</html>
"""

html = TEMPLATE.replace("__MARKDOWN_B64__", b64)
OUT.write_text(html, encoding="utf-8")
print(f"✅ index.html generado ({len(html):,} bytes) desde {SRC.name}")
