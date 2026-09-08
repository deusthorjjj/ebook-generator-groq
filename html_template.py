"""
html_template.py
Gera o HTML de luxo para o e-book com design profissional dark gold.
"""
import json
from typing import Dict, Any, List


def montar_html_ebook(
    tema: Dict[str, Any],
    capitulos: List[Dict[str, Any]],
    imagem_capa: str,
    imagens_capitulos: List[str],
    graficos_data: List[Dict],
    prompts_versao: str = "1.0",
) -> str:
    """
    Monta o HTML completo do e-book com design dark gold luxuoso.
    """

    titulo = tema.get("tema_escolhido", "E-Book Profissional")
    subtitulo = tema.get("subtitulo", "")
    preco = tema.get("preco_sugerido", "")
    publico = tema.get("publico_alvo", "")
    nicho = tema.get("nicho", "")

    # Gera índice
    itens_indice = ""
    for i, cap in enumerate(capitulos, 1):
        itens_indice += f"""
        <li class="toc-item">
          <a href="#capitulo-{i}" class="toc-link">
            <span class="toc-num">0{i}</span>
            <span class="toc-titulo">{cap.get('titulo', '')}</span>
            <span class="toc-dot"></span>
          </a>
        </li>"""

    # Gera capítulos
    secoes_capitulos = ""
    for i, cap in enumerate(capitulos, 1):
        img_uri = imagens_capitulos[i - 1] if i - 1 < len(imagens_capitulos) else ""
        img_tag = f'<img src="{img_uri}" class="cap-img" alt="{cap.get("titulo","")}" loading="lazy"/>' if img_uri else ""

        grafico_html = ""
        if i - 1 < len(graficos_data) and graficos_data[i - 1]:
            gd = graficos_data[i - 1]
            chart_id = f"chart{i}"
            grafico_html = f"""
        <div class="chart-container">
          <canvas id="{chart_id}"></canvas>
        </div>
        <script>
        (function(){{
          var ctx = document.getElementById('{chart_id}');
          if(!ctx) return;
          new Chart(ctx.getContext('2d'), {{
            type: '{gd.get("tipo","bar")}',
            data: {json.dumps(gd.get("data",{}))},
            options: {{
              responsive: true,
              plugins: {{
                legend: {{ labels: {{ color: '#d4af37', font: {{ size: 13 }} }} }},
                title: {{ display: true, text: '{gd.get("titulo","")}', color: '#d4af37', font: {{ size: 16, weight: 'bold' }} }}
              }},
              scales: {{
                x: {{ ticks: {{ color: '#cccccc' }}, grid: {{ color: 'rgba(212,175,55,0.15)' }} }},
                y: {{ ticks: {{ color: '#cccccc' }}, grid: {{ color: 'rgba(212,175,55,0.15)' }} }}
              }}
            }}
          }});
        }})();
        </script>"""

        insights = cap.get("insights", [])
        insights_html = ""
        if insights:
            itens = "".join(f"<li>{ins}</li>" for ins in insights)
            insights_html = f'<ul class="insight-list">{itens}</ul>'

        checklist = cap.get("checklist", [])
        checklist_html = ""
        if checklist:
            itens_ck = "".join(
                f'<li><span class="check-icon">&#10003;</span> {item}</li>'
                for item in checklist
            )
            checklist_html = f'<div class="checklist-box"><h4>Checklist de Ação</h4><ul>{itens_ck}</ul></div>'

        conteudo = cap.get("conteudo", "").replace("\n", "<br/>")

        secoes_capitulos += f"""
    <section class="capitulo" id="capitulo-{i}">
      <div class="cap-header">
        <span class="cap-numero">0{i}</span>
        <h2 class="cap-titulo">{cap.get('titulo', '')}</h2>
        <p class="cap-resumo">{cap.get('resumo', '')}</p>
      </div>
      {img_tag}
      <div class="cap-conteudo">
        {conteudo}
      </div>
      {insights_html}
      {grafico_html}
      {checklist_html}
    </section>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{titulo}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap"/>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --gold: #d4af37;
      --bg: #0a0a0a;
      --surface: #111111;
      --text: #e8e8e8;
      --text-muted: #888888;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; line-height: 1.8; }}

    #progress-bar {{
      position: fixed; top: 0; left: 0; height: 3px;
      background: linear-gradient(90deg, var(--gold), #f0d060);
      width: 0%; z-index: 9999; transition: width 0.1s;
    }}

    .cover {{
      min-height: 100vh; display: flex; flex-direction: column;
      justify-content: center; align-items: center; text-align: center;
      position: relative; overflow: hidden; padding: 4rem 2rem;
      background: linear-gradient(135deg, #0a0a0a 0%, #1a0a00 50%, #0a0a0a 100%);
    }}
    .cover-img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.2; filter: saturate(0.3); }}
    .cover-overlay {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(10,10,10,0.4) 0%, rgba(10,10,10,0.85) 100%); }}
    .cover-content {{ position: relative; z-index: 2; max-width: 900px; }}
    .cover-badge {{ display: inline-block; border: 1px solid var(--gold); color: var(--gold); padding: 0.4rem 1.5rem; letter-spacing: 4px; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 2.5rem; font-weight: 600; }}
    .cover h1 {{ font-family: 'Playfair Display', serif; font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 900; line-height: 1.15; color: #fff; margin-bottom: 1.5rem; text-shadow: 0 4px 30px rgba(0,0,0,0.8); }}
    .cover h1 .gold {{ color: var(--gold); }}
    .cover .subtitulo {{ font-size: clamp(1rem, 2vw, 1.3rem); color: #cccccc; font-weight: 300; max-width: 600px; margin: 0 auto 3rem; letter-spacing: 0.5px; }}
    .cover-divider {{ width: 80px; height: 2px; background: var(--gold); margin: 0 auto 2rem; }}
    .cover-meta {{ display: flex; gap: 2rem; justify-content: center; flex-wrap: wrap; }}
    .cover-meta span {{ font-size: 0.85rem; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; font-weight: 500; }}
    .cover-meta strong {{ color: var(--gold); }}

    nav.sidenav {{
      position: fixed; left: 0; top: 0; bottom: 0; width: 260px;
      background: var(--surface); border-right: 1px solid #222;
      padding: 2rem 1.5rem; overflow-y: auto; z-index: 100;
      transform: translateX(-100%); transition: transform 0.3s ease;
    }}
    nav.sidenav.open {{ transform: translateX(0); }}
    .nav-toggle {{ position: fixed; top: 1.5rem; left: 1.5rem; z-index: 200; background: var(--gold); border: none; color: #000; width: 44px; height: 44px; cursor: pointer; font-size: 1.1rem; border-radius: 4px; font-weight: bold; }}
    .nav-logo {{ color: var(--gold); font-family: 'Playfair Display', serif; font-size: 1rem; margin-bottom: 2rem; font-weight: 700; }}
    .toc-list {{ list-style: none; }}
    .toc-item {{ margin-bottom: 0.75rem; }}
    .toc-link {{ display: flex; align-items: center; gap: 0.75rem; color: var(--text-muted); text-decoration: none; font-size: 0.85rem; transition: color 0.2s; padding: 0.4rem 0; }}
    .toc-link:hover {{ color: var(--gold); }}
    .toc-num {{ color: var(--gold); font-weight: 700; font-size: 0.75rem; min-width: 24px; }}

    main {{ padding-left: 0; transition: padding-left 0.3s; }}
    @media (min-width: 900px) {{
      nav.sidenav {{ transform: translateX(0) !important; }}
      main {{ padding-left: 260px; }}
      .nav-toggle {{ display: none; }}
    }}

    .capitulo {{ max-width: 860px; margin: 0 auto; padding: 5rem 2rem 4rem; border-bottom: 1px solid #1e1e1e; }}
    .cap-header {{ margin-bottom: 2.5rem; }}
    .cap-numero {{ font-family: 'Playfair Display', serif; font-size: 4rem; color: var(--surface); font-weight: 900; line-height: 1; display: block; margin-bottom: -1rem; -webkit-text-stroke: 1px var(--gold); }}
    .cap-titulo {{ font-family: 'Playfair Display', serif; font-size: clamp(1.6rem, 3vw, 2.4rem); font-weight: 700; color: #fff; margin-bottom: 1rem; line-height: 1.3; }}
    .cap-resumo {{ color: var(--text-muted); font-size: 1rem; font-style: italic; }}
    .cap-img {{ width: 100%; max-height: 420px; object-fit: cover; margin: 2rem 0; border-left: 4px solid var(--gold); filter: brightness(0.85) saturate(0.8); }}
    .cap-conteudo {{ font-size: 1.05rem; color: #d0d0d0; margin-bottom: 2rem; }}
    .cap-conteudo p {{ margin-bottom: 1.2rem; }}

    .insight-list {{ list-style: none; background: var(--surface); border-left: 3px solid var(--gold); padding: 1.5rem 2rem; margin: 2rem 0; border-radius: 0 8px 8px 0; }}
    .insight-list li {{ padding: 0.5rem 0; color: #e0e0e0; }}
    .insight-list li::before {{ content: "→ "; color: var(--gold); font-weight: bold; }}

    .checklist-box {{ background: var(--surface); border: 1px solid #2a2a2a; padding: 1.5rem 2rem; margin: 2rem 0; border-radius: 8px; }}
    .checklist-box h4 {{ color: var(--gold); margin-bottom: 1rem; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; }}
    .checklist-box ul {{ list-style: none; }}
    .checklist-box li {{ padding: 0.4rem 0; color: #c0c0c0; font-size: 0.95rem; }}
    .check-icon {{ color: var(--gold); font-weight: bold; margin-right: 0.5rem; }}

    .chart-container {{ background: var(--surface); padding: 2rem; margin: 2rem 0; border-radius: 8px; border: 1px solid #1e1e1e; max-height: 400px; }}

    footer {{ text-align: center; padding: 4rem 2rem; color: var(--text-muted); font-size: 0.85rem; background: var(--surface); border-top: 1px solid #1e1e1e; }}
    footer .gold-text {{ color: var(--gold); font-family: 'Playfair Display', serif; font-size: 1.1rem; }}

    @page {{ size: A4; margin: 20mm; }}
    @media print {{
      #progress-bar, .nav-toggle, nav.sidenav {{ display: none !important; }}
      main {{ padding-left: 0 !important; }}
      .capitulo {{ page-break-before: always; padding: 2rem 1rem; border: none; }}
      .cover {{ min-height: auto; page-break-after: always; }}
      body {{ background: #fff !important; color: #111 !important; }}
      .cap-titulo, .cover h1 {{ color: #111 !important; }}
      .cap-conteudo {{ color: #333 !important; }}
    }}
  </style>
</head>
<body>
<div id="progress-bar"></div>
<button class="nav-toggle" onclick="toggleNav()" aria-label="Menu">&#9776;</button>

<nav class="sidenav" id="sidenav">
  <div class="nav-logo">{titulo[:30]}</div>
  <ul class="toc-list">
    {itens_indice}
  </ul>
</nav>

<main>
  <section class="cover">
    <img src="{imagem_capa}" class="cover-img" alt="Capa"/>
    <div class="cover-overlay"></div>
    <div class="cover-content">
      <div class="cover-badge">{nicho}</div>
      <h1><span class="gold">{titulo}</span></h1>
      <div class="cover-divider"></div>
      <p class="subtitulo">{subtitulo}</p>
      <div class="cover-meta">
        <span><strong>{preco}</strong></span>
        <span>{publico}</span>
        <span>IA v{prompts_versao}</span>
      </div>
    </div>
  </section>

  {secoes_capitulos}

  <footer>
    <p class="gold-text">{titulo}</p>
    <p style="margin-top:1rem;">Gerado por IA • {nicho}</p>
    <p style="margin-top:0.5rem;font-size:0.75rem;opacity:0.5;">v{prompts_versao} • Todos os direitos reservados</p>
  </footer>
</main>

<script>
  window.addEventListener('scroll', function() {{
    var scrollTop = document.documentElement.scrollTop;
    var scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
    document.getElementById('progress-bar').style.width = progress + '%';
  }});

  function toggleNav() {{
    document.getElementById('sidenav').classList.toggle('open');
  }}

  document.querySelectorAll('.toc-link').forEach(function(link) {{
    link.addEventListener('click', function() {{
      if(window.innerWidth < 900) {{
        document.getElementById('sidenav').classList.remove('open');
      }}
    }});
  }});
</script>
</body>
</html>"""
