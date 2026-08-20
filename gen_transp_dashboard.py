#!/usr/bin/env python3
"""Genera dashboard web de transparencia_osint desde la DB."""
import sqlite3
import html
import datetime
from collections import Counter, defaultdict
from pathlib import Path

DB = "/home/deploy/transparencia-osint/data/transparencia.db"
OUT = Path("/home/deploy/transparencia-osint/dashboard/index.html")
SITE = "https://transparencia.viajeinteligencia.com"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

total = conn.execute("SELECT COUNT(*) c, COUNT(DISTINCT poder) p, COUNT(DISTINCT cif) f, "
                     "COUNT(importe) ci FROM contratos").fetchone()
n_imp = total["ci"]
with_imp = conn.execute("SELECT COUNT(*) FROM contratos WHERE importe IS NOT NULL").fetchone()[0]
sum_imp = conn.execute("SELECT COALESCE(SUM(importe),0) FROM contratos").fetchone()[0]

# Concentración: empresa con >=5 contratos menores a la misma entidad
conc = conn.execute("""
    SELECT cif, razon_social, poder, COUNT(*) n, COALESCE(SUM(importe),0) suma
    FROM contratos WHERE procedimiento LIKE '%menor%'
    GROUP BY cif, poder HAVING n >= 5 ORDER BY n DESC""").fetchall()

# Top entidades por nº contratos
top_ent = conn.execute("SELECT poder, COUNT(*) n FROM contratos GROUP BY poder ORDER BY n DESC LIMIT 12").fetchall()

# Top empresas por contratos menores
top_emp = conn.execute("""
    SELECT razon_social, COUNT(*) n FROM contratos WHERE procedimiento LIKE '%menor%'
    GROUP BY razon_social ORDER BY n DESC LIMIT 12""").fetchall()

hoy = datetime.date.today().isoformat()

def bars(rows, key_n):
    mx = max(r[key_n] for r in rows) if rows else 1
    out = ""
    for r in rows:
        w = int(r[key_n] / mx * 100)
        out += f'<div style="display:flex;align-items:center;gap:10px;margin:4px 0;">'
        out += f'<span style="min-width:200px;font-size:0.85em;">{html.escape(r[0])[:40]}</span>'
        out += f'<div style="flex:1;background:#0e1322;border-radius:4px;"><div style="height:12px;background:#f87171;width:{w}%;border-radius:4px;"></div></div>'
        out += f'<b style="min-width:40px;text-align:right;">{r[1]}</b></div>'
    return out

conc_html = ""
if conc:
    for r in conc:
        conc_html += f'<tr><td>{html.escape(r["razon_social"])[:40]}</td><td>{html.escape(r["poder"])[:35]}</td>'
        conc_html += f'<td style="color:#f87171;font-weight:700;">{r["n"]}</td>'
        conc_html += f'<td>{r["suma"]:,.0f} €</td></tr>'
else:
    conc_html = '<tr><td colspan="4">Ninguna empresa con ≥5 contratos menores a una misma entidad en los datos ingeridos.</td></tr>'

ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "transparencia_osint",
      "url": SITE, "inLanguage": "es",
      "description": "Detección de anomalías en contratación pública: concentración de contratos menores, troceado y adjudicaciones irregulares. Datos oficiales."}

html_out = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>transparencia_osint · Anomalías en contratación pública | Viaje Inteligencia</title>
<meta name="description" content="Detección de irregularidades en contratos públicos: empresas con muchos contratos menores a una misma entidad, posibles troceados y concentración. Datos oficiales abiertos.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{SITE}/">
<meta property="og:title" content="transparencia_osint · Anomalías en contratación pública">
<meta property="og:locale" content="es_ES">
<script type="application/ld+json">{html.escape(str(ld))}</script>
<style>
body {{ font-family:-apple-system,'Inter',sans-serif;background:#0b0f17;color:#e7ebf3;max-width:960px;margin:0 auto;padding:24px;line-height:1.6;}}
h1 {{ font-size:1.5em;}} .sub {{ color:#8993a8;}} a {{ color:#67e8f9;}}
.kpis {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:16px 0;}}
.kpi {{ background:#0e1322;border:1px solid #232b3d;border-radius:10px;padding:12px;}}
.kpi .n {{ font-size:1.4em;font-weight:700;color:#ffb454;}} .kpi .l {{ font-size:0.72em;color:#8993a8;}}
table {{ width:100%;border-collapse:collapse;font-size:0.85em;}}
th,td {{ text-align:left;padding:6px 8px;border-bottom:1px solid #1a2233;}}
th {{ color:#8993a8;}}
.fuente {{ font-size:0.75em;color:#576076;margin-top:20px;border-top:1px solid #232b3d;padding-top:10px;}}
</style>
</head>
<body>
<h1>🔎 transparencia_osint · Anomalías en contratación pública</h1>
<p class="sub">Detección de irregularidades en contratos públicos con datos oficiales abiertos (Euskadi / datos.gob.es). Actualizado {hoy}.</p>

<div class="kpis">
  <div class="kpi"><div class="n">{total['c']}</div><div class="l">contratos</div></div>
  <div class="kpi"><div class="n">{total['p']}</div><div class="l">entidades</div></div>
  <div class="kpi"><div class="n">{total['f']}</div><div class="l">empresas distintas</div></div>
  <div class="kpi"><div class="n">{sum_imp:,.0f} €</div><div class="l">importe total ({with_imp} con importe)</div></div>
</div>

<h2>🚨 Concentración de contratos menores (≥5 a una misma entidad)</h2>
<table>
<tr><th>Empresa</th><th>Entidad</th><th>Nº menores</th><th>Suma</th></tr>
{conc_html}
</table>

<h2>🏢 Entidades con más contratos</h2>
{bars(top_ent, 1)}

<h2>🏭 Empresas con más contratos menores</h2>
{bars(top_emp, 1)}

<p class="fuente">Fuente: datos abiertos de contratación de Euskadi (datos.gob.es). Reglas: concentración (misma empresa + misma entidad + contratos menores) y troceado (importes <15k c/u sumando >15k en 90 días). Proyecto experimental de transparencia — los datos requieren verificación. · <a href="https://www.viajeinteligencia.com/">Viaje Inteligencia</a> · <a href="mailto:nearme@viajeinteligencia.com">contacto</a></p>
</body></html>"""
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(html_out, encoding="utf-8")
print(f"OK: dashboard generado ({OUT}) · {total['c']} contratos · {len(conc)} anomalías de concentración")
